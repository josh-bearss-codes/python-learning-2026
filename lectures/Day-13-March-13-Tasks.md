# DAY 13 — Friday, March 13, 2026
## Lecture: Programs That Touch the Real World — Filesystem Operations and the Strategy Pattern

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue)  
**Phase**: Foundation — you write, AI reviews more aggressively  
**Commute**: Talk Python To Me or Python Bytes  
**Evening Session**: 7:00–9:00 PM (2 hours) — Build 1 project  
**Today's theme**: The leap from programs that manage data to programs that act on the physical world — moving real files, creating real directories, and the irreversibility that comes with it

---

## OPENING LECTURE: THE IRREVERSIBILITY BOUNDARY

Every program you've written so far has been **safe**. If your budget tracker had a bug, the worst outcome was a corrupted JSON file you could delete and recreate. If your gradebook's GPA calculation was wrong, you'd fix the formula and recalculate. Data in memory and data in JSON files is soft — malleable, recoverable, forgiving.

Tonight you cross a boundary. Your program will move real files on your real filesystem. If it moves a file to the wrong directory, that file is in the wrong directory. If it renames a file incorrectly, that file has the wrong name. If it overwrites a file that already exists at the destination, the original is gone. These operations are **irreversible** in a way that JSON manipulation is not.

This might seem like a small distinction, but it's one of the most important lessons in software engineering:

> **Programs that affect the real world require a fundamentally different design philosophy than programs that manage internal data.**

That philosophy has three pillars:

1. **Preview before execute.** The program should show what it *would* do before actually doing it. "I would move `report.pdf` from Downloads to Documents/PDFs." The user reviews the plan. Only then does execution happen. This is called a **dry run**.

2. **Logging every action.** Every file moved, every directory created, every conflict encountered is logged with a timestamp. If something goes wrong, the log tells you exactly what happened and when.

3. **Handling conflicts explicitly.** What happens when `report.pdf` already exists at the destination? The program must not silently overwrite it. It must either skip, rename (add a suffix), or ask the user. The conflict resolution strategy must be defined upfront, not discovered at runtime by a crash.

These principles apply directly to your future work:

- **AI data pipelines**: When your RAG system ingests documents, it moves/copies files into a processing directory. Duplicate detection, conflict resolution, and dry-run previews are essential.
- **Client deliverables**: When you deploy a private AI system to a client's infrastructure, your setup scripts create directories, move configuration files, and modify system paths. One wrong move can break their environment.
- **Automation tools**: The backup automator you'll build in Week 3 moves files on a schedule. It must never silently overwrite a newer file with an older backup.

Let's learn the tools that make this possible.

---

## LECTURE: PYTHON'S FILESYSTEM TOOLKIT — `pathlib`, `os`, AND `shutil`

Python has three modules for filesystem operations. They overlap somewhat, but each has a distinct role. Understanding which to use when is important.

### `pathlib` — Object-Oriented Path Manipulation (Your Primary Tool)

`pathlib` represents file paths as objects with methods, rather than plain strings. This is the modern, Pythonic approach introduced in Python 3.4.

```python
from pathlib import Path

# Creating paths
downloads = Path.home() / "Downloads"      # /Users/josh/Downloads
report = downloads / "report.pdf"          # /Users/josh/Downloads/report.pdf

# The / operator joins path segments — this is pathlib's signature feature
# It's actually the __truediv__ dunder method on Path objects!
# Path.__truediv__(self, other) is called when you write path / "segment"
```

**Why this matters for your OOP understanding**: The `/` operator on Path objects is a **dunder method** — specifically `__truediv__`. When you write `downloads / "report.pdf"`, Python calls `downloads.__truediv__("report.pdf")`. This is the same mechanism as `__lt__` for comparison or `__eq__` for equality. The Path class teaches Python that `/` means "join paths" rather than "divide numbers." This is called **operator overloading** — the same operator does different things depending on the types involved.

```python
# Inspecting paths
report = Path("/Users/josh/Downloads/report.pdf")

report.name              # "report.pdf"        — filename with extension
report.stem              # "report"             — filename without extension
report.suffix            # ".pdf"               — extension (including the dot)
report.parent            # Path("/Users/josh/Downloads")  — parent directory
report.parents           # All ancestors up to root

# Checking existence and type
report.exists()          # True/False — does this path exist on disk?
report.is_file()         # True/False — is it a regular file?
report.is_dir()          # True/False — is it a directory?

# Getting file metadata
report.stat().st_size    # File size in bytes
report.stat().st_mtime   # Last modified time (Unix timestamp)

# Converting modification time to a readable date
from datetime import datetime
mod_time = datetime.fromtimestamp(report.stat().st_mtime)
# datetime(2026, 3, 10, 14, 23, 45)
```

