import json
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
from enum import Enum
from functools import total_ordering
from collections import Counter, defaultdict
from pathlib import Path

DATA_FILE = Path("reading_list.json")
CHARTS_DIR = Path("reading_charts")


# ──────────────────────────────────────
# ENUMS AND CONSTANTS
# ──────────────────────────────────────

class ReadingStatus(Enum):
    WANT_TO_READ = "want_to_read"
    READING = "reading"
    FINISHED = "finished"
    ABANDONED = "abandoned"

VALID_TRANSITIONS = {
    ReadingStatus.WANT_TO_READ: [ReadingStatus.READING],
    ReadingStatus.READING: [ReadingStatus.FINISHED, ReadingStatus.ABANDONED],
    ReadingStatus.ABANDONED: [ReadingStatus.WANT_TO_READ],
    ReadingStatus.FINISHED: [],
}

STAR_DISPLAY = {1: "★☆☆☆☆", 2: "★★☆☆☆", 3: "★★★☆☆", 4: "★★★★☆", 5: "★★★★★"}


# ──────────────────────────────────────
# DATA MODEL
# ──────────────────────────────────────

@total_ordering
class Book:
    """A book in the reading list with state machine status tracking.
    
    Identity: isbn (two Books with same ISBN are the same book)
    Natural ordering: (author, title) — alphabetical bookshelf
    
    State machine: WANT_TO_READ → READING → FINISHED/ABANDONED
    Rating: only settable on FINISHED books, validated 1–5
    
    This class demonstrates:
      - @total_ordering with __eq__/__lt__ (Day 11)
      - __hash__ consistent with __eq__ (Day 12)
      - Property setter with business rule validation (Day 11)
      - State machine transitions with side effects (today)
      - Computed @property values (Day 10)
      - __repr__ and __str__ (Day 11)
      - to_dict / from_dict serialization (Day 9)
    """

    def __init__(self, isbn: str, title: str, author: str,
                 genre: str = "General", page_count: int = 0,
                 publication_year: int = None, tags: list = None,
                 status: ReadingStatus = ReadingStatus.WANT_TO_READ,
                 rating: int = None, start_date: date = None,
                 finish_date: date = None, notes: str = "",
                 date_added: date = None):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.genre = genre
        self.page_count = page_count
        self.publication_year = publication_year
        self.tags = tags or []
        self.status = status
        self._rating = rating   # Bypass setter for loading from JSON
        self.start_date = start_date
        self.finish_date = finish_date
        self.notes = notes
        self.date_added = date_added or date.today()

    # ── State Machine ─────────────────────

    def transition_to(self, new_status: ReadingStatus) -> bool:
        """Transition reading status with validation and side effects.
        
        Returns True if transition succeeded, False if invalid.
        Side effects:
          → READING: sets start_date to today
          → FINISHED: sets finish_date to today
          → WANT_TO_READ (from ABANDONED): clears start_date
        """
        # Validate against VALID_TRANSITIONS
        # Apply side effects
        # Update status
        # Return True/False
        if new_status not in VALID_TRANSITIONS.get(self.status, []):
            return False #Invalid transition
        
        if new_status == ReadingStatus.READING:
            self.start_date = date.today()
        elif new_status == ReadingStatus.FINISHED:
            self.finish_date = date.today()
        elif new_status == ReadingStatus.WANT_TO_READ and self.status == ReadingStatus.ABANDONED:
            self.start_date = None

        self.status = new_status
        return True

    def start_reading(self) -> bool:
        """Convenience method for WANT_TO_READ → READING."""
        return self.transition_to(ReadingStatus.READING)

    def finish(self) -> bool:
        """Convenience method for READING → FINISHED."""
        return self.transition_to(ReadingStatus.FINISHED)

    def abandon(self) -> bool:
        """Convenience method for READING → ABANDONED."""
        return self.transition_to(ReadingStatus.ABANDONED)

    # ── Validated Properties ──────────────

    @property
    def rating(self) -> int:
        return self._rating

    @rating.setter
    def rating(self, value: int):
        """Only FINISHED books can be rated. Rating must be 1–5."""
        # Validate status is FINISHED
        # Validate value is int, 1 <= value <= 5
        # Set self._rating

        if self.status != ReadingStatus.FINISHED:
            raise ValueError("Cannot rate a book that is not finished.")
        if not isinstance(value, int) or not (1 <= value <= 5):
            raise ValueError("Rating must be an integer between 1 and 5.")
        self._rating = value

    # ── Computed Properties ───────────────

    @property
    def days_to_read(self):
        """Days from start to finish. None if not finished."""
        if self.start_date and self.finish_date:
            return (self.finish_date - self.start_date).days
        return None

    @property
    def reading_pace(self):
        """Pages per day. None if not finished or zero days."""
        if self.days_to_read and self.days_to_read > 0 and self.page_count > 0:
            return round(self.page_count / self.days_to_read, 1)
        return None

    @property
    def is_finished(self) -> bool:
        return self.status == ReadingStatus.FINISHED

    @property
    def star_display(self) -> str:
        """Visual star rating or 'Not rated'."""
        if self._rating:
            return STAR_DISPLAY.get(self._rating, "?")
        return "Not rated"

    # ── Comparison Operators ──────────────

    def __eq__(self, other) -> bool:
        # Identity by ISBN
        if not isinstance(other, Book):
            return NotImplemented
        return self.isbn == other.isbn

    def __hash__(self) -> int:
        # Hash on ISBN
        return hash(self.isbn)

    def __lt__(self, other) -> bool:
        # Natural ordering: (author, title)
        if not isinstance(other, Book):
            return NotImplemented
        return (self.author, self.title) < (other.author, other.title)

    # ── Display ───────────────────────────

    def __repr__(self) -> str:
        # "Book(isbn='978...', title='Dune', author='Frank Herbert')"
        return f"Book(isbn='{self.isbn}', title='{self.title}', author='{self.author}'"
    
    def __str__(self) -> str:
        # Rich display:
        # "Dune by Frank Herbert (1965) — ★★★★★"
        # "  Sci-Fi | 412 pages | Finished in 14 days (29.4 pg/day)"
        # "  Tags: science-fiction, classic, desert"
        rich_display = f"{self.title} by {self.author} ({self.publication_year}) — {'★' * self.rating}\n{self.genre} | {self.page_count} pages | Finished in {self.days_to_read} days ({self.reading_pace:.1f} pg/day\nTags: {', '.join(self.tags)}"
        
        return rich_display

    def brief(self) -> str:
        """One-line display for list views."""
        # "[FINISHED] Dune — Frank Herbert ★★★★★"
        # "[READING]  Project Hail Mary — Andy Weir (started Mar 10)"
        # "[WANT]     Neuromancer — William Gibson"
        if self.is_finished:
            return f"[{self.status}] {self.title} — {self.author} {self.star_display}"
        elif self.start_date is not None:
            return f"[{self.status}] {self.title} — {self.author} (started {self.start_date})"
        else:
            return f"[{self.status}] {self.title} - {self.author}"
            
    # ── Visualization ─────────────────────

    def display_card(self) -> str:
        """Full book card for detail view.
        
        ═══════════════════════════════════════
        DUNE
        by Frank Herbert (1965)
        ═══════════════════════════════════════
        ISBN: 978-0441172719
        Genre: Science Fiction  |  412 pages
        Tags: science-fiction, classic, desert
        Status: Finished ★★★★★
        Started: 2026-02-15  |  Finished: 2026-03-01
        Reading time: 14 days (29.4 pages/day)
        
        Notes: "The spice must flow..."
        ═══════════════════════════════════════
        """
        book_card = f"=" * 50 + "\n"
        book_card += f"{self.title}\n"
        book_card += f"by {self.author} ({self.publication_year})\n"
        book_card = f"=" * 50 + "\n"
        book_card += f"ISBN: {self.isbn}\n"
        book_card += f"Genre: {self.genre}\n"
        book_card += f"Tags: {', '.join(self.tags)}\n"
        book_card += f"Status: {self.status} {self.star_display}\n"
        book_card += f"Started: {self.start_date} | Finished: {self.finish_date}\n"
        book_card += f"Reading time: {self.days_to_read} days ({self.reading_pace:.1f} pages/day)\n\n"
        book_card += f"Notes: {self.notes}\n"
        book_card += f"=" * 50 + "\n"

        return book_card

    # ── Serialization ─────────────────────

    def to_dict(self) -> dict:
        # Serialize everything
        # Dates as ISO strings or None
        # Status as enum value string
        # Rating as int or None

        return {
                "isbn": self.isbn,
                "title": self.title,
                "author": self.author,
                "genre": self.genre,
                "page_count": self.page_count,
                "publication_year": self.publication_year,
                "tags": self.tags,
                "status": self.status.value,
                "rating": self._rating,
                "start_date": self.start_date.isoformat() if self.start_date is not None else None,
                "finish_date": self.finish_date.isoformat() if self.finish_date is not None else None,
                "notes": self.notes,
                "date_added": self.date_added.isoformat() if self.date_added is not None else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        # Deserialize
        # Parse ISO date strings back to date objects
        # Parse status string back to ReadingStatus enum
        # Use _rating bypass for loading (don't trigger setter validation)
        return cls(
            isbn=data["isbn"],
            title=data["title"],
            author=data["author"],
            genre=data["genre"],
            page_count=data["page_count"],
            publication_year=data["publication_year"],
            tags=data["tags"],
            status=ReadingStatus[data["status"]],
            _rating=data["rating"],
            start_date=date.fromisoformat(data["start_date"]) if data["start_date"] is not None else None,
            finish_date=date.fromisoformat(data["finish_date"]) if data["finish_date"] is not None else None,
            notes=data["notes"],
            date_added=date.fromisoformat(data["date_added"]) if data["date_added"] is not None else None
        )


# ──────────────────────────────────────
# EXPORT STRATEGIES (Day 13 Strategy Pattern)
# ──────────────────────────────────────

class CSVExporter:
    """Export reading list to CSV format."""
    
    def export(self, books: list, filepath: Path) -> None:
        """Write books to CSV with DictWriter.
        Headers: ISBN, Title, Author, Genre, Pages, Year, Status, Rating, Tags
        """
        try:
            with open(filepath, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["ISBN", "Title", "Author", "Genre", "Pages", "Year", "Status", "Rating", "Tags"])
                writer.writeheader()
                for book in books:
                    writer.writerow(
                        {
                            'ISBN': book.isbn,
                            'Title': book.title,
                            'Author': book.author,
                            'Genre': book.genre,
                            'Pages': book.page_count,
                            'Year': book.publication_year,
                            'Status': book.status.value,
                            'Rating': book.rating,
                            'Tags': book.tags,
                        }
                    )
        except IOError as e:
            print(f"Error writing to file: {e}")
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            return
        return

class JSONExporter:
    """Export reading list to JSON format (backup/restore)."""
    
    def export(self, books: list, filepath: Path) -> None:
        """Write books to pretty-printed JSON."""
        book_data = [book.to_dict() for book in books]
        try:
            with open(filepath, "w") as f:
                json.dump(book_data, f, indent=4)
        except IOError as e:
            print(f"Error writing to file: {e}")
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            return

class MarkdownExporter:
    """Export reading list to Markdown for blog/README."""
    
    def export(self, books: list, filepath: Path) -> None:
        """Write formatted Markdown with sections by status.
        
        ## Currently Reading
        - **Project Hail Mary** by Andy Weir (started Mar 10)
        
        ## Finished (★★★★★)
        - **Dune** by Frank Herbert — 412 pages, 14 days
        
        ## Want to Read
        - **Neuromancer** by William Gibson
        """
        currently_reading = []
        finished = []
        want_to_read = []
        for book in books:
            if book.status == ReadingStatus.READING:
                currently_reading.append(book)
                continue
            elif book.status == ReadingStatus.FINISHED:
                finished.append(book)
                continue
            elif book.status == ReadingStatus.WANT_TO_READ:
                want_to_read.append(book)
                continue
        
        lines = []
        
        if currently_reading:
            lines.append("## Currently Reading")
            for book in currently_reading:
                lines.append(f"- **{book.title}** by {book.author} (started {book.start_date})")
            lines.append("")
        if finished:
            lines.append("## Finished (★★★★★)")
            for book in finished:
                lines.append(f"- **{book.title}** by {book.author} - {book.pages} pages, {book.days_to_read} days")
            lines.append("")
        if want_to_read:
            lines.append("## Want to Read")
            for book in want_to_read:
                lines.append(f"- **{book.title}** by {book.author}")
        
        with open(filepath, 'w') as f: f.write("\n".join(lines))
            
EXPORTERS = {
    "csv": CSVExporter(),
    "json": JSONExporter(),
    "md": MarkdownExporter(),
}


# ──────────────────────────────────────
# DATA LAYER
# ──────────────────────────────────────

class ReadingListStore:
    def __init__(self, filepath: Path = DATA_FILE):
        self.filepath = filepath

    def load(self) -> list:
        """Load books from JSON. Returns list of Book objects."""
        if not self.filepath.exists():
            return []
        with open(self.filepath, 'r') as f:
            data = json.load(f)
            books = [Book(**book) for book in data]
            return books

    def save(self, books: list) -> None:
        """Save all books to JSON."""
        data = [book.to_dict() for book in books]
        with open(self.filepath, 'w') as f:
            f.write(json.dumps(data, indent=2))
        return None

# ──────────────────────────────────────
# BUSINESS LOGIC — the Library Manager
# ──────────────────────────────────────

class ReadingListManager:
    """Manages the book collection with search, stats, and recommendations.
    
    This is the business logic layer. It handles:
      - CRUD operations on books
      - Search and filtering
      - Statistics and aggregation
      - Recommendations (cross-book analysis)
      - Chart generation
      - Export coordination
    """

    def __init__(self, store: ReadingListStore = None):
        self.store = store or ReadingListStore()
        self.books = self.store.load()

    def _save(self):
        self.store.save(self.books)

    # ── CRUD ──────────────────────────────

    def add_book(self, book: Book) -> bool:
        """Add a book. Reject duplicates by ISBN (__eq__)."""
        if book not in self.books:
            self.books.append(book)
            self._save()
            return True
        return False

    def remove_book(self, isbn: str) -> bool:
        """Remove a book by ISBN."""
        for book in self.books:
            if book.isbn == isbn:
                self.books.remove(book)
                self._save()
                return True
        return False

    def find_by_isbn(self, isbn: str):
        """Find a book by ISBN. Returns Book or None."""
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None

    # ── Status Transitions ────────────────

    def start_reading(self, isbn: str) -> bool:
        """Transition a book to READING status."""
        for book in self.books:
            if book.isbn == isbn:
                book.start_reading()
                self._save()
                return True
        return False

    def finish_book(self, isbn: str, rating: int = None) -> bool:
        """Transition to FINISHED and optionally set rating."""
        for book in self.books:
            if book.isbn == isbn:
                book.finish()
                if rating is not None:
                    book.rate_book(rating)
                self._save()
                return True
        return False

    def abandon_book(self, isbn: str) -> bool:
        """Transition to ABANDONED."""
        for book in self.books:
            if book.isbn == isbn:
                book.abandon()
                self._save()
                return True
        return False

    def rate_book(self, isbn: str, rating: int) -> bool:
        """Set or update rating on a finished book."""
        for book in self.books:
            if book.isbn == isbn and book.is_finished:
                book.rate_book(rating)

    # ── Search & Filter ───────────────────

    def search(self, query: str) -> list:
        """Search by title, author, or tags (case-insensitive, partial match)."""
        # Check title, author, and tags using any()
        return [b for b in self.books if any(q.lower() in b.title.lower() for q in query.split())]

    def filter_by_status(self, status: ReadingStatus) -> list:
        """All books with a given status, sorted naturally (__lt__)."""
        return sorted([b for b in self.books if b.status == status])

    def filter_by_genre(self, genre: str) -> list:
        """Books in a specific genre."""
        return [b for b in self.books if b.genre == genre] 

    def filter_by_tag(self, tag: str) -> list:
        """Books that have a specific tag."""
        return [b for b in self.books if tag in b.tags]

    def filter_by_rating(self, min_rating: int) -> list:
        """Finished books with rating >= min_rating, sorted by rating desc."""
        return sorted(
            [b for b in self.books if b.rating and b.rating >= min_rating],
            key=lambda b: b.rating,
            reverse=True
        )

    # ── Statistics ────────────────────────

    def get_statistics(self) -> dict:
        """Comprehensive reading statistics.
        
        Returns dict with:
          total_books, by_status counts, 
          finished_count, average_rating, average_pace,
          total_pages_read, books_this_month, books_this_year,
          favorite_genre, favorite_author,
          fastest_read, slowest_read
        """
        return {
            "total_books": len(self.books),
            "by_status": Counter([b.status for b in self.books]),
            "finished_count": len([b for b in self.books if b.status == ReadingStatus.FINISHED]),
            "average_rating": sum([b.rating for b in self.books if b.rating]) / len(self.books) and len(self.books) > 0,
            "average_pace": sum([b.days_to_read for b in self.books if b.status == ReadingStatus.FINISHED]) / len([b for b in self.books if b.status == ReadingStatus.FINISHED]),
            "total_pages_read": sum([b.page_count for b in self.books]), 
            "books_this_month": len([b.status == ReadingStatus.FINISHED and b.finish_date.month == datetime.now().month for b in self.books]),
            "books_this_year": len([b.status == ReadingStatus.FINISHED and b.finish_date.year == date.now().year for b in self.books]),
            "favorite_genre": Counter([b.genre for b in self.books]).most_common(1)[0][0] if Counter([b.genre for b in self.books]) else None,
            "favorie_author": Counter([b.author for b in self.books]).most_common(1)[0][0] if Counter([b.author for b in self.books]) else None,
            "fastest_read": min([b.days_to_read for b in self.books if b.status == ReadingStatus.FINISHED]), 
            "slowest_read": max([b.days_to_read for b in self.books if b.status == ReadingStatus.FINISHED])
        }

    def get_monthly_counts(self) -> dict:
        """Books finished per month.
        Returns: {"2026-01": 3, "2026-02": 5, "2026-03": 2}
        Uses finish_date.strftime("%Y-%m") as grouping key.
        """
        monthly_counts = defaultdict(int)
        for book in self.books:
            if book.status == ReadingStatus.FINISHED and book.finish_date:
                key = book.finish_date.strftime("%Y-%m")
                monthly_counts[key] += 1
        return dict(monthly_counts)

    # ── Recommendations ───────────────────

    def get_recommendations(self, limit: int = 5) -> list:
        """Recommend unread books based on taste profile.
        
        Algorithm (rule-based scoring, not ML):
          For each WANT_TO_READ book, calculate score based on
          similarity to books rated 4+ stars:
            +3 per highly-rated book by same author
            +2 per highly-rated book in same genre
            +1 per shared tag with any highly-rated book
        
        Returns top N books sorted by score descending.
        """
        unread = [b for b in self.books if b.status == ReadingStatus.WANT_TO_READ]
        highly_rated = [b for b in self.books if b.rating and b.rating >= 4]

        if not highly_rated or not unread:
            return unread[:limit]  # No data to score — return arbitrary unread

        scored = []
        score = 0
        for candidate in unread:
            score = self._calculate_recommendation_score(candidate, highly_rated)
            scored.append((score, candidate))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [book for score, book in scored[:limit]]

    def _calculate_recommendation_score(self, candidate: Book,
                                         highly_rated: list) -> int:
        """Score a candidate book based on similarity to highly-rated books."""
        score = 0
        for rated in highly_rated:
            # Same author = strong signal
            # Same genre = moderate signal
            # Shared tags = weak signal per tag
            if candidate.author == rated.author:
                score += 10
            if candidate.genre == rated.genre:
                score += 5
            for tag in candidate.tags:
                if tag in rated.tags:
                    score += 1
        return score

    # ── Charts ────────────────────────────

    def generate_charts(self) -> list:
        """Generate all reading statistics charts.
        Returns list of saved filenames.
        """
        CHARTS_DIR.mkdir(exist_ok=True)
        saved = []

        # Chart 1: Books finished per month (bar)
        fig, ax = plt.subplots(figsize=(10, 6))
        self._plot_monthly_books(ax)
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "monthly_books.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved.append("monthly_books.png")
            
        # Chart 2: Rating distribution (bar)
        fig, ax = plt.subplots(figsize=(10, 6))
        self._plot_rating_distribution(ax)
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "rating_distribution.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved.append("rating_distribution.png")

        # Chart 3: Genre breakdown (bar or pie)
        fig, ax = plt.subplots(figsize=(10, 6))
        self._plot_genre_breakdown(ax)
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "genre_breakdown.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved.append("genre_breakdown.png")
                               
        # Chart 4: Pages read per month (line)
        fig, ax = plt.subplots(figsize=(10, 6))
        self._plot_monthly_pages(ax)
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "monthly_pages.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved.append("monthly_pages.png")

        # Chart 5: Reading pace scatter (pages/day for each finished book)
        fig, ax = plt.subplots(figsize=(10, 6))
        self._plot_reading_pace(ax)
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "reading_pace.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved.append("reading_pace.png")
    
        return saved

    def _plot_monthly_books(self, ax) -> None:
        """Bar chart: books finished per month."""
        books_per_month = self.get_monthly_counts()
        ax.bar(books_per_month.keys(), books_per_month.values())
        ax.set_xlabel("Month")
        ax.set_ylabel("Books")
        ax.set_title("Books Finished Per Month")
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        return ax

    def _plot_rating_distribution(self, ax) -> None:
        """Bar chart: count of books at each rating level."""
        ratings = Counter([b.rating for b in self.books])
        ax.bar(ratings.keys(), ratings.values())
        ax.set_xlabel("Rating")
        ax.set_ylabel("Count")
        ax.set_title("Rating Distribution")
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        return ax

    def _plot_genre_breakdown(self, ax) -> None:
        """Bar or pie chart: books per genre."""
        books_per_genre = Counter([b.genre for b in self.books])
        ax.bar(books_per_genre.keys(), books_per_genre.values())
        ax.set_xlabel("Genre")
        ax.set_ylabel("Count")
        ax.set_title("Genre Breakdown")
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        return ax

    def _plot_monthly_pages(self, ax) -> None:
        """Line chart: total pages read per month."""
        pages = [e.pages for e in self.entries]
        months = [e.date_performed.month for e in self.entries]
        ax.plot(months, pages, marker='o', linewidth=2, label="Pages Read")
        ax.axhline(y=sum(pages)/len(pages), color='green', linestyle='--', label="Average")
        ax.set_xlabel("Month")
        ax.set_ylabel("Pages")
        ax.set_title("Pages Read per Month")
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.tick_params(axis='x', rotation=45)
        return ax

    def _plot_reading_pace(self, ax) -> None:
        """Scatter plot: pages/day for each finished book over time."""
        days = [e.days_to_read for e in self.entries]
        pages = [e.pages for e in self.entries]
        ax.scatter(days, pages, color='blue', label="Pages/Day")
        ax.axhline(y=sum(pages)/len(pages), color='green', linestyle='--', label="Average")
        ax.set_xlabel("Days to Read")
        ax.set_ylabel("Pages")
        ax.set_title("Reading Pace")
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.tick_params(axis='x', rotation=45)
        return ax

    # ── Export ─────────────────────────────

    def export(self, format_name: str, filepath: Path) -> bool:
        """Export books using the specified format strategy.
        
        Uses the EXPORTERS dict to look up the correct exporter.
        Strategy Pattern: callers pick the format, the exporter handles the details.
        """
        exporter = EXPORTERS.get(format_name.lower())
        if not exporter:
            return False
        exporter.export(self.books, filepath)
        return True


# ──────────────────────────────────────
# PRESENTATION
# ──────────────────────────────────────

class ReadingListApp:
    def __init__(self):
        self.manager = ReadingListManager()

    def run(self):
        print(f"\n📚 Your Library: {len(self.manager.books)} books")
        reading = self.manager.filter_by_status(ReadingStatus.READING)
        if reading:
            print(f"📖 Currently reading: {', '.join(b.title for b in reading)}")

        while True:
            print("\n--- Reading List ---")
            print("1. Add book")
            print("2. View all books")
            print("3. View by status")
            print("4. Start reading / Finish / Abandon")
            print("5. Rate a book")
            print("6. Search")
            print("7. Recommendations")
            print("8. Statistics")
            print("9. Generate charts")
            print("10. Export")
            print("11. Book details")
            print("12. Quit")

            choice = input("\nChoose: ").strip()
            # Route to methods
            if choice == "1":
                self.add_book_prompt()
            elif choice == "2":
                self.view_all()
            elif choice == "3":
                self.view_by_status()
            elif choice == "4":
                self.status_transition_prompt()
            elif choice == "5":
                self.rate_prompt()
            elif choice == "6":
                self.search_prompt()
            elif choice == "7":
                self.recommendations_prompt()
            elif choice == "8":
                self.statistics_prompt()
            elif choice == "9":
                self.charts_prompt()
            elif choice == "10":
                self.export_prompt()
            elif choice == "11":
                self.book_details_prompt()
            elif choice == "12":
                break
            else:
                print("Invalid choice. Please try again.")

    def add_book_prompt(self):
        """Get book details from user.
        ISBN, title, author are required.
        Genre, page_count, year, tags are optional.
        """
        isbn = input("Enter ISBN: ")
        title = input("Enter title: ")
        author = input("Enter author: ")
        genre = input("Enter genre (optional): ")
        page_count = input("Enter page count (optional): ")
        year = input("Enter year (optional): ")
        tags = input("Enter tags (comma-separated): ")
        # Add book to library
        # ...
        book = Book(
            isbn=isbn,
            title=title,
            author=author,
            genre=genre or "General",
            page_count=int(page_count) if page_count else 0,
            publication_year=int(year) if year else None,
            tags=[t.strip() for t in tags.split(",")] if tags else []
        )
        self.manager.add_book(book)
        print("Book added successfully.")
        
        return

    def view_all(self):
        """Display all books using brief() format.
        Ask for sort order: name, rating, date added, pages.
        Demonstrates natural __lt__ vs key function sorting.
        """
        for book in self.manager.books:
            book.brief()
        print()

        return

    def view_by_status(self):
        """Let user pick a status, show matching books."""
        status = input("Enter status (read, unread, reading): ")
        for book in self.manager.books:
            if book.status == status:
                book.brief()
        print()
        return

    def status_transition_prompt(self):
        """Handle start/finish/abandon transitions.
        Show current status, available transitions, get user choice.
        """
        for book in self.manager.books:
            if book.status == "reading":
                print(book.title, "is currently reading.")
                print("1. Finish")
                print("2. Abandon")
                choice = input("Enter choice (1/2): ")
                if choice == "1":
                    book.status = "read"
                    self.manager.save()
                    print("Book marked as read.")
                    return
                elif choice == "2":
                    book.status = "unread"
                    self.manager.save()
                    print("Book abandoned.")
                    return
                else:
                    print("Invalid choice. Please enter 1 or 2.")
                    return
            elif book.status == "unread":
                print(book.title, "is unread.")
                print("1. Start")
                print("2. Abandon")
                choice = input("Enter choice (1/2): ")
                if choice == "1":
                    book.status = "reading"
                    self.manager.save()
                    print("Book started.")
                    return
                elif choice == "2":
                    book.status = "unread"
                    self.manager.save()
                    print("Book abandoned.")
                    return
                else:
                    print("Invalid choice. Please enter 1 or 2.")
                    return
            elif book.status == "finished":
                print(book.title, "is finished.")
                return
            else:
                print("Invalid book status.")
                return
        else:
            print("Invalid book ID.")
            return
    
    def rate_prompt(self):
        """Rate a finished book 1–5."""
        title = input("Enter Book Title to rate: ")
        for book in self.manager.books:
            if book.title == title:
                if book.status == "finished":
                    try:
                        rating = int(input("Rate this book (1-5): "))
                        book.rating = rating
                    except ValueError:
                        print("Invalid rating. Please enter a number between 1 and 5.")
                    self.manager.save()
                    print("Rating saved.")
                    return
                else:
                    print("Invalid book status. Please enter a finished book.")
                    return
            else:
                print("Invalid book title")
                return
        return
                    
    def search_prompt(self):
        """Search by title, author, or tag."""
        print("Searching for a book...")
        print("Enter search term:")
        search_term = input()
        print("Search results:")
        for book in self.manager.search(search_term):
            print(book.title, book.author)
            print("-" * 20)
        print("Search complete.")
        return

    def recommendations_prompt(self):
        """Show top 5 recommended unread books with scores."""
        print("Viewing recommendations...")
        print("Recommendations:")
        for book in self.manager.get_recommendations():
            print(f"{book.title} by {book.author}")
            print(f"Score: {book.score}")
            print(f"Tags: {', '.join(book.tags)}")
            print("-" * 20)
        print("Recommendations complete.")
        return

    def statistics_prompt(self):
        """Display comprehensive reading statistics."""
        print("Viewing overall stats...")
        for stat in self.manager.get_statistics():
            print(f"{stat}")
        return

    def charts_prompt(self):
        """Generate and save all charts."""
        print("Generating charts...")
        saved = self.manager.generate_charts()
        print(f"\n📊 {len(saved)} charts saved to {CHARTS_DIR}/:")
        for filename in saved:
            print(f"   {filename}")

    def export_prompt(self):
        """Export to CSV, JSON, or Markdown."""
        print("Exporting data...")
        print("Select export format:")
        print("1. CSV")
        print("2. JSON")
        print("3. Markdown")
        choice = input("Enter choice (1-3): ")
        filepath = input("Enter file path: ")
        if choice == "1":
            self.manager.export('csv', filepath)
            print(f"\n📚 Data exported to {filepath} as CSV.")
        elif choice == "2":
            self.manager.export('json', filepath)
            print(f"\n📚 Data exported to {filepath} as JSON.")
        elif choice == "3":
            self.manager.export('markdown', filepath)
            print(f"\n📚 Data exported to {filepath} as Markdown.")
        else:
            print("Invalid choice. Please try again.")
        return

    def book_details_prompt(self):
        """Show full book card with display_card()."""
        print("Enter book title to view details:")
        title = input("Title: ")
        for book in self.manager.books:
            if book.title == title:
                book.display_card()
                return
        return

if __name__ == "__main__":
    app = ReadingListApp()
    app.run()