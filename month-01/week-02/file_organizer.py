import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import textwrap

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
        return filepath.suffix.lower() in self.extensions

    def __repr__(self) -> str:
        # "FileRule('Documents' → 'Documents/', 5 extensions)"
        return f"FileRule('{self.name}' → '{self.destination_folder}', {len(self.extensions)})"


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
        return f"DateRule('{self.name}' → YYYY/MM-Month)"


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
        return filepath.stat().st_size >= self.min_bytes

    def __repr__(self) -> str:
        # "SizeRule('Large Files' > 100MB → 'Large/')"
        return f"SizeRule('{self.name}' > {self.min_bytes} → '{self.destination_folder}')"

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
        if self.conflict:
            return f"{self.source} → {self.destination} (renamed — conflict)"
        else:
            return f"{self.source} → {self.destination} (Documents rule)"


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
        if not source_dir.is_dir():
            raise ValueError(f"{source_dir} is not a directory")
        exclude_dirs = exclude_dirs or []
        files_to_organize = []
        for item in source_dir.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                files_to_organize.append(item)
        return files_to_organize


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
        for rule in self.rules:
            if rule.matches(filepath):
                return (rule.destination_folder, rule.name)
        return (self.default_folder, "Default")
        

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
        # Implement conflict resolution logic
        # Implement logic to handle each strategy
        planned_actions = []
        for file in files:
            destination_folder, rule_name = self.classify(file)
            destination_path = dest_root / destination_folder / file.name
            if destination_path.exists():
                resolved_path, resolution = self._resolve_conflict(destination_path, conflict_strategy)
                planned_action = PlannedAction(
                    source=file, 
                    destination=resolved_path, 
                    rule_name=rule_name,
                    conflict=True,
                    conflict_resolution=resolution
                )
                planned_actions.append(planned_action)
            else:
                planned_action = PlannedAction(
                    source=file, 
                    destination=destination_path,
                    rule_name=rule_name,
                    conflict=False,
                    conflict_resolution=""
                )
                planned_actions.append(planned_action)
        return planned_actions

    def _resolve_conflict(self, dest_path: Path,
                          strategy: ConflictStrategy) -> tuple:
        """Handle a file that already exists at the destination.
        
        SKIP: return (original_path, "skipped")
        RENAME: find next available name (report_1.pdf, report_2.pdf, ...)
        OVERWRITE: return (original_path, "will overwrite")
        """
        # Implement each strategy
        if strategy == ConflictStrategy.SKIP:
            return (dest_path, "skipped")
        elif strategy == ConflictStrategy.RENAME:
            # Implement logic to find next available name
            # Return new path and "renamed"
            i = 1
            while True:
                new_path = dest_path.with_stem(f"{dest_path.stem}_{i}")
                if not new_path.exists():
                    return (new_path, "renamed")
                i += 1
        elif strategy == ConflictStrategy.OVERWRITE:
            return (dest_path, "will overwrite")



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
        summary = {
            "total": len(results),
            "moved": sum(1 for r in results if r.success),
            "skipped": sum(1 for r in results if not r.success),
            "renamed": sum(1 for r in results if r.success and r.action.type == "rename"),
            "errors": sum(1 for r in results if r.error),
            "by_folder": {}
        }
        return summary

    def display(self, summary: dict) -> None:
        """Print a formatted summary to the console."""
        # Formatted output with counts and categories
        print(f"Total files: {summary['total']}")
        print(f"Moved: {summary['moved']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Renamed: {summary['renamed']}")
        if summary["errors"]:
            print(f"Errors: {summary['errors']}")
        return


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
        # Group by destination folder
        by_folder = {}
        conflicts = []
        for action in plan:
            folder = action.destination.parent.name
            if folder not in by_folder:
                by_folder[folder] = []
            by_folder[folder].append(action)
            
            if action.conflict:
                conflicts.append(action)
        
        # Display formatted preview
        print(f"\n{'=' * 60}")
        print(f"FILE ORGANIZER — Dry Run Preview")
        print(f"{'=' * 60}")
        print(f"Source: {source_dir}")
        print(f"Destination: {dest_root}")
        print(f"Conflict strategy: {self.conflict_strategy.name}")
        print(f"Total files: {len(plan)}")
        print(f"{'=' * 60}\n")

        for folder, actions in sorted(by_folder.items()):
            print(f"{folder}/ ({len(actions)} files)")
            for action in actions[:5]:  # Show up to 5 per folder
                conflict_marker = " ⚠ RENAMED" if action.conflict else ""
                print(f"  {action.source.name} → {action.destination.name}{conflict_marker}")
            if len(actions) > 5:
                print(f"  ... and {len(actions) - 5} more")
        print()
    
        if conflicts:
            print(f"{'=' * 60}")
            print(f"⚠ CONFLICTS: {len(conflicts)} files will be renamed")
            for action in conflicts[:3]:  # Show first 3
                print(f"  {action.source.name} → {action.destination.name}")
            if len(conflicts) > 3:
                print(f"  ... and {len(conflicts) - 3} more")
            print()
        
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