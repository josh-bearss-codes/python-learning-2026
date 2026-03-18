import os
import json
import hashlib
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN_ENV = "GITHUB_TOKEN"
CACHE_DIR = Path.home() / ".github_analyzer_cache"
CACHE_TTL = 1800  # 30 minutes in seconds
PER_PAGE = 100


# --- Data Models ---

@dataclass
class UserProfile:
    login: str
    name: str
    bio: str
    location: str
    company: str
    public_repos: int
    followers: int
    following: int
    created_at: str
    updated_at: str


@dataclass
class RepoSummary:
    name: str
    full_name: str
    description: Optional[str]
    language: Optional[str]
    stargazers_count: int
    forks_count: int
    size: int
    updated_at: str
    html_url: str
    fork: bool


# --- GitHubAPIClient ---

class GitHubAPIClient:
    """
    Handles HTTP requests to the GitHub API with caching and pagination.
    """

    def __init__(self, token: Optional[str] = None, cache_dir: Path = CACHE_DIR):
        self.base_url = GITHUB_API_BASE
        self.token = token or None
        self.session = requests.Session()
        
        # Configure headers
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitHubAnalyzer"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        self.session.headers.update(headers)
        
        # Ensure cache directory exists
        cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_rate_limit_remaining(self) -> int:
        """Reads X-RateLimit-Remaining header from the last response."""
        try:
            response = self._request('get',GITHUB_API_BASE + "/rate_limit")
            return int(response['rate']['remaining'])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch rate limit: {e}")
        except ValueError:
            return 0

    def _handle_rate_limit(self) -> bool:
        """
        Checks rate limit.
        Returns True if we can proceed with detailed fetching, False if we should stop.
        """
        remaining = self._get_rate_limit_remaining()
        if remaining < 20:
            logger.warning(f"Rate limit low: {remaining} requests remaining. Switching to summary mode.")
            return False
        return True

    def _get_cache_key(self, url: str, params: Dict) -> str:
        """Generates an MD5 hash of the full URL and params for cache lookup."""
        content = f"{url}{json.dumps(params, sort_keys=True)}".encode('utf-8')
        return hashlib.md5(content).hexdigest()

    def _get_cache(self, key: str) -> Optional[Dict]:
        """Retrieves data from cache if it exists and is not expired."""
        cache_file = CACHE_DIR / f"{key}.json"
        if not cache_file.exists():
            return None
        
        # Check expiration
        file_time = cache_file.stat().st_mtime
        current_time = time.time()
        if current_time - file_time > CACHE_TTL:
            logger.debug(f"Cache expired for key: {key}")
            cache_file.unlink()
            return None
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _set_cache(self, key: str, data: Dict) -> None:
        """Stores data in cache."""
        cache_file = CACHE_DIR / f"{key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except IOError:
            logger.warning("Failed to write to cache directory.")

    def _request(self, method: str, url: str, params: Optional[Dict] = None) -> Dict:
        """Generic request handler with caching and error handling."""
        # Generate cache key
        cache_key = self._get_cache_key(url, params or {})
        
        # Try cache first
        cached_data = self._get_cache(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for {url}")
            return cached_data

        # Perform request
        response = self.session.request(method, url, params=params)
        
        # Handle 409 (Empty repo) gracefully for commits
        if response.status_code == 409:
            logger.warning(f"Empty repo or error fetching: {url}")
            return {}

        # Handle 404
        if response.status_code == 404:
            raise ValueError(f"Resource not found: {url}")

        # Handle 403 Rate Limit
        if response.status_code == 403:
            reset_time = response.headers.get('X-RateLimit-Reset')
            reset_dt = datetime.fromtimestamp(int(reset_time)) if reset_time else datetime.now() + timedelta(hours=1)
            raise Exception(f"Rate limited — resets at {reset_dt}")

        # Handle 401 Bad Token
        if response.status_code == 401:
            raise ValueError("Invalid token — check GITHUB_TOKEN")

        response.raise_for_status()
        
        # Store in cache
        self._set_cache(cache_key, response.json())
        
        return response.json()

    def _get_all_pages(self, url: str, params: Dict) -> Tuple[List, int]:
        """
        Pagination helper.
        Returns: (list of items, page_count)
        """
        results = []
        page = 1
        page_count = 0
        
        while True:
            params['page'] = page
            try:
                data = self._request('GET', url, params)
                if not data:  # Empty list means no more pages
                    break
                results.extend(data)
                page_count += 1
                logger.debug(f"Fetched page {page_count} ({len(data)} items)")
                page += 1
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
                
        return results, page_count

    def fetch_user(self, user: str) -> UserProfile:
        """Fetches user profile.
            login: str
            name: str
            bio: str
            location: str
            company: str
            public_repos: int
            followers: int
            following: int
            created_at: str
            updated_at: str
        """
        url = f"{self.base_url}/users/{user}"
        data = self._request('GET', url)
        return UserProfile( 
            login=data.get("login", "Unknown"),
            name=data.get("name", "Unknown"),
            bio=data.get("bio", ""),
            location=data.get("location", ""),
            company=data.get("company", ""),
            public_repos=data.get("public_repos",""),
            followers=data.get("followers",""),
            following=data.get("following",""),
            created_at=data.get("created_at",""),
            updated_at=data.get("updated_at","")
        )

    def fetch_repos(self, user: str, fetch_forks: bool = False) -> List[RepoSummary]:
        """
        Fetches repositories for a user.
        Skips forks by default unless fetch_forks is True.
        """
        url = f"{self.base_url}/users/{user}/repos"
        params = {'per_page': PER_PAGE}
        
        if not fetch_forks:
            params['per_page'] = PER_PAGE
            params['sort'] = 'updated'
            # Note: GitHub API doesn't natively support 'forks=false' in the query param easily
            # We filter in Python below to adhere to spec requirements
            params['visibility'] = 'public'

        all_data, page_count = self._get_all_pages(url, params)
        
        repos = []
        for item in all_data:
            # Skip forks if requested
            """
                name: str
                full_name: str
                description: Optional[str]
                language: Optional[str]
                stargazers_count: int
                forks_count: int
                size: int
                updated_at: str
                html_url: str
                fork: bool
            """
            if not fetch_forks and item.get('fork', False):
                continue

            repos.append(RepoSummary(
                name=item.get('name' or ''),
                full_name=item.get('full_name' or ''),
                description=item.get('description' or ''),
                language=item.get('language' or ''),
                stargazers_count=int(item.get('stargazers') or 0),
                forks_count=int(item.get('forks_count') or 0),
                size=int(item.get('size') or 0),
                updated_at=item.get('updated_at' or ''),
                html_url=item.get('html_url' or ''),
                fork=item.get('fork' or '')
            ))
            
        logger.info(f"Fetched {len(repos)} repos from {page_count} pages.")
        return repos

    def fetch_languages(self, owner: str, repo: str) -> Dict:
        """Fetches language breakdown for a specific repo."""
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        return self._request('GET', url)

    def fetch_commits(self, owner: str, repo: str, since: Optional[str] = None) -> List[Dict]:
        """
        Fetches commits for a repo.
        Returns list of dicts with sha, commit.author.date, commit.message.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {'per_page': PER_PAGE}
        if since:
            params['since'] = since

        all_data, page_count = self._get_all_pages(url, params)
        
        commits = []
        for item in all_data:
            commits.append({
                'sha': item['sha'],
                'date': item['commit']['author']['date'],
                'message': item['commit']['message'].strip()
            })
            
        logger.info(f"Fetched {len(commits)} commits from {page_count} pages.")
        return commits


# --- GitHubAnalyzer ---

class GitHubAnalyzer:
    """
    Business logic for aggregating and calculating statistics.
    """

    @staticmethod
    def analyze(profile: UserProfile, repos: List[RepoSummary], 
                repo_languages: Dict, repo_commits: Dict) -> Dict:
        """
        Analyzes user data and returns a summary dictionary.
        """
        # Basic stats
        total_repos = len(repos)
        total_stars = sum(r.stargazers_count for r in repos)
        total_forks = sum(r.forks_count for r in repos)

        # Language breakdown
        language_breakdown = {}
        for repo_name, lang_data in repo_languages.items():
            for lang, bytes_count in lang_data.items():
                if lang not in language_breakdown:
                    language_breakdown[lang] = 0
                language_breakdown[lang] += bytes_count
        # Commit Activity (Top 5 / Bottom 5)
        # Calculate commit count per repo
        repo_commit_counts = {repo: len(commits) for repo, commits in repo_commits.items()}
        
        # Sort by count (descending)
        sorted_repos = sorted(repos, key=lambda r: repo_commit_counts.get(r.full_name, 0), reverse=True)
        
        most_active = sorted_repos[:5]
        least_active = sorted_repos[-5:] if len(sorted_repos) > 5 else []

        # Weekly commit counts for charting
        weekly_counts = {}
        for repo_name, commits in repo_commits.items():
            for commit in commits:
                # Parse date to get ISO week
                try:
                    date = datetime.fromisoformat(str(commit['date']).replace('Z', '+00:00'))
                    week_key = (date.year, date.isocalendar()[1])
                    weekly_counts[week_key] = weekly_counts.get(week_key, 0) + 1
                except ValueError:
                    continue

        # Averages
        avg_stars = total_stars / total_repos if total_repos > 0 else 0
        avg_forks = total_forks / total_repos if total_repos > 0 else 0

        return {
            'total_repos': total_repos,
            'total_stars': total_stars,
            'total_forks': total_forks,
            'language_breakdown': language_breakdown,
            'most_active_repos': most_active,
            'least_active_repos': least_active,
            'weekly_commit_counts': weekly_counts,
            'average_stars': avg_stars,
            'average_forks': avg_forks
        }


# --- GitHubDisplay ---

class GitHubDisplay:
    """
    Handles formatted terminal output.
    """

    @staticmethod
    def show_profile(profile: UserProfile, summary: Dict) -> None:
        """Displays user profile and basic stats."""
        print("\n" + "="*50)
        print(f"👤 User: {profile.login}")
        if profile.name:
            print(f"   Name: {profile.name}")
        if profile.bio:
            print(f"   Bio:  {profile.bio}")
        if profile.location:
            print(f"   📍 Location: {profile.location}")
        if profile.company:
            print(f"   🏢 Company: {profile.company}")
        
        print("\n📊 Stats:")
        print(f"   Public Repos: {summary['total_repos']}")
        print(f"   Followers:    {profile.followers}")
        print(f"   Following:    {profile.following}")
        print(f"   Stars:        {summary['total_stars']}")
        print(f"   Forks:        {summary['total_forks']}")
        print(f"   Avg Stars/Repo: {summary['average_stars']:.2f}")
        print("=" * 50 + "\n")

    @staticmethod
    def show_repos(repos: List[RepoSummary]) -> None:
        """Displays a list of repositories."""
        print("\n📂 Repositories:")
        print("-" * 80)
        for repo in repos:
            lang = f" [{repo.language}]" if repo.language else ""
            stars = f" ⭐ {repo.stargazers_count}"
            forks = f" 🔀 {repo.forks_count}"
            size = f" 📦 {repo.size}KB"
            print(f"{repo.name:40} {lang:15} {stars:8} {forks:8} {size:8}")
        print("-" * 80 + "\n")

    @staticmethod
    def show_language_chart(language_breakdown: Dict) -> None:
        """Displays a simple text-based bar chart for languages."""
        if not language_breakdown:
            print("No language data available.")
            return

        # Sort by bytes descending
        sorted_langs = sorted(language_breakdown.items(), key=lambda x: x[1], reverse=True)
        total_bytes = sum(language_breakdown.values())
        
        print("\n🎨 Language Breakdown:")
        print("-" * 40)
        for lang, bytes_count in sorted_langs[:10]:  # Top 10
            percentage = (bytes_count / total_bytes) * 100
            bar_len = int((bytes_count / max(language_breakdown.values())) * 40) if language_breakdown else 0
            bar = "█" * bar_len
            print(f"{lang:20} {bar:40} {percentage:.1f}%")
        print("-" * 40 + "\n")

    @staticmethod
    def show_commit_activity(weekly_counts: Dict) -> None:
        """Displays commit activity summary."""
        if not weekly_counts:
            print("No recent commit activity data.")
            return

        print("\n📅 Commit Activity (Last 4 Weeks):")
        print("-" * 30)
        
        # Sort weeks
        sorted_weeks = sorted(weekly_counts.items(), key=lambda x: x[0])
        
        # Format output
        for (year, week), count in sorted_weeks[-12:]:  # Last 12 weeks
            date_str = f"{year}-W{week:02d}"
            bar = "█" * min(count, 30) # Cap bar at 30 chars
            print(f"{date_str} : {bar} ({count})")
        print("-" * 30 + "\n")


# --- Main Entry Point ---

def main():
    import argparse
    # Initialize Argument Parser
    parser = argparse.ArgumentParser(description="GitHub Repository Analyzer")
    
    # Add the flag argument
    # action="store_true": Sets the value to True if --token is used, False otherwise
    parser.add_argument(
        "--token", 
        action="store",
        help="Use GitHub Personal Access Token (flag only)"
    )

    # Parse arguments
    args = parser.parse_args()
    
    # Check if the flag was passed
    if args.token:
        logger.info("Using GitHub Token for higher rate limits.")
        token = os.getenv(GITHUB_TOKEN_ENV)
    else:
        logger.info("No token provided. Using unauthenticated rate limit (60/hr).")
          

    username = input("Enter GitHub username: ").strip()
    if not username:
        print("Username required.")
        return

    try:
        if args.token:
            client = GitHubAPIClient(token=token)
        else:
            client = GitHubAPIClient()
        
        # Fetch Profile
        profile = client.fetch_user(username)
        
        # Fetch Repos
        repos = client.fetch_repos(username)
        
        # Fetch Languages and Commits
        repo_languages = {}
        repo_commits = {}
        
        # Check rate limit before detailed fetching
        can_fetch_details = client._handle_rate_limit()
        
        if can_fetch_details:
            print("Fetching detailed repo data (languages, commits)...")
            for repo in repos:
                # Languages
                try:
                    langs = client.fetch_languages(repo.full_name.split('/')[0], repo.name)
                    repo_languages[repo.full_name] = langs
                except Exception as e:
                    logger.warning(f"Could not fetch languages for {repo.name}: {e}")
                logger.info(f"Fetched languages for {repo.name}")
                # Commits (last 3 months)
                since_date = (datetime.now() - timedelta(days=90)).isoformat()
                try:
                    commits = client.fetch_commits(repo.full_name.split('/')[0], repo.name, since=since_date)
                    repo_commits[repo.full_name] = commits
                except Exception as e:
                    logger.warning(f"Could not fetch commits for {repo.name}: {e}")
                logger.info(f"Fetched commits for {repo.name}")
        else:
            print("Rate limit low. Skipping languages and commits details.")

        # Analyze
        analyzer = GitHubAnalyzer()
        summary = analyzer.analyze(profile, repos, repo_languages, repo_commits)
        
        # Display
        display = GitHubDisplay()
        display.show_profile(profile, summary)
        
        # Only show repos if we have data
        if repos:
            display.show_repos(repos)
            display.show_language_chart(summary['language_breakdown'])
            display.show_commit_activity(summary['weekly_commit_counts'])

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()