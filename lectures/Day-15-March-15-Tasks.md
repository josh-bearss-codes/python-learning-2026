# DAY 15 — Sunday, March 15, 2026
## Lecture: The Capstone — Everything You Know, One System. Then the Shift.

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue)  
**Phase**: Foundation — FINAL DAY of hand-writing code  
**Morning Session**: 8:00–11:00 AM (3 hours) — Build the Week 2 capstone project  
**Evening Session**: 7:00–8:30 PM (1.5 hours) — Week 2 review + Week 3 preparation  
**Today's theme**: Synthesis — proving you can combine every concept from two weeks into one coherent system. Then preparing for the paradigm shift.

---

## OPENING LECTURE: WHAT A CAPSTONE PROVES

In university, a capstone project exists to prove that you can synthesize knowledge from an entire program into a single coherent work. It's not about learning new concepts — it's about demonstrating that the concepts you've already learned can work together in a system that's more than the sum of its parts.

That's today. You're not learning new Python concepts. You're proving to yourself that the concepts from 14 days can combine into a complete, well-architected application.

Let me enumerate what you know and where each piece appears in today's project:

| Week | Day | Concept | How It Appears Today |
|------|-----|---------|---------------------|
| 1 | 1–4 | Functions, file I/O, JSON, error handling | Core infrastructure of the entire app |
| 1 | 5–6 | Classes, `__init__`, `__str__`, `@property`, argparse, lambda, sorted(key=) | Every entity, every sort operation |
| 1 | 7 | Layered architecture, separation of concerns | The overall structure: data → logic → presentation |
| 1 | 8 | Pipeline pattern, logging, dataclasses, type hints | Data import/export pipeline |
| 2 | 9 | Composition, nested serialization, `any()`/`all()` | Books with nested data, search functionality |
| 2 | 10 | Date arithmetic, `set`, `@property` computed values, `@classmethod` factory | Reading dates, computed statistics, deserialization |
| 2 | 11 | `__eq__`/`__lt__`/`@total_ordering`, `__repr__`, property setters, Enum | Book identity, sorting, validated ratings |
| 2 | 12 | Many-to-many, mediator pattern, `__hash__`, weighted averages | Books ↔ Tags relationship, weighted rating calculations |
| 2 | 13 | Strategy pattern, pathlib, dry-run preview | Export formatters, file operations |
| 2 | 14 | matplotlib, objects that render themselves | Reading statistics charts |

Every concept. One project. This is the test.

---

## LECTURE: THE DOMAIN — A PERSONAL LIBRARY

A reading list tracker sounds simple. It's not. A well-designed one requires:

**Rich data modeling**: A Book isn't just a title and author. It has an ISBN, publication year, page count, genre, reading status (want-to-read, reading, finished, abandoned), your personal rating, a start date, a finish date, and notes. Some of these are mandatory, some are optional, and some have validation constraints (rating must be 1–5, page count must be positive).