**Creating directories**:

```python
# Create a single directory
Path("organized/PDFs").mkdir()           # Fails if "organized" doesn't exist

# Create a directory and all missing parents
Path("organized/PDFs").mkdir(parents=True, exist_ok=True)
# parents=True  → creates "organized" if it doesn't exist
# exist_ok=True → doesn't error if "PDFs" already exists
```

The `exist_ok=True` parameter is a **design decision by the Python standard library** that embodies the irreversibility principle. Without it, calling `mkdir()` on an existing directory raises `FileExistsError`. With it, the operation is **idempotent** — you can call it multiple times with the same result. Your data engineering instincts should recognize this immediately: idempotency is a core principle of reliable pipeline design.

**Listing directory contents**:

```python
downloads = Path.home() / "Downloads"

# All items (files and directories)
for item in downloads.iterdir():
    print(item.name, "—", "dir" if item.is_dir() else "file")

# Only files matching a pattern (glob)
for pdf in downloads.glob("*.pdf"):
    print(pdf.name)

# Recursive glob — searches subdirectories too
for py_file in downloads.glob("**/*.py"):
    print(py_file)
```

The `glob()` method uses pattern matching: `*` matches any sequence of characters, `**` matches any depth of subdirectories, `?` matches a single character. `*.pdf` means "anything ending in .pdf." `**/*.py` means "any .py file at any depth."

### `shutil` — High-Level File Operations (Moving, Copying)

`pathlib` handles path manipulation and inspection. `shutil` handles the actual moving and copying of files:

```python
import shutil
from pathlib import Path

source = Path("Downloads/report.pdf")
destination = Path("Documents/PDFs/report.pdf")

# Copy a file (preserves the original)
shutil.copy2(source, destination)
# copy2 preserves metadata (modification time, permissions)
# copy  would only copy content, not metadata

# Move a file (removes from source)
shutil.move(str(source), str(destination))
# Note: shutil.move takes strings, not Path objects (historical API)
# Always convert: str(path)
```

**Critical distinction**: `shutil.copy2()` is safe — the original stays. `shutil.move()` is destructive — the original is gone. Your file organizer should use `shutil.move()` (the whole point is to organize files by moving them), but the dry-run preview becomes even more important because the operation removes files from their original location.

### `os` — Lower-Level Operations (When You Need Them)

The `os` module provides lower-level filesystem access. You'll use it less often than `pathlib`, but some operations are still easier with `os`:

```python
import os

# Environment variables
home = os.environ.get("HOME")      # "/Users/josh"

# Rename a file (same as move within a directory)
os.rename("old_name.txt", "new_name.txt")

# Delete a file
os.remove("unwanted_file.txt")

# Check permissions
os.access("file.txt", os.R_OK)     # Can we read it?
os.access("file.txt", os.W_OK)     # Can we write it?
```

**General rule**: Use `pathlib` for path manipulation and inspection. Use `shutil` for moving and copying. Fall back to `os` only for operations that `pathlib` and `shutil` don't cover (environment variables, low-level permissions, process-level operations).

---

## LECTURE: THE STRATEGY PATTERN — RULES THAT DECIDE BEHAVIOR

Your file organizer needs to decide *where* each file goes. A PDF goes to a "PDFs" folder. An image goes to an "Images" folder. A Python script goes to "Code." But these rules aren't hardcoded logic — they're **strategies** that should be configurable, extensible, and testable independently.

The **Strategy Pattern** says: encapsulate a family of algorithms (strategies) and make them interchangeable. Instead of a giant if/elif chain that mixes "how to classify files" with "how to move files," you separate the two concerns.

### The Problem With if/elif Chains

A naive approach looks like this:

```python
def organize(filepath):
    if filepath.suffix in [".pdf", ".doc", ".docx", ".txt"]:
        dest = "Documents"
    elif filepath.suffix in [".jpg", ".jpeg", ".png", ".gif", ".svg"]:
        dest = "Images"
    elif filepath.suffix in [".py", ".js", ".html", ".css"]:
        dest = "Code"
    elif filepath.suffix in [".mp3", ".wav", ".flac"]:
        dest = "Music"
    elif filepath.suffix in [".mp4", ".mov", ".avi"]:
        dest = "Videos"
    else:
        dest = "Other"
    # ... move the file
```

This works for a small number of categories. But it has problems:

1. **Adding a new category requires modifying the function.** Want to add "Spreadsheets"? You edit the function. Want to organize by date instead of type? You rewrite the function. The classification logic and the file-moving logic are tangled together.

2. **It's not testable in isolation.** You can't test the classification rules without actually having files on disk. The rules and the filesystem operations are coupled.

3. **It can't handle multiple strategies.** What if the user wants to organize by file type AND then by date within each type? The if/elif chain doesn't compose.

