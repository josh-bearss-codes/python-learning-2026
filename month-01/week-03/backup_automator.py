import sqlite3
import hashlib
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Configuration defaults
DEFAULT_SOURCE = Path.home() / "documents"
DEFAULT_DEST = Path.home() / "backups"
DEFAULT_DB = Path("backup_history.db")
CHUNK_SIZE = 8192   # 8KB chunks for file hashing

# Patterns to skip during scanning
SKIP_PATTERNS = {".git", "__pycache__", ".DS_Store", "node_modules", ".venv"}

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")
logger = logging.getLogger(__name__)


# ──────────────────────────────────────
# FILE UTILITIES
# ──────────────────────────────────────

def compute_file_hash(filepath: Path, algorithm: str = "sha256") -> str:
    """Compute SHA-256 hash of a file's contents.
    
    Reads in CHUNK_SIZE chunks to handle large files
    without loading the entire file into memory.
    
    Returns the hex digest string (64 characters for SHA-256).
    """
    # Create hasher
    # Read file in binary mode, chunk by chunk
    # Return hex digest
    hasher = hashlib.new(algorithm)
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                if not chunk:
                    break
                hasher.update(chunk)
            return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error computing hash for {filepath}: {e}")
        return None

def human_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format.
    
    Examples:
        human_size(1024)       → "1.0 KB"
        human_size(1048576)    → "1.0 MB"
        human_size(5368709120) → "5.0 GB"
    """
    # Loop through units: B, KB, MB, GB, TB
    # Divide by 1024 until the number is < 1024
    # Return formatted string
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} {units[-1]}"

def should_skip(filepath: Path) -> bool:
    """Check if a file should be excluded from backup.
    
    Skip if any parent directory matches SKIP_PATTERNS.
    For example, anything inside .git/ or __pycache__/ is skipped.
    """
    # Skip hidden files/dirs (starting with .) — but allow .gitignore, etc. if desired
    for part in filepath.parts:
        if part.startswith('.') and part not in {'.gitignore', '.env'}:
            return True
    # Explicit patterns
    if any(part in SKIP_PATTERNS for part in filepath.parts):
        return True
    return False

# ──────────────────────────────────────
# DATA LAYER — Backup history database
# ──────────────────────────────────────

class BackupDatabase:
    """SQLite database tracking backup runs and file states.
    
    Two tables:
      backup_runs — one row per backup execution
      file_records — one row per tracked file, stores hash + mtime
    
    This applies Day 19's SQLite skills to a real automation problem.
    """

    def __init__(self, db_path: Path = DEFAULT_DB):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create connection with foreign keys enabled and row factory set."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if they don't exist.
        
        backup_runs:
          id, timestamp, source_dir, dest_dir,
          files_backed_up, files_skipped, bytes_copied
        
        file_records:
          id, filepath (TEXT UNIQUE), file_hash, file_size, mtime,
          last_backup_run (FK → backup_runs.id)
        
        Note: filepath is UNIQUE in file_records because each file
        appears only once — we UPDATE its hash/mtime on each backup,
        not INSERT a new row.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS backup_runs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                            source_dir TEXT NOT NULL,
                            dest_dir TEXT NOT NULL,
                            files_backed_up INTEGER NOT NULL DEFAULT 0,
                            files_skipped INTEGER NOT NULL DEFAULT 0,
                            bytes_copied INTEGER NOT NULL DEFAULT 0
                        );
                        """
            )
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS file_records (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            filepath TEXT UNIQUE NOT NULL,
                            file_hash TEXT NOT NULL,
                            file_size INTEGER NOT NULL,
                            mtime REAL NOT NULL,
                            last_backup_run INTEGER NOT NULL,
                            FOREIGN KEY (last_backup_run) REFERENCES backup_runs(id)
                        );
                        """
            )
            conn.commit()
        except sqlite3.Error as e: 
            logger.error(f"Error creating tables: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise e
        finally:
            conn.close()
        
    def start_run(self, source_dir: str, dest_dir: str) -> int:
        """Record the start of a backup run.
        
        Inserts a new row in backup_runs with zero counts.
        Returns the new run's ID.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO backup_runs DEFAULT VALUES")
            run_id = cursor.lastrowid 
            cursor.execute("UPDATE backup_runs SET source_dir = ?, dest_dir = ? WHERE id = ?", (source_dir, dest_dir, run_id))
            conn.commit()
            return run_id
        
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Error starting backup run: {e}")
        except Exception as e:
            conn.rollback()
            logger.error(f"Unexpected error: {e}")
        finally:
            conn.close()

    def complete_run(self, run_id: int, files_backed_up: int,
                     files_skipped: int, bytes_copied: int):
        """Update a backup run with final statistics."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE backup_runs SET files_backed_up = ?, files_skipped = ?, bytes_copied = ? WHERE id = ?", (files_backed_up, files_skipped, bytes_copied, run_id))
            conn.commit()
            return run_id
    
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Error completing backup run: {e}")
        except Exception as e:
            conn.rollback()
            logger.error(f"Unexpected error: {e}")
        finally:
            conn.close()

    def get_file_record(self, filepath: str) -> dict:
        """Get the stored hash and mtime for a file.
        
        Returns dict with 'file_hash', 'mtime', 'file_size'
        or None if the file has never been backed up.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT file_hash, mtime, file_size FROM file_records WHERE filepath = ?", (filepath,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Error fetching file record for {filepath}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching file record for {filepath}: {e}")
            return None
        finally:
            conn.close()

    def update_file_record(self, filepath: str, file_hash: str,
                           file_size: int, mtime: float, run_id: int):
        """Insert or update a file's record after backing it up.
        
        Uses INSERT OR REPLACE (SQLite upsert) since filepath is UNIQUE.
        This means:
          - New file → INSERT a new row
          - Existing file → REPLACE the row with updated hash/mtime
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO file_records (filepath, file_hash, file_size, mtime, last_backup_run) VALUES ( ?, ?, ?, ?, ?) 
                """,
                (filepath, file_hash, file_size, mtime, run_id))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Unexpected error updating file record for {filepath}: {e}")
            return None
        except Exception as e:
            conn.rollback()
            logger.error(f"Unexpected error updating file record for {filepath}: {e}")
            return None
        finally:
            conn.close()

    def get_last_run(self) -> dict:
        """Get the most recent backup run, or None."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM backup_runs ORDER BY timestamp DESC LIMIT 1
                """
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                return None
            
        except sqlite3.Error as e:
            logger.error(f"Unexpected error getting last run: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting last run: {e}")
            return None
        finally:
            conn.close()

    def get_run_history(self, limit: int = 10) -> list:
        """Get recent backup runs, most recent first."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM backup_runs ORDER BY timestamp DESC
                """
            )
            rows = cursor.fetchmany(limit)
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Unexpected error getting run history: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting run history: {e}")
            return None
        finally:
            conn.close()

    def get_backed_up_files(self, run_id: int) -> list:
        """Get all files that were backed up in a specific run."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM file_records WHERE last_backup_run = ? ORDER BY filepath ASC 
                """, (run_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Unexpected error getting backed up files for run {run_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting backed up files for run {run_id}: {e}")
            return None
        finally:
            conn.close()

    def get_stats(self) -> dict:
        """Overall backup statistics.
        
        Returns: total_runs, total_files_tracked, total_bytes_copied,
        last_run_timestamp, oldest_file_backup
        """
        queries = {
            "total_runs": "SELECT COUNT(*) FROM backup_runs",
            "total_files_tracked": "SELECT COUNT(*) FROM file_records",
            "total_bytes_copied": "SELECT SUM(bytes_copied) from backup_runs",
            "last_run_timestamp": "SELECT MAX(timestamp) FROM backup_runs",
            "oldest_file_backup": "SELECT MIN(timestamp) FROM backup_runs"
        }
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            results = {}
            for label, sql in queries.items():
                cursor.execute(sql)
                results[label] = cursor.fetchone()[0]
            return results
            
        except sqlite3.Error as e:
            logger.error(f"Error executing query for {queries}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
        finally:
            conn.close()

# ──────────────────────────────────────
# BUSINESS LOGIC — The backup engine
# ──────────────────────────────────────

class BackupEngine:
    """Performs incremental file backups with change detection.
    
    Algorithm:
      1. Scan source directory for all files (recursive)
      2. For each file:
         a. Check mtime against database record
         b. If mtime unchanged → skip (file not modified)
         c. If mtime changed → compute hash, compare to stored hash
         d. If hash changed → copy file to destination, update record
         e. If hash same → skip (mtime changed but content didn't)
         f. If no record exists → new file, copy and create record
      3. Record the backup run in the database
    
    This two-tier check (mtime first, hash second) balances speed
    and accuracy. Most files won't need hashing because their
    mtime hasn't changed.
    """

    def __init__(self, source_dir: Path, dest_dir: Path,
                 db: BackupDatabase = None):
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.db = db or BackupDatabase()

    def run_backup(self) -> dict:
        """Execute a full incremental backup.
        
        Returns a summary dict:
            {
                "files_backed_up": 12,
                "files_skipped": 988,
                "bytes_copied": 4567890,
                "new_files": 3,
                "changed_files": 9,
                "duration_seconds": 14.2,
                "run_id": 5
            }
        """
        # Validate source exists
        # Create destination if needed
        # Start a backup run in the database
        # Scan source directory
        # Process each file
        # Complete the run record
        # Return summary
        """
        "Scanning /Users/josh/documents..."
          "Found 1,247 files"
          "Backing up: notes/todo.txt (2.4 KB) [new]"
          "Backing up: projects/app/main.py (8.1 KB) [changed]"
          "Skipping: resume.pdf [unchanged]"
          "..."
        """
        if self.source_dir.exists():
            self.dest_dir.mkdir(parents=True, exist_ok=True)
            start = datetime.now()
            run_id = self.db.start_run(self.source_dir, self.dest_dir)
            print(f"Scanning source dir {self.source_dir}")
            print(f"Found {len(self.source_dir.rglob('*'))} files")
            for file in self.source_dir.rglob("*"):
                size = human_size(file.stat().st_size)
                if file.is_file():
                    result = self._process_file(file, run_id)
                    if result == "backed_up":
                        if file.__new__:
                            print(f"Backing up: {file} {size} [new]")
                            self.new_files += 1
                            print
                        else:
                            print(f"Backing up: {file} {size} [changed]")
                            self.changed_files += 1
                        self.files_backed_up += 1
                        self.bytes_copied += size
                        filepath = str(file.parent / file.name)
                        self.db.update_file_record(filepath, compute_file_hash(file), size, file.stat().st_mtime, run_id)
                    elif result == "skipped_unchanged":
                        print(f"Skipping unchanged file {file} in {self.source}")
                        self.files_skipped += 1
                        self.bytes_skipped += size
                    elif result == "skipped_excluded":
                        self.files_skipped += 1
                        self.bytes_skipped += size
            self.db.complete_run(run_id, self.files_backed_up, self.files_skipped, self.bytes_copied)
            end = datetime.now()
            self.duration_seconds = (end - start).total_seconds
            return {
                "files_backed_up": self.files_backed_up,
                "files_skipped": self.files_skipped,
                "bytes_copied": self.bytes_copied,
                "new_files": self.new_files,
                "changed_files": self.changed_files,
                "duration_seconds": self.duration_seconds,
                "run_id": run_id
            }
        else:
            logger.info("Backup run already in progress. Skipping.")


    def _process_file(self, filepath: Path, run_id: int) -> str:
        """Process one file: decide whether to back it up.
        
        Returns one of: "backed_up", "skipped_unchanged", "skipped_excluded"
        
        The two-tier change detection algorithm:
          1. Check if file should be excluded (SKIP_PATTERNS)
          2. Get the file's current mtime from stat()
          3. Look up the file's record in the database
          4. If no record → new file → copy and record
          5. If mtime unchanged → skip
          6. If mtime changed → compute hash
          7. If hash changed → copy and update record
          8. If hash same → update mtime in record, skip copy
        """
        if should_skip(filepath):
            return "skipped_excluded"

        current_mtime = filepath.stat().st_mtime
        record = self.db.get_file_record(str(filepath))  # ← must convert to str

        if record is None:
            # New file
            self._copy_file(filepath)
            self.db.update_file_record(
                str(filepath),
                compute_file_hash(filepath),
                filepath.stat().st_size,  # ← bytes, not human_size()
                current_mtime,
                run_id
            )
            return "backed_up"

        # mtime changed → hash check required
        if record["mtime"] != current_mtime:
            current_hash = compute_file_hash(filepath)
            if current_hash != record["file_hash"]:
                # Content changed → copy
                self._copy_file(filepath)
                self.db.update_file_record(
                    str(filepath),
                    current_hash,
                    filepath.stat().st_size,
                    current_mtime,
                    run_id
                )
                return "backed_up"
            else:
                # Only mtime changed (e.g., touch), no copy needed
                self.db.update_file_record(
                    str(filepath),
                    record["file_hash"],
                    record["file_size"],
                    current_mtime,
                    run_id
                )
                return "skipped_unchanged"
        else:
            # mtime unchanged → skip (no hash needed)
            return "skipped_unchanged"

    def _copy_file(self, source_file: Path) -> int:
        """Copy a file from source to destination, preserving structure.
        
        Uses relative_to() to compute the backup path.
        Creates parent directories as needed.
        Uses shutil.copy2 to preserve metadata.
        
        Returns the file size in bytes.
        """
        relative = source_file.relative_to(self.source_dir)
        dest_file = self.dest_dir / relative
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, dest_file)
        return source_file.stat().st_size

    def _scan_files(self) -> list:
        """Scan source directory for all files, excluding skip patterns.
        
        Returns a list of Path objects for all files to consider.
        Logs: "Found {count} files in {source_dir}"
        """
        # rglob("*"), filter is_file(), filter should_skip()
        count = 0
        file_list = []
        for file in self.source_dir.rglob("*"):
            if file.is_file() and not should_skip(file):
                count += 1
                file_list.append(file.parent / file.name)
        logger.info(f"Found {count} files in {self.source_dir}")
        return file_list                

    def should_run(self, interval_hours: int = 24) -> bool:
        """Check if enough time has passed since the last backup.
        
        Returns True if no backup exists or if more than
        interval_hours have elapsed since the last run.
        """
        last_backup = self.db.get_last_run()
        if not last_backup:
            return True
        elif (datetime.today() - last_backup) > timedelta(hours=interval_hours):
            return True
        else:
            return False


# ──────────────────────────────────────
# PRESENTATION
# ──────────────────────────────────────

class BackupApp:
    """Terminal interface for the backup automator."""

    def __init__(self):
        self.engine = None   # Created when user specifies directories

    def run(self):
        """Main menu loop."""
        while True:
            print("\n--- Backup Automator ---")
            print("1. Run backup now")
            print("2. Check if backup needed")
            print("3. View backup history")
            print("4. View last backup details")
            print("5. View statistics")
            print("6. Configure source/destination")
            print("7. Dry run (show what would be backed up)")
            print("8. Quit")

            choice = input("\nChoose: ").strip()
            # Route to methods
            if choice == "1":
                self.run_backup_prompt()
            elif choice == "2":
                self.check_backup_needed_prompt()
            elif choice == "3":
                self.history_prompt()
            elif choice == "4":
                self.last_backup_prompt()
            elif choice == "5":
                self.stats_prompt()
            elif choice == "6":
                self.configure_prompt()
            elif choice == "7":
                self.dry_run_prompt()
            elif choice == "8":
                break
            else:
                print("Invalid choice. Please try again.")

    def configure_prompt(self):
        """Set source and destination directories.
        
        Validate that source exists and is a directory.
        Create destination if it doesn't exist (with confirmation).
        Initialize the BackupEngine with the chosen paths.
        """
        print("Configure backup paths")
        source_dir = input("Enter source directory: ")
        destination_dir = input("Enter destination directory: ")
        if not Path(source_dir).is_dir():
            print("Source directory does not exist or is not a directory.")
            return 
        if not Path(destination_dir).exists():
            print("Destination directory does not exist. Creating...")
            if not input("Create directory? (y/n): ").lower().startswith('y'):
                return 
            Path(destination_dir).mkdir(parents=True, exist_ok=True)
        self.engine = BackupEngine(source_dir, destination_dir)
        print("Backup paths configured successfully.")
        return

    def run_backup_prompt(self):
        """Execute a backup and display the summary.
        
        Shows progress during backup:
          "Scanning /Users/josh/documents..."
          "Found 1,247 files"
          "Backing up: notes/todo.txt (2.4 KB) [new]"
          "Backing up: projects/app/main.py (8.1 KB) [changed]"
          "Skipping: resume.pdf [unchanged]"
          "..."
          "Backup complete: 12 files backed up, 1,235 skipped"
          "Total copied: 156.3 KB in 3.2 seconds"
        """
        summary = self.engine.run_backup()  
        """
        return {
                "files_backed_up": self.files_backed_up,
                "files_skipped": self.files_skipped,
                "bytes_copied": self.bytes_copied,
                "new_files": self.new_files,
                "changed_files": self.changed_files,
                "duration_seconds": self.duration_seconds,
                "run_id": run_id
            }
        """
        print("...")
        print("Backup complete. Summary:")
        print(f"Backed up {summary['files_backed_up']} files, {summary['files_skipped']} skipped")
        print(f"Total copied: {summary['bytes_copied']} in {summary['duration_seconds']} seconds")

    def dry_run_prompt(self):
        """Show what WOULD be backed up without actually copying.
        
        Same logic as run_backup but skip the copy step.
        Display: which files would be backed up and why (new/changed).
        This is the 'preview before commit' pattern from Day 13.
        """
        print("Dry run complete. Summary:")
        print("Would have backed up the following files:")
        for file in self.engine.source_dir.glob("**/*"):
            result = self.engine._process_file(file)
            if result:
                print(f"  {file}: {result}")
                print(f"    Reason: {result}")
            else:
                print(f"  {file}: Not backed up because {result}")
                print(f"    Reason: {result}")
        

    def history_prompt(self):
        """Display recent backup runs.
        
            CREATE TABLE IF NOT EXISTS backup_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                source_dir TEXT NOT NULL,
                dest_dir TEXT NOT NULL,
                files_backed_up INTEGER NOT NULL DEFAULT 0,
                files_skipped INTEGER NOT NULL DEFAULT 0,
                bytes_copied INTEGER NOT NULL DEFAULT 0
            );

        ┌────┬─────────────────────┬──────────┬─────────┬────────────┐
        │ #  │ Timestamp           │ Backed Up│ Skipped │ Size       │
        ├────┼─────────────────────┼──────────┼─────────┼────────────┤
        │  5 │ 2026-03-22 09:15:00 │       12 │   1,235 │ 156.3 KB   │
        │  4 │ 2026-03-21 09:00:00 │        3 │   1,244 │  24.1 KB   │
        │  3 │ 2026-03-20 08:45:00 │       47 │   1,200 │   2.1 MB   │
        └────┴─────────────────────┴──────────┴─────────┴────────────┘
        """
        history = self.engine.db.get_run_history()
        print("Recent Backup Runs:")
        for run in history:
            print(f"-" * 40)
            print(f"| # | Timestamp | Backed Up | Skipped | Size |")
            print(f"| {run['id']} | {run['timestamp']} | {run['backed_up']} | {run['skipped']} | {run['size']} |")
            print("-" * 40)


    def last_backup_prompt(self):
        """Show details of the most recent backup.
        
        Which files were backed up, their sizes, and why (new/changed).
        """
        last_run = self.engine.db.get_last_run()
        print("Most Recent Backup:")
        for file in last_run['files']:
            print(f"-" * 40)
            print(f"| File | Size | Reason |")
            print(f"| {file['name']} | {file['size']} | {file['reason']} |")
            print("-" * 40)


    def stats_prompt(self):
        """Display overall backup statistics.
        
        Total backup runs: 5
        Total files tracked: 1,247
        Total data backed up: 12.4 MB
        Last backup: 2026-03-22 09:15:00 (2 hours ago)
        Average files per backup: 15
        """
        print("Backup Statistics:")
        stats = self.engine.db.get_stats()
        print(f"Total backup runs: {stats['total_runs']}")
        print(f"Total files tracked: {stats['total_files']}")
        print(f"Total data backed up: {human_size(stats['total_bytes_copied'])}")
        print(f"Last backup: {stats['last_run_timestamp']}")
        print(f"Average files per backup: {stats['avg_files']}")

    def check_backup_needed_prompt(self):
        """Check if a backup is due.
        
        "Last backup: 2026-03-21 09:00:00 (26 hours ago)"
        "Backup is DUE (interval: 24 hours)"
        or
        "Last backup: 2026-03-22 09:15:00 (2 hours ago)"
        "Next backup due in approximately 22 hours"
        """
        last_backup = self.engine.should_run()
        if last_backup:
            print(f"Last backup: {last_backup} ({self.engine.time_since_last_backup()} ago)")
            print(f"Backup is DUE (interval: {self.engine.backup_interval} hours)")
            return True
        else:
            print(f"Last backup: {last_backup} ({self.engine.time_since_last_backup()} ago)")
            print(f"Next backup due in approximately {self.engine.time_until_next_backup()} hours)")
            return False
        
if __name__ == "__main__":
    app = BackupApp()
    app.run()