**Many-to-many relationships**: Books have Tags (fiction, sci-fi, business, self-improvement). One book has many tags. One tag applies to many books. This is the Day 12 pattern — you need either a mediator or a simpler approach (since there's no data on the relationship itself, a simple list of tag strings on each Book works).

**Temporal tracking**: When did you start a book? When did you finish? How many pages per day did you average? What's your reading pace this month vs. last month? This is Day 10's date arithmetic applied to a new domain.

**Multiple sort orders**: By title, by author, by rating, by date finished, by page count. This is Day 11's comparison operators — `__lt__` for natural ordering, `key` functions for alternatives.

**Statistics with weighted averages**: Your average rating across all books. But should a 600-page book you spent three weeks on count the same as a 100-page book you read in an afternoon? A weighted average using page count (or time spent) as weight might be more meaningful. This is Day 12's GPA calculation in a different domain.

**Export to multiple formats**: CSV for spreadsheets, JSON for backup, markdown for a blog post. This is Day 13's Strategy Pattern — different export formatters with a common interface.

**Visualization**: A chart showing books read per month, average rating over time, genre distribution. This is Day 14's matplotlib with the `plot()` method pattern.

The point is this: **the domain is simple enough to understand immediately, but the architecture required to model it well uses every concept from two weeks.** That's what makes it a capstone.

---

## LECTURE: READING STATUS AS A STATE MACHINE

One concept that ties together several things you've learned: the reading status of a book is a **state machine** — a system with defined states and valid transitions between them.

```
                    ┌────────────┐
                    │ WANT_TO_   │
              ┌────→│   READ     │←────┐
              │     └─────┬──────┘     │
              │           │            │
              │     start_reading()    │
              │           │            │
              │     ┌─────▼──────┐     │
              │     │  READING   │     │
              │     └──┬─────┬───┘     │
              │        │     │         │
              │  finish()  abandon()   │
              │        │     │         │
              │  ┌─────▼──┐ ┌▼────────┤
              │  │FINISHED│ │ABANDONED │
              │  └────────┘ └─────────┘
              │                   │
              └───────────────────┘
                 re-add to list
```

**Valid transitions**:
- WANT_TO_READ → READING (start reading)
- READING → FINISHED (complete the book)
- READING → ABANDONED (gave up)
- ABANDONED → WANT_TO_READ (changed mind, want to try again)
- FINISHED → (no further transitions — a finished book stays finished)

**Invalid transitions** (these should be rejected):
- WANT_TO_READ → FINISHED (can't finish a book you haven't started)
- FINISHED → READING (can't un-finish a book)
- WANT_TO_READ → ABANDONED (can't abandon a book you haven't started)

Implementing this as an Enum with transition validation on the Book class:

```python
from enum import Enum

class ReadingStatus(Enum):
    WANT_TO_READ = "want_to_read"
    READING = "reading"
    FINISHED = "finished"
    ABANDONED = "abandoned"

# Valid transitions: {current_status: [allowed_next_statuses]}
VALID_TRANSITIONS = {
    ReadingStatus.WANT_TO_READ: [ReadingStatus.READING],
    ReadingStatus.READING: [ReadingStatus.FINISHED, ReadingStatus.ABANDONED],
    ReadingStatus.ABANDONED: [ReadingStatus.WANT_TO_READ],
    ReadingStatus.FINISHED: [],  # Terminal state — no transitions allowed
}
```

Then on the Book class:

```python
class Book:
    def transition_to(self, new_status: ReadingStatus) -> bool:
        """Attempt to change reading status.
        
        Validates the transition against the state machine.
        Returns True if successful, False if invalid transition.
        
        Also handles side effects:
          - WANT_TO_READ → READING: sets start_date to today
          - READING → FINISHED: sets finish_date to today
        """
        if new_status not in VALID_TRANSITIONS.get(self.status, []):
            return False  # Invalid transition
        
        # Handle side effects
        if new_status == ReadingStatus.READING:
            self.start_date = date.today()
        elif new_status == ReadingStatus.FINISHED:
            self.finish_date = date.today()
        
        self.status = new_status
        return True
```

**Why model it this way?** Because the alternative — letting any code set `book.status` to anything — leads to inconsistent data. A book marked as FINISHED with no finish_date. A book marked as READING with a finish_date but no start_date. State machines prevent these inconsistencies by ensuring transitions are valid and side effects (setting dates) happen automatically.

This is a real-world pattern. Order processing (placed → paid → shipped → delivered), user accounts (pending → active → suspended → deleted), and CI/CD pipelines (queued → building → testing → deployed) all use state machines. The principle is the same: define valid states, define valid transitions, reject everything else.

---

## LECTURE: THE RECOMMENDATION ENGINE — SIMPLE BUT POWERFUL

Today's project includes a recommendation feature: "Based on books you've rated highly, what else in your list should you read next?" This sounds like it requires machine learning. It doesn't. A simple scoring algorithm works surprisingly well:

**The algorithm**: For each unread book, calculate a "recommendation score" based on how similar it is to books you've rated highly (4 or 5 stars).

Similarity factors:
- **Same author**: If you rated another book by the same author 4+ stars, strong signal (+3 points)
- **Same genre**: If you rated books in the same genre highly, moderate signal (+2 points per matching genre)
- **Shared tags**: Each tag shared with a highly-rated book adds a point (+1 per shared tag)
- **Similar page count**: If the book's page count is within 20% of books you've enjoyed, slight signal (+1 point)

This is not machine learning — it's **rule-based scoring.** Each rule contributes points, and the total score ranks the recommendations. It's the same pattern as the inventory alert levels (Day 11), where multiple factors combine into a single assessment.

```python
def calculate_recommendation_score(self, candidate_book, rated_books):
    """Score an unread book based on similarity to highly-rated books.
    
    This is a simple rule-based recommender, not ML.
    Each rule contributes points. Higher total = stronger recommendation.
    """
    score = 0
    highly_rated = [b for b in rated_books if b.rating and b.rating >= 4]
    
    for rated in highly_rated:
        # Same author is a strong signal
        if candidate_book.author == rated.author:
            score += 3
        
        # Same genre
        if candidate_book.genre == rated.genre:
            score += 2
        
        # Shared tags (Day 9's any()/set intersection)
        shared = set(candidate_book.tags) & set(rated.tags)
        score += len(shared)
    
    return score
```

**The OOP lesson**: This method belongs on the `ReadingListManager` (the mediator/business logic class), not on the `Book` class. Why? Because recommendation requires knowledge of *other* books. A single Book doesn't know about other books — only the manager does. This is the separation of concerns principle: individual objects manage their own data; the manager handles cross-object queries.

---

## PROJECT 22: `reading_list.py` (~2.5 hours)

### The Problem

Build a comprehensive personal library tracker. The user manages their reading list: adding books with rich metadata, tracking reading status through a state machine, rating finished books, searching and filtering by various criteria, getting recommendations based on their taste, exporting in multiple formats, and generating reading statistics with charts.

### Design Questions (Answer These BEFORE You Code)

1. **What is the complete Book data model?**

   | Attribute | Type | Stored/Computed | Validation |
   |-----------|------|----------------|------------|
   | `isbn` | str | Stored | Unique identifier (equality key) |
   | `title` | str | Stored | Required, non-empty |
   | `author` | str | Stored | Required, non-empty |
   | `genre` | str | Stored | Optional, default "General" |
   | `page_count` | int | Stored | Must be positive |
   | `publication_year` | int | Stored | Optional |
   | `tags` | list[str] | Stored | Optional, default [] |
   | `status` | ReadingStatus | Stored | Enum, transition-validated |
   | `rating` | int or None | Stored | 1–5 via property setter, only if FINISHED |
   | `start_date` | date or None | Stored | Set automatically on READING transition |
   | `finish_date` | date or None | Stored | Set automatically on FINISHED transition |
   | `notes` | str | Stored | Optional free text |
   | `date_added` | date | Stored | Set on creation, default today |
   | `days_to_read` | int or None | **Computed** | finish_date - start_date, @property |
   | `reading_pace` | float or None | **Computed** | page_count / days_to_read, @property |

2. **What are the comparison semantics?**

   - `__eq__` and `__hash__`: based on `isbn` (two Book objects are the same book if they share an ISBN, regardless of differing metadata)
   - `__lt__` with `@total_ordering`: natural ordering by `(author, title)` — this produces alphabetical-by-author bookshelves, which is the most common library ordering
   - Alternative sorts via `key`: by rating (highest first), by finish_date (most recent first), by page_count, by recommendation score

3. **How does the rating property setter work?**

   Rating should only be assignable when the book's status is FINISHED. Setting a rating on a WANT_TO_READ or READING book should raise a ValueError. And the rating must be between 1 and 5 inclusive.

   ```python
   @property
   def rating(self):
       return self._rating
   
   @rating.setter
   def rating(self, value):
       if self.status != ReadingStatus.FINISHED:
           raise ValueError("Can only rate finished books")
       if not isinstance(value, int) or value < 1 or value > 5:
           raise ValueError("Rating must be an integer 1–5")
       self._rating = value
   ```

   This is business rule enforcement through property setters (Day 11) combined with state machine validation (today's lecture).

4. **What export formats should be supported?**

   Three exporters, each using the Strategy Pattern (Day 13):
   - **CSV**: one row per book, columns for all attributes
   - **JSON**: full nested export for backup/restore
   - **Markdown**: formatted reading list for a blog post or README

   Each exporter is a class with a common `export(books, filepath)` method. The presentation layer lets the user pick the format.

5. **What charts should be generated?**

   - **Books per month** (bar chart): how many books you finished each month
   - **Rating distribution** (bar chart): how many books at each rating level (1–5)
   - **Genre breakdown** (pie or bar): what genres you read most
   - **Pages per month** (line chart): total pages read over time — a volume metric
   - **Reading pace** (scatter plot): pages/day for each finished book — are you speeding up or slowing down?

### Ask GLM-4.7-Flash Before Coding

`Cmd+L` → "Explain these Python concepts:

1. State machines in Python — how to model valid states as an Enum, define valid transitions in a dictionary, and validate transitions before applying them. Include the concept of side effects on transition (like setting a date when status changes).

2. Set intersection in Python — how `set_a & set_b` gives the shared elements, and how `len(set_a & set_b)` counts them. How this is useful for finding shared tags between two objects.

3. Multiple export formats using the Strategy Pattern — how to define different exporter classes with a common `export()` method so the caller can switch formats without changing any other code.

Explain each concept clearly with examples. Don't write my program."

### Skeletal Structure

```python
import json
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import date, timedelta
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

    def __hash__(self) -> int:
        # Hash on ISBN

    def __lt__(self, other) -> bool:
        # Natural ordering: (author, title)

    # ── Display ───────────────────────────

    def __repr__(self) -> str:
        # "Book(isbn='978...', title='Dune', author='Frank Herbert')"

    def __str__(self) -> str:
        # Rich display:
        # "Dune by Frank Herbert (1965) — ★★★★★"
        # "  Sci-Fi | 412 pages | Finished in 14 days (29.4 pg/day)"
        # "  Tags: science-fiction, classic, desert"

    def brief(self) -> str:
        """One-line display for list views."""
        # "[FINISHED] Dune — Frank Herbert ★★★★★"
        # "[READING]  Project Hail Mary — Andy Weir (started Mar 10)"
        # "[WANT]     Neuromancer — William Gibson"

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

    # ── Serialization ─────────────────────

    def to_dict(self) -> dict:
        # Serialize everything
        # Dates as ISO strings or None
        # Status as enum value string
        # Rating as int or None

    @classmethod
    def from_dict(cls, data: dict):
        # Deserialize
        # Parse ISO date strings back to date objects
        # Parse status string back to ReadingStatus enum
        # Use _rating bypass for loading (don't trigger setter validation)


# ──────────────────────────────────────
# EXPORT STRATEGIES (Day 13 Strategy Pattern)
# ──────────────────────────────────────

class CSVExporter:
    """Export reading list to CSV format."""
    
    def export(self, books: list, filepath: Path) -> None:
        """Write books to CSV with DictWriter.
        Headers: ISBN, Title, Author, Genre, Pages, Year, Status, Rating, Tags
        """

class JSONExporter:
    """Export reading list to JSON format (backup/restore)."""
    
    def export(self, books: list, filepath: Path) -> None:
        """Write books to pretty-printed JSON."""

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

    def save(self, books: list) -> None:
        """Save all books to JSON."""


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

    def remove_book(self, isbn: str) -> bool:
        """Remove a book by ISBN."""

    def find_by_isbn(self, isbn: str):
        """Find a book by ISBN. Returns Book or None."""

    # ── Status Transitions ────────────────

    def start_reading(self, isbn: str) -> bool:
        """Transition a book to READING status."""

    def finish_book(self, isbn: str, rating: int = None) -> bool:
        """Transition to FINISHED and optionally set rating."""

    def abandon_book(self, isbn: str) -> bool:
        """Transition to ABANDONED."""

    def rate_book(self, isbn: str, rating: int) -> bool:
        """Set or update rating on a finished book."""

    # ── Search & Filter ───────────────────

    def search(self, query: str) -> list:
        """Search by title, author, or tags (case-insensitive, partial match)."""
        # Check title, author, and tags using any()

    def filter_by_status(self, status: ReadingStatus) -> list:
        """All books with a given status, sorted naturally (__lt__)."""
        return sorted([b for b in self.books if b.status == status])

    def filter_by_genre(self, genre: str) -> list:
        """Books in a specific genre."""

    def filter_by_tag(self, tag: str) -> list:
        """Books that have a specific tag."""

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

    def get_monthly_counts(self) -> dict:
        """Books finished per month.
        Returns: {"2026-01": 3, "2026-02": 5, "2026-03": 2}
        Uses finish_date.strftime("%Y-%m") as grouping key.
        """

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
        return score

    # ── Charts ────────────────────────────

    def generate_charts(self) -> list:
        """Generate all reading statistics charts.
        Returns list of saved filenames.
        """
        CHARTS_DIR.mkdir(exist_ok=True)
        saved = []

        # Chart 1: Books finished per month (bar)
        # Chart 2: Rating distribution (bar)
        # Chart 3: Genre breakdown (bar or pie)
        # Chart 4: Pages read per month (line)
        # Chart 5: Reading pace scatter (pages/day for each finished book)

        return saved

    def _plot_monthly_books(self, ax) -> None:
        """Bar chart: books finished per month."""

    def _plot_rating_distribution(self, ax) -> None:
        """Bar chart: count of books at each rating level."""

    def _plot_genre_breakdown(self, ax) -> None:
        """Bar or pie chart: books per genre."""

    def _plot_monthly_pages(self, ax) -> None:
        """Line chart: total pages read per month."""

    def _plot_reading_pace(self, ax) -> None:
        """Scatter plot: pages/day for each finished book over time."""

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

    def add_book_prompt(self):
        """Get book details from user.
        ISBN, title, author are required.
        Genre, page_count, year, tags are optional.
        """

    def view_all(self):
        """Display all books using brief() format.
        Ask for sort order: name, rating, date added, pages.
        Demonstrates natural __lt__ vs key function sorting.
        """

    def view_by_status(self):
        """Let user pick a status, show matching books."""

    def status_transition_prompt(self):
        """Handle start/finish/abandon transitions.
        Show current status, available transitions, get user choice.
        """

    def rate_prompt(self):
        """Rate a finished book 1–5."""

    def search_prompt(self):
        """Search by title, author, or tag."""

    def recommendations_prompt(self):
        """Show top 5 recommended unread books with scores."""

    def statistics_prompt(self):
        """Display comprehensive reading statistics."""

    def charts_prompt(self):
        """Generate and save all charts."""

    def export_prompt(self):
        """Export to CSV, JSON, or Markdown."""

    def book_details_prompt(self):
        """Show full book card with display_card()."""


if __name__ == "__main__":
    app = ReadingListApp()
    app.run()
```

### Seed Data for Testing

Add at least 8-10 books across different statuses to test all features:

```
Finished books (with ratings):
  - Dune, Frank Herbert, Sci-Fi, 412 pages, 1965, rating 5, tags: [science-fiction, classic]
  - Project Hail Mary, Andy Weir, Sci-Fi, 476 pages, 2021, rating 5, tags: [science-fiction, space]
  - Clean Code, Robert Martin, Technical, 464 pages, 2008, rating 4, tags: [programming, best-practices]
  - Atomic Habits, James Clear, Self-Help, 320 pages, 2018, rating 4, tags: [habits, productivity]
  - The Great Gatsby, F. Scott Fitzgerald, Fiction, 180 pages, 1925, rating 3, tags: [classic, fiction]

Currently reading:
  - Designing Data-Intensive Applications, Martin Kleppmann, Technical, 616 pages, tags: [data-engineering, distributed-systems]

Want to read:
  - Neuromancer, William Gibson, Sci-Fi, 271 pages, tags: [science-fiction, cyberpunk]
  - The Pragmatic Programmer, David Thomas, Technical, 352 pages, tags: [programming, best-practices]
  - Rendezvous with Rama, Arthur C. Clarke, Sci-Fi, 243 pages, tags: [science-fiction, classic, space]

Abandoned:
  - Some Boring Book, Unknown Author, Fiction, 500 pages, rating: None
```

**Test your recommendations**: With the data above, "Rendezvous with Rama" should score highest (same genre as two 5-star books, shares "science-fiction" and "classic" and "space" tags). "The Pragmatic Programmer" should score well too (same genre as a 4-star book, shares "programming" and "best-practices" tags). "Neuromancer" should be mid-range (same genre, shares "science-fiction").

### Ask GLM-4.7-Flash After Coding — The Final Review

Select all code → `Cmd+L` →

"Review this reading list tracker as a senior developer. This is my Week 2 capstone — it's meant to combine every concept from 14 days of learning. Specifically evaluate:

1. Does the architecture have clean layers — data model, persistence, business logic, presentation?
2. Is the state machine (ReadingStatus transitions) correctly implemented? Are invalid transitions properly rejected? Are side effects (setting dates) handled correctly?
3. Are my comparison operators (__eq__ on ISBN, __lt__ on author/title, __hash__ on ISBN) consistent and correct?
4. Does the property setter on rating correctly enforce 'only finished books can be rated, 1–5 only'?
5. Is the recommendation algorithm reasonable? Is the scoring logic clear and extensible?
6. Is the export Strategy Pattern properly implemented? Could I add a new format without changing existing code?
7. Am I using matplotlib correctly for the charts? Are figures properly closed after saving?
8. What is the weakest part of this codebase? Where would a senior developer focus refactoring efforts?
9. Is this codebase ready to be shown in a portfolio?"

**Read every suggestion. Implement the changes yourself. This is the last hand-written project — make it your best.**

```bash
git add . && git commit -m "Project 22: reading_list.py — Week 2 capstone, state machine, recommendations, export strategies, charts"
```

---

## BREAK — Afternoon

Take a real break. Walk the dog. Meal prep. Lift. You've been coding for 3 hours on your most complex project yet. The evening session is reflection and preparation — no building.

---

## EVENING SESSION (7:00–8:30 PM): WEEK 2 REVIEW + WEEK 3 PREPARATION

### Week 2 by the Numbers

| Day | Project | Architecture Principle | Hours |
|-----|---------|----------------------|-------|
| 9 | Recipe Manager | Composition, nested serialization | 2 |
| 10 | Habit Tracker | Event sourcing, computed properties, dates | 2 |
| 11 | Inventory System | Comparison operators, property setters, Enums | 2 |
| 12 | Student Gradebook | Many-to-many, mediator, weighted averages | 2 |
| 13 | File Organizer | Strategy pattern, dry-run, filesystem ops | 2 |
| 14 | Workout Logger | matplotlib, objects render themselves | 3 |
| **15** | **Reading List** | **Capstone: everything combined** | **3** |
| | | **Week 2 Total** | **16 hours, 7 projects** |

**Combined Weeks 1–2**: 34 hours, 22 projects.

### Reflection Exercise

Create `~/dev/year-1/month-01/week-02/week-02-review.md` and answer honestly:

1. **Which design principle felt most natural?** Composition? Strategy? State machines? The one that clicked fastest is probably where your existing engineering instincts transfer best.

2. **Which design principle still feels forced?** Is it comparison operators? Property setters? The mediator pattern? Identify what needs more practice — you'll encounter these patterns again when reviewing AI-generated code.

3. **Look at your Day 1 code vs. your Day 15 code.** The difference should be dramatic. Your Day 1 `hello.py` was a linear script. Your Day 15 `reading_list.py` has state machines, strategy patterns, computed properties, and chart generation. That's two weeks.

4. **How did the AI review workflow change your code?** Compare your initial implementations to the post-review versions. What patterns did GLM-4.7-Flash consistently suggest? Which suggestions were most valuable?

5. **Can you read Python code fluently now?** Open one of your projects and read it top to bottom. Can you follow the logic without running it? Can you predict what each method does from its name and signature? This reading fluency is what enables the Week 3 shift.

### THE SHIFT: Preparing for Week 3

**Tomorrow, everything changes.**

For two weeks, you've written every line of code yourself. AI explained concepts and reviewed your work, but *you* typed every function, every class, every loop.

Starting Monday, you **stop writing most code.** Instead:

1. **You write the architectural spec** — a plain-English document describing what the program does, what classes exist, what methods they have, how they interact, what edge cases matter, and what patterns to use.

2. **You give the spec to GLM-4.7-Flash** (or Qwen3-Coder-Next for complex projects) and ask it to implement the code.

3. **You review every line the AI writes.** Is it correct? Does it follow the architecture you specified? Did it use the right patterns? Are there bugs? Missing error handling? Security issues?

4. **You fix what's wrong yourself.** Don't ask AI to fix AI. The act of finding and correcting AI errors is the skill that makes you worth $150–$250/hour.

This is the **10-80-10 model**: you do the first 10% (architecture), AI does the middle 80% (implementation), you do the last 10% (review, testing, debugging).

### Practical Preparation for Monday

**Tomorrow's commute content**: Listen to a podcast or video about AI-assisted development, prompt engineering, or working with LLMs for code generation. Understand the workflow before you do it.

**Mental preparation**: Your role shifts from *writer* to *architect and reviewer.* The Python knowledge you built over two weeks isn't about typing code faster — it's about *evaluating* code that someone else (AI) typed. Can you spot a bug in a function you didn't write? Can you tell if a class design is clean or messy? Can you determine if an algorithm is correct without running it? Those are your skills now.

**Review your Continue model stack**: Make sure GLM-4.7-Flash and Qwen3-Coder-Next are both available and responding. You'll use GLM-4.7-Flash for most projects and switch to Qwen3-Coder-Next when the task is architecturally complex.

### Repo Organization

Clean up before Week 3:

```bash
cd ~/dev/year-1

# Make sure week-01 and week-02 folders are organized
ls month-01/week-01/    # Should have 15 project files + review
ls month-01/week-02/    # Should have 7 project files + review

# Create the week-03 folder
mkdir -p month-01/week-03

# Final commit
git add .
git commit -m "Week 2 complete: 7 projects, capstone done, ready for Week 3 shift"
git push
```

---

## CLOSING LECTURE: THE FOUNDATION IS COMPLETE

Two weeks ago you wrote `print("Hello, World!")`. Today you built a system with state machines, recommendation engines, strategy-pattern exporters, matplotlib charts, property-validated ratings, and comparison-based sorting — all in clean layered architecture.

You didn't just learn Python syntax. You learned software engineering principles *expressed in* Python:

- **Separation of concerns** (Day 7) — why layers exist
- **Event sourcing** (Day 10) — store facts, derive state
- **Business rule enforcement** (Day 11) — objects that reject invalid state
- **The mediator pattern** (Day 12) — managing relationships through a third object
- **The strategy pattern** (Day 13) — interchangeable algorithms
- **Objects that render themselves** (Day 14) — visualization as a method
- **State machines** (Day 15) — valid transitions with side effects

These aren't Python concepts. They're **engineering concepts** that happen to be implemented in Python. They'll apply regardless of what language or framework you use. And they're exactly what AI cannot do for you — AI generates implementations, not architectures.

Starting tomorrow, you'll prove this. You'll write architectural specs and watch AI generate code from them. When the AI gets the architecture wrong (and it will), you'll know — because you spent two weeks learning what *right* looks like.

**The foundation is complete. The shift begins.**

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 15
- [ ] Day number: 15
- [ ] Hours coded: 3 (morning) + 1.5 (evening review) = 4.5
- [ ] Projects completed: 1 (reading_list — Week 2 capstone)
- [ ] All 22 projects complete across 2 weeks ✓
- [ ] Week 2 review written ✓
- [ ] Week 3 folder created ✓
- [ ] Ready for the shift to AI-directed development ✓
- [ ] Mood/energy (1–5): ___

---

**Day 15 of 365. Week 2 complete. 22 projects. The foundation is set. Tomorrow you become the architect.** 🚀