### The Solution: Rules as Objects

Make each classification rule an object with a consistent interface:

```python
class FileRule:
    """A rule that determines where a file should go."""
    
    def __init__(self, name, extensions, destination):
        self.name = name
        self.extensions = {ext.lower() for ext in extensions}  # Set for O(1) lookup
        self.destination = destination
    
    def matches(self, filepath: Path) -> bool:
        """Does this rule apply to this file?"""
        return filepath.suffix.lower() in self.extensions
    
    def __repr__(self):
        return f"FileRule('{self.name}' → '{self.destination}')"
```

Now rules are data, not code:

```python
rules = [
    FileRule("Documents", [".pdf", ".doc", ".docx", ".txt", ".rtf"], "Documents"),
    FileRule("Images", [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"], "Images"),
    FileRule("Code", [".py", ".js", ".html", ".css", ".java", ".cpp"], "Code"),
    FileRule("Music", [".mp3", ".wav", ".flac", ".aac"], "Music"),
    FileRule("Videos", [".mp4", ".mov", ".avi", ".mkv"], "Videos"),
    FileRule("Spreadsheets", [".csv", ".xlsx", ".xls"], "Spreadsheets"),
    FileRule("Archives", [".zip", ".tar", ".gz", ".7z", ".rar"], "Archives"),
]
```

Adding a new category? Add a `FileRule` object. No function changes. Want to organize by date? Create a different kind of rule object — a `DateRule` that checks modification time instead of extension. The organizer doesn't care *how* the rule makes its decision — it only calls `rule.matches(filepath)`.

This is the Strategy Pattern: algorithms (rules) are interchangeable objects with a common interface (`matches()`). The organizer iterates through rules and applies the first one that matches. This is also an example of **polymorphism** — different objects (FileRule, DateRule) respond to the same method call (`matches()`) in different ways.

### Polymorphism: The OOP Concept That Ties This Together

You've been using polymorphism without naming it. When you call `print(some_object)`, Python calls `some_object.__str__()`. It doesn't matter whether `some_object` is a Student, a Product, or a Habit — `print()` works the same way because all three define `__str__`. That's polymorphism: the same interface, different implementations.

In today's project, the file organizer calls `rule.matches(filepath)` on every rule. It doesn't know or care whether the rule checks extensions, file size, modification date, or filename patterns. Each rule type implements `matches()` its own way. The organizer just asks "does this match?" and acts on the answer.

This is enormously powerful for extensibility. Imagine a client says: "I also want to separate files larger than 100MB into a 'Large Files' folder." You don't touch the organizer. You don't modify any existing rules. You write one new class:

```python
class SizeRule:
    def __init__(self, name, min_bytes, destination):
        self.name = name
        self.min_bytes = min_bytes
        self.destination = destination
    
    def matches(self, filepath: Path) -> bool:
        return filepath.stat().st_size >= self.min_bytes
```

Add it to the rules list, and it works. The organizer's code is unchanged. This is the **Open-Closed Principle**: open for extension (new rules), closed for modification (existing code unchanged). It's one of the most important principles in software architecture.

---

## LECTURE: DRY RUN — PREVIEWING BEFORE ACTING

The dry-run pattern separates **planning** from **execution**. The organizer first produces a **plan** — a list of actions it would take — and only executes after the user confirms.

```python
# A planned action (what WOULD happen)
class PlannedAction:
    def __init__(self, source, destination, rule_name):
        self.source = source            # Where the file is now
        self.destination = destination  # Where it would go
        self.rule_name = rule_name     # Why (which rule matched)
    
    def __str__(self):
        return f"  {self.source.name} → {self.destination.parent.name}/ ({self.rule_name})"
```

The organizer generates a list of `PlannedAction` objects. The presentation layer displays them. The user says "yes, do it." Only then does the organizer execute the moves.

This pattern comes from your world: an Airflow DAG has a "backfill" preview mode that shows which tasks *would* run before actually running them. A Terraform plan shows infrastructure changes before applying them. A database migration tool shows schema changes before executing them. Today you implement the same concept for file operations.

---

## PROJECT 20: `file_organizer.py` (~2 hours)

### The Problem

Build a tool that scans a source directory (like Downloads), classifies each file according to configurable rules, generates a plan showing what would be organized, and — only with user confirmation — executes the moves. It logs every action, handles conflicts (file already exists at destination), and produces a summary report.

### Concepts to Learn and Use

