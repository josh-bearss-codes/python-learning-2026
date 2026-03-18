# GitHub Analyzer — Technical Specification

## Overview
CLI tool that analyzes a GitHub user's public repositories. 
Fetches profile, repos, languages, and commits. 
Displays formatted terminal output with stats and charts.
Caches API responses (30 min TTL) to avoid redundant calls.

## Architecture
- Data Layer: GitHubAPIClient (HTTP, caching, pagination)
- Data Models: UserProfile, RepoSummary (dataclasses)
- Business Logic: GitHubAnalyzer (aggregation, statistics)
- Presentation: GitHubDisplay (formatted terminal output)

## Data Models

### UserProfile (dataclass)
Fields: login, name, bio, location, company, public_repos, 
followers, following, created_at (str), updated_at (str)

### RepoSummary (dataclass)
Fields: name, full_name, description (str or None), 
language (str or None), stargazers_count (int), forks_count (int),
size (int, KB), updated_at (str), html_url (str), fork (bool)

## GitHubAPIClient

__init__(token: str or None, cache_dir: Path)
- Base URL: https://api.github.com
- Headers: Authorization: token {token} (if token provided)
- Headers: Accept: application/vnd.github+json

fetch_user(user: str) -> UserProfile
- GET /users/{user}
- No pagination
- 404 → raise ValueError("User not found: {user}")

fetch_repos(user: str) -> list[RepoSummary]
- GET /users/{user}/repos
- Pagination: per_page=100, loop until empty response
- Parse each repo dict into RepoSummary dataclass
- Skip forks (where fork=True) unless user requests them

fetch_languages(owner: str, repo: str) -> dict
- GET /repos/{owner}/{repo}/languages
- No pagination — returns {language: bytes} dict
- Empty repo → return empty dict

fetch_commits(owner: str, repo: str, since: str = None) -> list[dict]
- GET /repos/{owner}/{repo}/commits
- Pagination: per_page=100, loop until empty response
- Optional since param (ISO date) to limit to recent commits
- 409 (empty repo) → log warning, return empty list
- Return list of commit dicts with: sha, commit.author.date, commit.message

### Pagination helper
_get_all_pages(url: str, params: dict) -> list
- Set per_page=100, start page=1
- Loop: fetch page, if empty list break, else extend results, page += 1
- Log: "Fetched {page_count} pages ({len(results)} items)"

### Caching
- Cache dir: ~/.github_analyzer_cache/
- Cache key: MD5 hash of full URL + params
- Store as JSON files
- Expiry: check file modification time, reject if > 1800 seconds old
- _get_cache(key) -> dict or None
- _set_cache(key, data) -> None

### Rate Limiting
- After each request, read X-RateLimit-Remaining header
- If < 100: log warning
- If < 20: stop fetching per-repo detail, use only summary data

## GitHubAnalyzer

analyze(profile: UserProfile, repos: list[RepoSummary], 
        repo_languages: dict, repo_commits: dict) -> dict

Returns a summary dict containing:
- total_repos, total_stars, total_forks
- language_breakdown: {language: total_bytes} aggregated across all repos
- most_active_repos: top 5 by recent commit count
- least_active_repos: bottom 5 by recent commit count  
- weekly_commit_counts: {(year, week): count} for charting
- average_stars, average_forks

## GitHubDisplay

show_profile(profile: UserProfile, summary: dict) -> None
show_repos(repos: list[RepoSummary]) -> None
show_language_chart(language_breakdown: dict) -> None
show_commit_activity(weekly_counts: dict) -> None

### Display Format
[Include your ASCII mockup here — that part was good, keep it]

## Error Handling
- 404 on user → "User not found: {user}"
- 409 on commits → skip repo, log warning, continue
- 403 rate limited → show "Rate limited — resets at {time}"
- 401 bad token → "Invalid token — check GITHUB_TOKEN"
- ConnectionError → show cached data if available, else "Network error"
- JSONDecodeError → "Unexpected API response"

## Dependencies
requests (pip install requests)

## Authentication
GITHUB_TOKEN environment variable (optional)
Without token: 60 req/hr. With token: 5000 req/hr.