- **`pathlib.Path`** — object-oriented filesystem paths, `glob()`, `iterdir()`, `exists()`, `is_file()`, `mkdir()`, `suffix`, `stem`, `stat()`
- **`shutil.move()`** — moving files between directories
- **`/` operator on Path (operator overloading)** — `__truediv__` in action
- **Strategy Pattern** — rules as objects with a common `matches()` interface
- **Polymorphism** — different rule types responding to the same method
- **Dry-run pattern** — preview before execute, plan as data
- **Conflict resolution** — skip, rename with suffix, or overwrite
- **`logging` module** — pipeline-style observability for file operations
- **`datetime.fromtimestamp()`** — converting file modification time to readable date
- **`Enum` for conflict strategy** — predefined strategies: SKIP, RENAME, OVERWRITE
- **Generator expressions for counting** — `sum(1 for f in dir.iterdir() if f.is_file())`

### Reference Material

- Python docs — `pathlib`: https://docs.python.org/3/library/pathlib.html
- Python docs — `shutil`: https://docs.python.org/3/library/shutil.html
- Python docs — `os`: https://docs.python.org/3/library/os.html
- Python docs — `glob` patterns: https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob
- Real Python — pathlib: https://realpython.com/python-pathlib/
- Real Python — shutil: https://realpython.com/working-with-files-in-python/

### Design Questions (Answer These BEFORE You Code)

1. **What is the flow of the program?**

   ```
   User provides:               Program does:
   ─────────────               ──────────────
   Source directory    →    1. SCAN: Find all files (not directories)
   Destination root   →    2. CLASSIFY: Match each file against rules
   Conflict strategy  →    3. PLAN: Generate list of PlannedActions
                           4. PREVIEW: Display the plan to user
                           5. CONFIRM: User says yes/no
                           6. EXECUTE: Move files, handle conflicts
                           7. REPORT: Summary of what happened
   ```

   Steps 1–4 are the dry run. Step 5 is the gate. Step 6 is irreversible. Step 7 is observability. This structure ensures the user always knows what will happen before it happens.

2. **How do rules compose?**

   Rules are checked in order. The **first matching rule wins.** If a file matches no rule, it goes to a default "Other" category. This means rule order matters — if you have a "Large Files" rule before a "Documents" rule, a 200MB PDF goes to "Large Files," not "Documents." The user controls priority by ordering the rules list.

3. **How does conflict resolution work?**

   When the destination file already exists, the strategy determines behavior:
   
   - **SKIP**: Don't move the file. Log a warning. The original stays where it is.
   - **RENAME**: Add a numeric suffix: `report.pdf` → `report_1.pdf`. If `_1` exists, try `_2`, and so on.
   - **OVERWRITE**: Replace the destination file. Log a warning. The old destination file is gone.

   The conflict strategy is set once for the entire run, not per-file. This is a design choice — per-file decisions would require user input during execution, which breaks automation.

4. **What should the dry-run preview look like?**

   ```
   ┌──────────────────────────────────────────────┐
   │ FILE ORGANIZER — Dry Run Preview             │
   ├──────────────────────────────────────────────┤
   │ Source: /Users/josh/Downloads                │
   │ Destination: /Users/josh/Downloads/Organized │
   │ Conflict strategy: RENAME                    │
   │ Files found: 23                              │
   ├──────────────────────────────────────────────┤
   │ PLANNED MOVES:                               │
   │                                              │
   │ Documents/ (5 files)                         │
   │   report.pdf                                 │
   │   notes.txt                                  │
   │   resume.docx                                │
   │   readme.md                                  │
   │   contract.pdf                               │
   │                                              │
   │ Images/ (8 files)                            │
   │   photo.jpg                                  │
   │   screenshot.png                             │
   │   ... (6 more)                               │
   │                                              │
   │ Code/ (3 files)                              │
   │   script.py                                  │
   │   index.html                                 │
   │   styles.css                                 │
   │                                              │
   │ Other/ (7 files)                             │
   │   unknown.xyz                                │
   │   ... (6 more)                               │
   │                                              │
   │ ⚠ Conflicts: 2 files already exist           │
   │   Documents/report.pdf → will rename to      │
   │                          report_1.pdf        │
   │   Images/photo.jpg → will rename to          │
   │                       photo_1.jpg            │
   └──────────────────────────────────────────────┘
   
   Proceed? (yes/no):
   ```

5. **How to test safely?**

   **Do not run this on your actual Downloads folder first.** Create a test directory with dummy files:
   
   ```bash
   mkdir -p ~/dev/year-1/test_files
   cd ~/dev/year-1/test_files
   touch report.pdf notes.txt photo.jpg screenshot.png script.py data.csv music.mp3 video.mp4 unknown.xyz
   ```
   
   Run your organizer on this test directory. Verify the moves are correct. Only then consider pointing it at a real directory.

### Ask GLM-4.7-Flash Before Coding

`Cmd+L` → "Explain these Python concepts:

1. `pathlib.Path` — how the `/` operator works for joining paths (and that it's actually `__truediv__`), how `glob()` finds files matching patterns, how `stat()` gives file metadata, and how `mkdir(parents=True, exist_ok=True)` creates directories idempotently.

2. `shutil.move()` and `shutil.copy2()` — the difference between moving and copying, why `copy2` preserves metadata, and the gotcha that `shutil.move()` takes strings not Path objects.

3. The Strategy Pattern in Python — how to create interchangeable algorithm objects with a common interface, and why this is better than a long if/elif chain. Use a simple example, not my program.

Explain each concept clearly. Don't write my program."

### Skeletal Structure

```python
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

# ──────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("organizer")


class ConflictStrategy(Enum):
    """What to do when a file already exists at the destination."""
    SKIP = "skip"
    RENAME = "rename"
    OVERWRITE = "overwrite"


# ──────────────────────────────────────
# RULES — the Strategy Pattern
# ──────────────────────────────────────

class FileRule:
    """Classifies files by extension.
    
    This is the Strategy Pattern: each rule is an interchangeable
    algorithm object with a common interface (matches).
    
    The organizer doesn't know or care HOW a rule decides —
    it only calls rule.matches(filepath) and acts on the result.
    """

    def __init__(self, name: str, extensions: list, destination_folder: str):
        self.name = name
        self.extensions = {ext.lower() for ext in extensions}
        self.destination_folder = destination_folder

    def matches(self, filepath: Path) -> bool:
        """Does this rule apply to this file?"""
        # Check if filepath.suffix.lower() is in self.extensions

    def __repr__(self) -> str:
        # "FileRule('Documents' → 'Documents/', 5 extensions)"


class DateRule:
    """Classifies files by modification date into year/month folders.
    
    Demonstrates POLYMORPHISM: DateRule and FileRule have different
    internals but the same interface (matches + destination logic).
    
    A DateRule always matches (every file has a date), so it should
    go LAST in the rules list as a catch-all, or be used as a
    secondary organizer within type folders.
    """

    def __init__(self, name: str = "By Date"):
        self.name = name

    def matches(self, filepath: Path) -> bool:
        """DateRule matches all files — it's a catch-all."""
        return filepath.is_file()

    def get_destination_folder(self, filepath: Path) -> str:
        """Generate destination based on file's modification date.
        Returns something like '2026/03-March'
        """
        mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
        return f"{mod_time.year}/{mod_time.strftime('%m-%B')}"

    def __repr__(self) -> str:
        # "DateRule('By Date' → YYYY/MM-Month)"


class SizeRule:
    """Classifies files by size.
    
    Another example of polymorphism — same interface, different criteria.
    """

    def __init__(self, name: str, min_bytes: int, destination_folder: str):
        self.name = name
        self.min_bytes = min_bytes
        self.destination_folder = destination_folder

    def matches(self, filepath: Path) -> bool:
        """Does this file meet the minimum size threshold?"""
        # Check filepath.stat().st_size >= self.min_bytes

    def __repr__(self) -> str:
        # "SizeRule('Large Files' > 100MB → 'Large/')"


# ──────────────────────────────────────
# PLAN — what WOULD happen (dry run data)
# ──────────────────────────────────────

@dataclass
class PlannedAction:
    """Represents one file move that would be performed.
    
    The plan is a list of these objects. The user reviews the plan.
    Only after confirmation does execution happen.
    """
    source: Path
    destination: Path
    rule_name: str
    conflict: bool = False
    conflict_resolution: str = ""

    def __str__(self) -> str:
        # "report.pdf → Documents/ (Documents rule)"
        # If conflict: "report.pdf → Documents/report_1.pdf (renamed — conflict)"


@dataclass
class ExecutionResult:
    """The outcome of one file move after execution."""
    source: Path
    destination: Path
    success: bool
    action: str        # "moved", "skipped", "renamed", "overwritten", "error"
    error_message: str = ""


# ──────────────────────────────────────
# SCANNER — find files to organize
# ──────────────────────────────────────

class FileScanner:
    """Scans a directory and returns files to organize.
    
    Skips:
      - Directories (we only organize files)
      - Hidden files (starting with '.')
      - The destination directory itself (avoid organizing already-organized files)
    """

    def scan(self, source_dir: Path, exclude_dirs: list = None) -> list:
        """Return list of Path objects for files to organize.
        
        Uses iterdir() — NOT recursive by default.
        Only includes files (is_file()), excludes hidden files.
        """
        # Validate source_dir exists and is a directory
        # Iterate, filter, return list of Paths


# ──────────────────────────────────────
# CLASSIFIER — match files to rules
# ──────────────────────────────────────

class FileClassifier:
    """Applies rules to files and generates a plan.
    
    Rules are checked in order. First match wins.
    Files matching no rule go to a default 'Other' folder.
    """

    def __init__(self, rules: list, default_folder: str = "Other"):
        self.rules = rules
        self.default_folder = default_folder

    def classify(self, filepath: Path) -> tuple:
        """Determine where a file should go.
        Returns: (destination_folder_name, rule_name)
        """
        # Iterate through self.rules
        # Return first match
        # If no match, return (self.default_folder, "Default")

    def generate_plan(self, files: list, source_dir: Path,
                      dest_root: Path, conflict_strategy: ConflictStrategy) -> list:
        """Generate the full move plan as a list of PlannedActions.
        
        For each file:
          1. Classify it (which folder)
          2. Build the destination path
          3. Check for conflicts (destination already exists)
          4. Apply conflict strategy to determine final destination
          5. Create PlannedAction
        """
        # For each file, classify and build PlannedAction
        # Handle conflicts based on strategy
        # Return list of PlannedActions

    def _resolve_conflict(self, dest_path: Path,
                          strategy: ConflictStrategy) -> tuple:
        """Handle a file that already exists at the destination.
        
        SKIP: return (original_path, "skipped")
        RENAME: find next available name (report_1.pdf, report_2.pdf, ...)
        OVERWRITE: return (original_path, "will overwrite")
        """
        # Implement each strategy


# ──────────────────────────────────────
# EXECUTOR — perform the actual moves
# ──────────────────────────────────────

class FileExecutor:
    """Executes a plan by moving files.
    
    This is the ONLY class that touches the real filesystem.
    Everything before this (scan, classify, plan) is read-only.
    This separation means you can test scanning, classification,
    and planning without ever moving a real file.
    """

    def execute(self, plan: list) -> list:
        """Execute all planned actions.
        Returns: list of ExecutionResult
        """
        results = []
        for action in plan:
            result = self._execute_one(action)
            results.append(result)
        return results

    def _execute_one(self, action: PlannedAction) -> ExecutionResult:
        """Move one file. Handle errors gracefully.
        
        Creates destination directory if it doesn't exist.
        Logs every action.
        Returns ExecutionResult with success/failure status.
        """
        # Create parent directory: action.destination.parent.mkdir(...)
        # Try to move: shutil.move(str(action.source), str(action.destination))
        # Log success or error
        # Return ExecutionResult


# ──────────────────────────────────────
# REPORTER — summarize what happened
# ──────────────────────────────────────

class OrganizeReport:
    """Generates a summary report from execution results."""

    def generate(self, results: list) -> dict:
        """Build a summary dictionary from results.
        
        Counts: total, moved, skipped, renamed, errors
        Groups files by destination folder for display.
        """
        # Count each action type
        # Group by destination folder
        # Return summary dict

    def display(self, summary: dict) -> None:
        """Print a formatted summary to the console."""
        # Formatted output with counts and categories


# ──────────────────────────────────────
# ORCHESTRATOR — ties everything together
# ──────────────────────────────────────

class FileOrganizer:
    """The main organizer that composes all components.
    
    Architecture:
      Scanner → Classifier → Plan → [Preview] → Executor → Reporter
    
    Note the similarity to the ETL pipeline from Day 8:
      Extract → Transform → Validate → [Preview] → Load → Report
    
    The pattern is the same. The domain is different.
    """

    DEFAULT_RULES = [
        FileRule("Documents", [".pdf", ".doc", ".docx", ".txt", ".rtf", ".md", ".odt"], "Documents"),
        FileRule("Images", [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp", ".ico"], "Images"),
        FileRule("Code", [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs", ".sh"], "Code"),
        FileRule("Data", [".csv", ".json", ".xml", ".yaml", ".yml", ".sql", ".db"], "Data"),
        FileRule("Spreadsheets", [".xlsx", ".xls", ".ods"], "Spreadsheets"),
        FileRule("Archives", [".zip", ".tar", ".gz", ".7z", ".rar", ".bz2"], "Archives"),
        FileRule("Music", [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"], "Music"),
        FileRule("Videos", [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".webm"], "Videos"),
    ]

    def __init__(self, rules: list = None,
                 conflict_strategy: ConflictStrategy = ConflictStrategy.RENAME):
        self.scanner = FileScanner()
        self.classifier = FileClassifier(rules or self.DEFAULT_RULES)
        self.executor = FileExecutor()
        self.reporter = OrganizeReport()
        self.conflict_strategy = conflict_strategy

    def organize(self, source_dir: Path, dest_root: Path = None,
                 dry_run: bool = True) -> None:
        """Main entry point.
        
        If dry_run=True (default): show preview only, don't move files.
        If dry_run=False: show preview, ask for confirmation, then execute.
        """
        dest_root = dest_root or (source_dir / "Organized")

        logger.info(f"Scanning: {source_dir}")
        files = self.scanner.scan(source_dir, exclude_dirs=[dest_root])

        if not files:
            print("No files found to organize.")
            return

        logger.info(f"Classifying {len(files)} files")
        plan = self.classifier.generate_plan(
            files, source_dir, dest_root, self.conflict_strategy
        )

        # Display preview
        self._display_preview(plan, source_dir, dest_root)

        if dry_run:
            print("\n[DRY RUN] No files were moved.")
            print("Run with dry_run=False to execute.")
            return

        # Confirm with user
        confirm = input("\nProceed with organizing? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Cancelled.")
            return

        # Execute
        logger.info("Executing plan...")
        results = self.executor.execute(plan)

        # Report
        summary = self.reporter.generate(results)
        self.reporter.display(summary)

    def _display_preview(self, plan: list, source_dir: Path, dest_root: Path) -> None:
        """Show the dry-run preview grouped by destination folder."""
        # Group PlannedActions by destination folder
        # Display in the formatted preview style
        # Highlight conflicts


# ──────────────────────────────────────
# CLI INTERFACE
# ──────────────────────────────────────

def main():
    """Command-line interface for the file organizer.
    
    Usage examples:
      python3 file_organizer.py ~/Downloads                    # Dry run (preview only)
      python3 file_organizer.py ~/Downloads --execute          # Execute moves
      python3 file_organizer.py ~/Downloads --strategy skip    # Skip conflicts
    
    For today, a simple interactive version is fine.
    argparse integration is a bonus.
    """
    print("=== File Organizer ===\n")

    source = input("Source directory (or press Enter for test_files): ").strip()
    source_dir = Path(source) if source else Path.home() / "dev" / "year-1" / "test_files"

    if not source_dir.exists():
        print(f"Directory not found: {source_dir}")
        return

    # Ask about conflict strategy
    print("\nConflict strategy:")
    print("  1. Rename (add _1, _2, etc.)")
    print("  2. Skip (leave in place)")
    print("  3. Overwrite (replace existing)")
    choice = input("Choose (1/2/3, default 1): ").strip() or "1"

    strategies = {"1": ConflictStrategy.RENAME, "2": ConflictStrategy.SKIP, "3": ConflictStrategy.OVERWRITE}
    strategy = strategies.get(choice, ConflictStrategy.RENAME)

    # Ask dry run or execute
    mode = input("\nMode: (1) Preview only  (2) Execute: ").strip() or "1"
    dry_run = mode != "2"

    organizer = FileOrganizer(conflict_strategy=strategy)
    organizer.organize(source_dir, dry_run=dry_run)


if __name__ == "__main__":
    main()
```

### Create Your Test Environment

Before writing any code, set up safe test data:

```bash
# Create test directory with dummy files
mkdir -p ~/dev/year-1/test_files
cd ~/dev/year-1/test_files

# Create dummy files of different types
touch report.pdf notes.txt resume.docx readme.md
touch photo.jpg screenshot.png logo.svg banner.webp
touch script.py index.html styles.css app.js
touch data.csv config.json database.sql
touch song.mp3 podcast.wav
touch movie.mp4 clip.mov
touch archive.zip backup.tar.gz
touch mystery.xyz unknown.abc

# Create a conflict: a file that already exists at destination
mkdir -p Organized/Documents
touch Organized/Documents/report.pdf

echo "Test environment ready. $(ls -1 | wc -l) files created."
```

Run your organizer in dry-run mode first. Verify the preview is correct. Then run in execute mode and verify files moved to the right places.

### Verify the Architecture

After building, trace the flow to verify separation of concerns:

| Component | Touches Filesystem? | What It Does |
|-----------|-------------------|--------------|
| `FileRule` / `DateRule` / `SizeRule` | Read-only (stat) | Classifies files — pure logic |
| `FileScanner` | Read-only (iterdir) | Lists files — no modifications |
| `FileClassifier` | No | Generates plan — pure logic |
| `PlannedAction` | No | Data object — the plan |
| `FileExecutor` | **Yes — moves files** | The only destructive component |
| `OrganizeReport` | No | Summarizes results — pure logic |
| `FileOrganizer` | No | Composes everything — orchestration |

Only `FileExecutor` modifies the filesystem. Everything else is either read-only or pure logic. This means you can test classification, planning, and reporting without touching any real files. The irreversible action is isolated to one small, focused class.

### Ask GLM-4.7-Flash After Coding — The Review Step

Select all code → `Cmd+L` →

"Review this file organizer as a senior developer. Specifically evaluate:

1. Is the Strategy Pattern properly implemented? Can I add a new rule type (like DateRule or SizeRule) without modifying the FileClassifier?
2. Is filesystem interaction properly isolated to the FileExecutor? Could I test the scanner, classifier, and planner without moving real files?
3. Is my conflict resolution logic correct? Am I handling the rename suffix incrementing properly (report_1.pdf, report_2.pdf, ...)?
4. Is my dry-run preview informative enough for a user to make a confident yes/no decision?
5. Am I using pathlib idiomatically? Am I accidentally using string operations where pathlib methods would be better?
6. What edge cases am I missing? (Empty directories, permission errors, symbolic links, files modified during execution, very long filenames?)
7. What would a senior developer change?"

**Read the suggestions. Implement the changes yourself. Commit the improved version.**

```bash
git add . && git commit -m "Project 20: file_organizer.py — Strategy pattern, pathlib, shutil, dry-run preview, conflict resolution"
```

---

## CLOSING LECTURE: TWO WEEKS OF FOUNDATION

Today is the last weeknight project of Week 2. Let me place the last 13 days in perspective.

**Week 1** built your Python vocabulary and introduced architecture. You learned how to make Python do things — write functions, create classes, handle files, sort data. By Day 8, you were building ETL pipelines.

**Week 2** built your Python judgment. Each project introduced a design principle that goes beyond syntax:

| Day | Project | Design Principle |
|-----|---------|-----------------|
| 9 | Recipe Manager | Composition over inheritance; nested serialization |
| 10 | Habit Tracker | Event sourcing; computed properties; date arithmetic |
| 11 | Inventory System | Business rule enforcement; comparison operators; property setters |
| 12 | Student Gradebook | Many-to-many relationships; mediator pattern; weighted averages |
| **13** | **File Organizer** | **Strategy pattern; dry-run previews; irreversibility awareness** |

Each project was more architecturally sophisticated than the last. And each principle you learned will appear in your AI-directed work next week. When you write a spec in Week 3, you'll say things like: "Use the Strategy Pattern for document classifiers. Use composition for the entity model. Use a mediator for the many-to-many relationship between users and documents. Enforce data validity through property setters."

AI can generate the *implementation* of each pattern. It cannot decide *which pattern to use where*. That's architectural judgment — the skill these two weeks built.

**Tomorrow and Sunday** are the last Foundation phase weekend. You'll build a workout logger with matplotlib charts (your first data visualization) and a comprehensive reading list tracker. Then Week 3 begins — the shift to AI-directed development where you architect, AI implements, and you review.

You're ready for it.

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 13
- [ ] Day number: 13
- [ ] Hours coded: 2
- [ ] Projects completed: 1 (file_organizer)
- [ ] Key concepts: pathlib, shutil, Strategy pattern, polymorphism, dry-run preview, conflict resolution, operator overloading (__truediv__), Open-Closed Principle
- [ ] AI review: What was the most useful suggestion? What change did you make?
- [ ] Mood/energy (1–5): ___

### Preview tomorrow (Day 14 — Saturday, Weekend Session):
- **Morning (8:00–11:00 AM)**: 3 hours
  - `workout_logger.py` — Exercise tracking with progress charts
  - **New concept**: `matplotlib` — your first data visualization library. Turning data into pictures.
  - **OOP focus**: Objects that generate their own visual representations

### Preview Sunday (Day 15):
- **Morning (8:00–11:00 AM)**: 3 hours
  - `reading_list.py` — Comprehensive book tracker with ratings, recommendations, export
  - **This is the Week 2 capstone** — pulls together everything: composition, serialization, sorting, filtering, search, formatted output

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

1. **`pathlib.Path`** — object-oriented filesystem paths: `/` joins paths (via `__truediv__`), `glob()` finds patterns, `stat()` gives metadata, `mkdir(parents=True, exist_ok=True)` creates directories idempotently
2. **`shutil.move()` and `shutil.copy2()`** — moving and copying files, and why `move` takes strings not Path objects
3. **Strategy Pattern** — interchangeable algorithm objects with a common interface, replacing long if/elif chains
4. **Polymorphism** — different classes (FileRule, DateRule, SizeRule) responding to the same method call (`matches()`) in different ways
5. **Operator overloading** — `__truediv__` on Path making `/` join paths, the same mechanism as `__lt__` for comparison
6. **Open-Closed Principle** — code that's open for extension (new rules) but closed for modification (existing code unchanged)
7. **Dry-run pattern** — preview before execute, separating planning from action for irreversible operations
8. **Conflict resolution strategies** — SKIP, RENAME, OVERWRITE as an Enum, applied systematically
9. **Isolating destructive operations** — only FileExecutor touches the filesystem; everything else is read-only or pure logic
10. **Idempotency in filesystem operations** — `mkdir(exist_ok=True)` creates safely, inspired by the same principle in ETL pipelines

---

**Day 13 of 365. Last weeknight of Week 2. Your programs no longer just manage data — they act on the real world. Carefully.** 🚀
