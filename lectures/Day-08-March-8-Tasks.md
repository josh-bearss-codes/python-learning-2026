# DAY 8 — Sunday, March 8, 2026
## Lecture: ETL in Python — Bridging Your Two Worlds

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue)  
**Phase**: Foundation — you write, AI explains and reviews  
**Morning Session**: 8:00–11:00 AM (3 hours) — Build 1 substantial project  
**Evening Session**: 7:00–8:30 PM (1.5 hours) — Week 1 review and reflection  
**Today's theme**: Data pipeline architecture — the place where your existing expertise meets your new language

---

## OPENING LECTURE: THE BRIDGE BETWEEN WHO YOU WERE AND WHO YOU'RE BECOMING

Today is the most important day of Week 1, and I don't say that lightly.

For seven days, you've been learning Python as a new language. You've built calculators, contact books, quiz games, budget trackers. Useful projects, but they could have been built by anyone learning Python for the first time. Today is different. Today we build something that only you — a data engineer — would build correctly on Day 8.

Let me frame the problem.

You've spent your career working with systems like Kafka, Flink, Spark, and Airflow. You understand concepts that most Python beginners won't encounter for years: idempotency, schema validation, data lineage, pipeline observability, error isolation, graceful degradation. These aren't Python concepts — they're **data engineering principles** that transcend any programming language.

Today's project is a miniature ETL pipeline in Python. On the surface, it reads CSV files, transforms the data, validates it, and outputs JSON. A beginner would build this as a linear script — read file, loop through rows, write output. Done in 30 minutes. Fragile. Untestable. No error recovery.

You're going to build it as a **pipeline** — a sequence of discrete stages where each stage has a single responsibility, where errors in one stage don't corrupt another, where the pipeline can be observed, logged, and debugged. You're going to build it the way a data engineer thinks about data movement, but expressed in Python.

**Why this matters for your career trajectory**: In two months, you'll be building AI data pipelines for clients. RAG systems are ETL systems — Extract documents, Transform them into embeddings, Load them into vector stores. AI agent workflows are pipelines — Extract a user query, Transform it through multiple reasoning steps, Load the result back to the user. The pipeline pattern is the architectural backbone of everything you'll build in this plan. Today you implement it from scratch in the language you'll deliver it in.

Let's formalize the concepts before we write code.

---

## LECTURE: PIPELINE ARCHITECTURE — FROM CONCEPT TO IMPLEMENTATION

### What Is a Pipeline?

A pipeline is a sequence of processing stages where the output of one stage becomes the input of the next. You know this intuitively from your Airflow DAGs — each task receives data, transforms it, and passes it forward. But there's a deeper principle at work that many engineers never articulate explicitly:

> **A pipeline is a composition of pure transformations separated by observable boundaries.**

Let's unpack that:

**Pure transformations** mean each stage takes input and produces output without side effects. The Extract stage reads a file and produces a list of raw records. It doesn't also validate them. It doesn't also transform them. It extracts. Period. This is separation of concerns applied to data flow.

**Observable boundaries** mean you can inspect the data between any two stages. After Extract, you can see exactly what was read. After Transform, you can see exactly what changed. After Validate, you can see exactly what passed and what failed. This observability is what makes pipelines debuggable. When a monolithic script fails, you get a stack trace somewhere in 200 lines. When a pipeline stage fails, you know exactly which stage, with exactly what input.

### The Stages of Today's Pipeline

```
┌──────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────┐
│ EXTRACT  │ ──> │  TRANSFORM  │ ──> │ VALIDATE │ ──> │   LOAD   │
│          │     │             │     │          │     │          │
│ Read CSV │     │ Clean data  │     │ Check    │     │ Write    │
│ Parse    │     │ Normalize   │     │ rules    │     │ JSON     │
│ rows     │     │ Derive      │     │ Reject   │     │ Report   │
│          │     │ fields      │     │ bad rows │     │ stats    │
└──────────┘     └─────────────┘     └──────────┘     └──────────┘
      │                │                   │                │
   raw_records    transformed_records  valid/invalid    output files
```

Each arrow represents a **contract** — an agreement about the shape of data flowing between stages. The Extract stage promises to output a list of dictionaries with certain keys. The Transform stage promises to take that exact shape and output a slightly different shape. The Validate stage promises to separate records into "valid" and "invalid" buckets. The Load stage promises to write valid records to a file and produce a summary.

If any stage breaks its contract, the next stage fails immediately with a clear error — not silently producing corrupt output 300 lines later.

### How This Differs From Yesterday's Architecture

Yesterday you learned about layered architecture: data layer, business logic, presentation. That organizes code by **responsibility type**. Today's pipeline architecture organizes code by **processing phase**. Both are valid. Both are useful. They answer different questions:

- **Layered**: "What kind of work is this code doing?" (storage? calculation? display?)
- **Pipeline**: "When in the data flow does this code execute?" (reading? transforming? writing?)

Real systems use both. Your pipeline stages might internally use layered architecture — the Extract stage might have its own data-reading logic and its own error handling. The Validate stage might have its own business rules and its own reporting. The two patterns compose.

---

## PROJECT 15: `data_pipeline_mini.py` (~2.5 hours)

### The Problem

You have a messy CSV file of sales data. Some rows have missing values. Some have negative prices. Some dates are in different formats. Some product names have inconsistent capitalization. Your pipeline needs to:

1. **Extract**: Read the CSV and produce a list of raw record dictionaries
2. **Transform**: Clean, normalize, and derive new fields from the raw data
3. **Validate**: Apply business rules, separating valid records from rejected ones
4. **Load**: Write valid records to JSON, write rejected records to a separate file, produce a run summary

### Concepts to Learn and Use

- **Pipeline pattern** — composing discrete stages where each stage has input/output contracts
- **Error isolation** — bad data in one stage doesn't corrupt another stage's output
- **Logging** — `logging` module instead of `print()` for pipeline observability. `logging.info()`, `logging.warning()`, `logging.error()` with timestamps and severity levels.
- **`dataclass` decorator** — a modern Python feature (3.7+) that generates `__init__`, `__repr__`, and more for you automatically. Reduces boilerplate for data-holding classes.
- **Type hints** — annotating function signatures with expected types: `def extract(filepath: str) -> list[dict]`. These don't enforce types at runtime, but they make your code self-documenting and enable IDE autocomplete.
- **`pathlib.Path`** — object-oriented file path handling, more Pythonic than `os.path`: `Path("data/input.csv").exists()`, `Path("output").mkdir(exist_ok=True)`
- **`datetime.strptime` and `strftime`** — parsing dates from various formats and outputting a canonical format
- **List comprehension with conditional** — `[transform(r) for r in records if r is not None]`
- **`try`/`except` at the record level** — catching errors per-row rather than aborting the entire pipeline
- **Pipeline statistics** — counting records in, records transformed, records valid, records rejected, runtime

### Reference Material

- Python docs — `logging`: https://docs.python.org/3/library/logging.html
- Python docs — `logging` HOWTO: https://docs.python.org/3/howto/logging.html
- Python docs — `dataclasses`: https://docs.python.org/3/library/dataclasses.html
- Python docs — `pathlib`: https://docs.python.org/3/library/pathlib.html
- Python docs — type hints: https://docs.python.org/3/library/typing.html
- Real Python — logging: https://realpython.com/python-logging/
- Real Python — data classes: https://realpython.com/python-data-classes/

### First: Create the Messy Input Data

Before writing any pipeline code, create the data your pipeline will process. Save this as `data/sales_raw.csv`:

```bash
mkdir -p data
```

```csv
date,product,quantity,unit_price,region
2026-03-01,Widget A,10,29.99,North
2026-03-01,widget b,5,49.99,South
03/02/2026,Widget A,3,29.99,north
2026-03-02,Widget C,-2,19.99,East
2026-03-03,Widget B,,49.99,West
2026-03-03,WIDGET A,7,29.99,North
2026-03-04,Widget D,12,0,South
2026-03-04,Widget A,8,29.99,
2026-03-05,Widget B,4,49.99,East
2026-03-05,,6,15.99,West
2026-03-06,Widget A,twenty,29.99,North
2026-03-06,Widget C,3,19.99,South
```

**Study this data before you code.** Identify every problem:

1. Row 2: product name lowercase ("widget b"), should be title case
2. Row 3: date is MM/DD/YYYY instead of YYYY-MM-DD, region lowercase
3. Row 4: negative quantity — does that make sense for a sale?
4. Row 5: quantity is empty/missing
5. Row 6: product name ALL CAPS
6. Row 7: unit_price is 0 — is a free product valid?
7. Row 8: region is empty
8. Row 10: product name is empty
9. Row 11: quantity is "twenty" — not a number

A good pipeline handles every one of these cases explicitly. It doesn't silently skip bad rows. It doesn't crash on the first error. It processes everything it can, rejects what it can't, and tells you exactly what happened.

### Design Questions (Answer These BEFORE You Code)

These design decisions define your pipeline's behavior. Work through each one as if you're writing a technical spec for a team.

1. **What is the contract between Extract and Transform?**
   Extract outputs a `list[dict]` where each dict has keys matching the CSV headers: `date`, `product`, `quantity`, `unit_price`, `region`. All values are strings at this point — Extract doesn't interpret the data, it just reads it faithfully. This is an important principle: **Extract is dumb on purpose.** It doesn't know that `quantity` should be an integer. It reads what the file says.

2. **What does Transform do to each record?**
   This is where data gets cleaned and enriched:
   - Normalize product names to title case: "widget b" → "Widget B", "WIDGET A" → "Widget A"
   - Normalize region to title case: "north" → "North"
   - Parse dates into canonical format (YYYY-MM-DD), handling both `YYYY-MM-DD` and `MM/DD/YYYY`
   - Convert quantity from string to integer
   - Convert unit_price from string to float
   - Derive a new field: `total = quantity × unit_price`
   - If a conversion fails (e.g., "twenty" can't become an integer), mark the record with an error rather than crashing

3. **What are the validation rules?**
   After transformation, a record is valid only if ALL of these are true:
   - `product` is not empty
   - `quantity` is a positive integer (> 0)
   - `unit_price` is a positive number (> 0)
   - `region` is not empty
   - `date` was successfully parsed
   - No transformation errors occurred

   A record that fails any rule is **rejected** — moved to a separate output with the reason for rejection. It is not silently discarded.

4. **What does Load produce?**
   Three outputs:
   - `data/sales_clean.json` — valid, clean records
   - `data/sales_rejected.json` — rejected records with rejection reasons
   - Console summary — counts and statistics for the pipeline run

5. **What should logging look like?**
   Each stage logs its start and end. Each rejected record logs a warning with the reason. The final summary logs overall statistics. This is how you'd observe a production pipeline.

### Ask GLM-4.7-Flash Before Coding

`Cmd+L` → "Explain three Python concepts I'm about to use:

1. The `logging` module — how to set up a basic logger with timestamps, log levels (INFO, WARNING, ERROR), and why logging is better than print() for applications. 
2. The `dataclass` decorator — how it works, what it generates automatically, and when you'd use it instead of a regular class.
3. Type hints in function signatures — how to annotate parameters and return types, and what `list[dict]` means as a type hint.

Explain each concept clearly. Don't write my program."

### Write Your Code

Build each stage as its own class. This might feel like over-engineering for a small project, but it establishes the pattern you'll use at scale.

```python
import csv
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────
INPUT_FILE = Path("data/sales_raw.csv")
OUTPUT_DIR = Path("data")
CLEAN_OUTPUT = OUTPUT_DIR / "sales_clean.json"
REJECTED_OUTPUT = OUTPUT_DIR / "sales_rejected.json"

# Set up logging — this replaces print() for pipeline observability
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("pipeline")


# ──────────────────────────────────────
# DATA MODELS
# ──────────────────────────────────────
@dataclass
class RawRecord:
    """Exactly what was read from the CSV. All strings."""
    date: str
    product: str
    quantity: str
    unit_price: str
    region: str
    row_number: int

@dataclass
class CleanRecord:
    """Transformed and typed. Ready for validation."""
    date: str              # Canonical YYYY-MM-DD format
    product: str           # Title case
    quantity: int           # Parsed integer
    unit_price: float      # Parsed float
    region: str            # Title case
    total: float           # Derived: quantity * unit_price
    row_number: int
    errors: list = field(default_factory=list)  # Any transformation issues

@dataclass
class RejectedRecord:
    """A record that failed validation, with reasons."""
    raw_data: dict
    reasons: list
    row_number: int


# ──────────────────────────────────────
# STAGE 1: EXTRACT
# ──────────────────────────────────────
class Extractor:
    """Reads raw data from CSV. Does NOT interpret or clean.
    
    Contract: 
      Input  → filepath (str or Path)
      Output → list[RawRecord]
    """

    def run(self, filepath: Path) -> list:
        logger.info(f"EXTRACT: Reading from {filepath}")
        # Open file with csv.DictReader
        # Create a RawRecord for each row, tracking row_number
        # Log how many records were read
        # Return list of RawRecords


# ──────────────────────────────────────
# STAGE 2: TRANSFORM
# ──────────────────────────────────────
class Transformer:
    """Cleans, normalizes, and derives fields.
    
    Contract:
      Input  → list[RawRecord]
      Output → list[CleanRecord]
    
    Does NOT decide if records are valid. That's the validator's job.
    If a field can't be converted, it records the error on the 
    CleanRecord rather than crashing the pipeline.
    """

    DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y"]

    def run(self, raw_records: list) -> list:
        logger.info(f"TRANSFORM: Processing {len(raw_records)} records")
        # For each RawRecord, call self._transform_one()
        # Log how many were processed
        # Return list of CleanRecords

    def _transform_one(self, raw: object) -> object:
        errors = []

        # Normalize product name to title case
        product = raw.product.strip().title() if raw.product.strip() else ""

        # Normalize region to title case
        region = raw.region.strip().title() if raw.region.strip() else ""

        # Parse date — try each format, record error if none work
        date = self._parse_date(raw.date, errors)

        # Convert quantity to int — record error if it fails
        quantity = self._safe_int(raw.quantity, "quantity", errors)

        # Convert unit_price to float — record error if it fails
        unit_price = self._safe_float(raw.unit_price, "unit_price", errors)

        # Derive total (only if both parsed successfully)
        total = (quantity or 0) * (unit_price or 0.0)

        # Return CleanRecord with whatever we could parse
        # ...

    def _parse_date(self, date_str: str, errors: list) -> str:
        # Try each format in DATE_FORMATS
        # Return canonical YYYY-MM-DD string
        # If none work, append to errors and return empty string

    def _safe_int(self, value: str, field_name: str, errors: list) -> Optional[int]:
        # Try int(value.strip()), return result
        # On failure, append error message, return None

    def _safe_float(self, value: str, field_name: str, errors: list) -> Optional[float]:
        # Try float(value.strip()), return result
        # On failure, append error message, return None


# ──────────────────────────────────────
# STAGE 3: VALIDATE
# ──────────────────────────────────────
class Validator:
    """Applies business rules. Separates valid from invalid.
    
    Contract:
      Input  → list[CleanRecord]
      Output → (list[CleanRecord], list[RejectedRecord])
    
    Returns TWO lists: records that passed, and records that failed 
    with specific reasons attached. Nothing is silently discarded.
    """

    def run(self, records: list) -> tuple:
        logger.info(f"VALIDATE: Checking {len(records)} records")
        valid = []
        rejected = []

        for record in records:
            reasons = self._check_rules(record)
            if reasons:
                # Record failed — create RejectedRecord
                # Log warning with row number and reasons
                pass
            else:
                # Record passed
                pass

        logger.info(f"VALIDATE: {len(valid)} valid, {len(rejected)} rejected")
        return valid, rejected

    def _check_rules(self, record: object) -> list:
        reasons = []
        # Rule 1: product must not be empty
        # Rule 2: quantity must be positive integer (> 0)
        # Rule 3: unit_price must be positive (> 0)
        # Rule 4: region must not be empty
        # Rule 5: date must have been successfully parsed (not empty)
        # Rule 6: no transformation errors
        return reasons


# ──────────────────────────────────────
# STAGE 4: LOAD
# ──────────────────────────────────────
class Loader:
    """Writes outputs and produces pipeline summary.
    
    Contract:
      Input  → valid records, rejected records
      Output → JSON files + console summary
    """

    def run(self, valid: list, rejected: list, 
            clean_path: Path, rejected_path: Path) -> dict:
        logger.info(f"LOAD: Writing outputs")

        # Ensure output directory exists
        clean_path.parent.mkdir(parents=True, exist_ok=True)

        # Write valid records to JSON
        # Use dataclasses.asdict() to convert dataclass → dict

        # Write rejected records to JSON

        # Build and return summary statistics
        summary = {
            "records_extracted": len(valid) + len(rejected),
            "records_valid": len(valid),
            "records_rejected": len(rejected),
            "rejection_rate": f"...",
            # Add more: total revenue from valid records,
            # records per region, etc.
        }
        return summary


# ──────────────────────────────────────
# PIPELINE ORCHESTRATOR
# ──────────────────────────────────────
class Pipeline:
    """Composes stages and runs them in sequence.
    
    This is the equivalent of an Airflow DAG definition.
    Each stage is a task. The pipeline defines the order.
    """

    def __init__(self):
        self.extractor = Extractor()
        self.transformer = Transformer()
        self.validator = Validator()
        self.loader = Loader()

    def run(self, input_file: Path) -> dict:
        logger.info("=" * 50)
        logger.info("PIPELINE START")
        logger.info("=" * 50)
        start_time = datetime.now()

        # Stage 1: Extract
        raw_records = self.extractor.run(input_file)

        # Stage 2: Transform
        clean_records = self.transformer.run(raw_records)

        # Stage 3: Validate
        valid, rejected = self.validator.run(clean_records)

        # Stage 4: Load
        summary = self.loader.run(valid, rejected, CLEAN_OUTPUT, REJECTED_OUTPUT)

        # Add runtime to summary
        elapsed = (datetime.now() - start_time).total_seconds()
        summary["runtime_seconds"] = round(elapsed, 3)

        logger.info("=" * 50)
        logger.info("PIPELINE COMPLETE")
        for key, value in summary.items():
            logger.info(f"  {key}: {value}")
        logger.info("=" * 50)

        return summary


if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run(INPUT_FILE)
```

### What to Notice as You Build

**1. Each stage class has a `run()` method with a documented contract.** The docstring tells you exactly what goes in and what comes out. This is self-documenting code — someone reading your pipeline for the first time can understand the flow without reading the implementation details.

**2. The Transformer doesn't crash on bad data.** It records errors on the record and keeps going. The Validator then uses those errors as one of its rejection criteria. This is **error isolation** — a malformed quantity in row 11 doesn't prevent row 12 from being processed.

**3. Rejected records carry their rejection reasons.** When you inspect `sales_rejected.json`, every record tells you exactly why it was rejected. This is **pipeline observability**. In production systems, this is how you debug data quality issues without re-running the pipeline.

**4. The Pipeline class is the orchestrator.** It creates the stages and runs them in order. It doesn't contain business logic. It doesn't read files. It composes stages. This is the same role that Airflow plays — defining task dependencies and execution order.

**5. The `@dataclass` decorator eliminates boilerplate.** Compare `RawRecord` with yesterday's `Transaction` class. With `@dataclass`, you get `__init__`, `__repr__`, and `__eq__` for free. The `asdict()` function converts a dataclass to a dictionary for JSON serialization — no more writing `to_dict()` methods.

### Testing Your Pipeline

After you've built it, run it and verify the output:

```bash
python3 data_pipeline_mini.py
```

**Expected console output** should look something like:
```
08:45:01 [INFO] ==================================================
08:45:01 [INFO] PIPELINE START
08:45:01 [INFO] ==================================================
08:45:01 [INFO] EXTRACT: Reading from data/sales_raw.csv
08:45:01 [INFO] EXTRACT: Read 12 records
08:45:01 [INFO] TRANSFORM: Processing 12 records
08:45:01 [INFO] TRANSFORM: Processed 12 records
08:45:01 [INFO] VALIDATE: Checking 12 records
08:45:01 [WARNING] Row 4: Rejected — quantity must be positive
08:45:01 [WARNING] Row 5: Rejected — quantity could not be parsed
08:45:01 [WARNING] Row 7: Rejected — unit_price must be positive
08:45:01 [WARNING] Row 8: Rejected — region must not be empty
08:45:01 [WARNING] Row 10: Rejected — product must not be empty
08:45:01 [WARNING] Row 11: Rejected — quantity could not be parsed
08:45:01 [INFO] VALIDATE: 6 valid, 6 rejected
08:45:01 [INFO] LOAD: Writing outputs
08:45:01 [INFO] ==================================================
08:45:01 [INFO] PIPELINE COMPLETE
08:45:01 [INFO]   records_extracted: 12
08:45:01 [INFO]   records_valid: 6
08:45:01 [INFO]   records_rejected: 6
08:45:01 [INFO]   rejection_rate: 50.0%
08:45:01 [INFO]   runtime_seconds: 0.003
08:45:01 [INFO] ==================================================
```

**Then inspect the output files**:
```bash
# Valid records — should be clean, normalized, with totals
cat data/sales_clean.json | python3 -m json.tool

# Rejected records — each should have specific reasons
cat data/sales_rejected.json | python3 -m json.tool
```

**Verify specific transformations**:
- Row 2: "widget b" → "Widget B", region "South" unchanged ✓
- Row 3: date "03/02/2026" → "2026-03-02", region "north" → "North" ✓
- Row 6: "WIDGET A" → "Widget A" ✓
- Row 1: total should be 10 × 29.99 = 299.90 ✓

### Ask GLM-4.7-Flash After Coding

Select all code → `Cmd+L` → "Review this ETL pipeline. I'm trying to implement clean pipeline architecture with these principles: each stage has a documented input/output contract, errors are isolated per-record rather than crashing the pipeline, rejected records carry their rejection reasons, and the orchestrator only composes stages without containing logic. Does my implementation achieve this? Is my use of dataclasses, logging, type hints, and pathlib idiomatic Python? If I wanted to add a new stage (e.g., deduplication between Transform and Validate), how easy would that be? What would a senior data engineer change?"

### Commit

```bash
git add . && git commit -m "Project 15: data_pipeline_mini.py — ETL pipeline architecture, logging, dataclasses, type hints"
```

---

## BREAK — Afternoon

Take a real break. Walk the dog. Lift. Eat. You've been coding for 3 hours on a dense project. The evening session is reflection, not building.

---

## EVENING SESSION (7:00–8:30 PM): WEEK 1 REVIEW

### The Numbers

Before reflecting on what you've learned, look at what you've done:

| Day | Date | System | Hours | Projects | Key Concepts |
|-----|------|--------|-------|----------|-------------|
| 1 | Mar 1 | Ubuntu | 4.5 | 4 | Variables, input, f-strings, try/except, functions, dicts |
| 2 | Mar 2 | Ubuntu | 2 | 2 | Lists, loops (for/while), random, break |
| 3 | Mar 3 | Mac | 0 | 0 | Hardware setup, Ollama, model downloads |
| 4 | Mar 4 | Mac | 1.5 | 2 | def functions, return values, JSON file I/O, with statement |
| 5 | Mar 5 | Mac | 2 | 2 | Classes, \_\_init\_\_, self, \_\_str\_\_, enumerate, OOP |
| 6 | Mar 6 | Mac | 2 | 2 | argparse, lambda, sorted(key=), \_\_name\_\_ |
| 7 | Mar 7 | Mac | 3 | 2 | Layered architecture, defaultdict, csv module, @property |
| 8 | Mar 8 | Mac | 3 | 1 | Pipeline architecture, logging, dataclasses, type hints |
| **Total** | | | **18** | **15** | |

You wrote 15 projects in 18 hours of active coding across 8 days.

### Reflection Exercise (Write This Down)

Open a new file: `~/dev/year-1/month-01/week-01/week-01-review.md`

Answer these questions honestly. This isn't for anyone but you.

**1. What concept clicked the fastest?**
Think about which idea felt natural the moment you encountered it. Was it functions? Classes? File I/O? Identifying this tells you where your existing mental models transfer cleanly.

**2. What concept still feels shaky?**
Be honest. Is it classes and `self`? Lambda functions? The difference between `sorted()` and `.sort()`? Whatever it is, that's where you should spend extra time in Week 2. Ask Qwen3-Coder to explain it from a different angle.

**3. Where did your data engineering experience help the most?**
Today's pipeline probably felt more natural than the quiz game. Yesterday's layered architecture probably mapped to your ETL instincts. Identify the places where your existing expertise accelerated learning — these are your competitive advantages.

**4. How does GLM-4.7-Flash compare to CodeLlama 34B on Ubuntu?**
You used both this week. What's the difference in quality? Speed? Usefulness? This matters because you're evaluating your own AI tools — a skill you'll use when recommending models to clients.

**5. Can you read Python code now?**
Open one of your Day 1 projects and one of your Day 7 or 8 projects. Compare the code quality. Can you look at Python code and understand what it does without running it? This reading ability is what enables the AI-directed workflow starting in Week 3.

**6. What would you change about the week if you could redo it?**
More time on one concept? Less time on another? Different project order? Your answer helps calibrate Week 2.

### Code Organization

Before Week 2 starts tomorrow, make sure your repo is clean:

```bash
cd ~/dev/year-1

# Verify structure
ls month-01/week-01/
# Should show all 15 project files plus the review markdown

# If any files are in the wrong place, move them
# git mv source destination

# Final commit
git add .
git commit -m "Week 1 complete: 15 projects, week-01-review.md"
git push
```

### Preview: Week 2 (March 9–15)

Week 2 stays in the Foundation phase — you still write code yourself — but with a key change: **lean harder on AI code review.** After finishing each project, send the entire file to Continue and ask "What would a senior developer change?" Then make those changes yourself.

The projects get more practical and interconnected:

| Day | Project | New Concepts |
|-----|---------|-------------|
| 9 (Mon) | `recipe_manager.py` | Nested dicts, lists of dicts, search |
| 10 (Tue) | `habit_tracker.py` | Date arithmetic, streak logic, persistence |
| 11 (Wed) | `inventory_system.py` | Low-stock alerts, sorting, filtering patterns |
| 12 (Thu) | `student_gradebook.py` | Multiple related classes, GPA calculation |
| 13 (Fri) | `file_organizer.py` | os, pathlib, shutil — working with the filesystem |
| 14-15 (Sat-Sun) | `workout_logger.py` + `reading_list.py` | matplotlib charts, comprehensive OOP |

By end of Week 2, you should be comfortable enough with Python that you can read AI-generated code and tell whether it's good or bad. That's the gate to Week 3, where you start directing AI instead of writing everything yourself.

---

## CLOSING LECTURE: WHAT WEEK 1 BUILT

I want to leave you with a mental model for what happened this week.

**Days 1–4** loaded your brain with Python's vocabulary: variables, functions, loops, conditionals, file I/O, error handling. These are the words of the language.

**Days 5–6** taught you Python's grammar: classes, OOP, module structure, lambda, argparse. These are the rules for combining words into sentences.

**Days 7–8** taught you Python's rhetoric: architecture, separation of concerns, pipeline patterns, layered design. These are the principles for organizing sentences into coherent arguments.

An AI can generate vocabulary and grammar flawlessly. What it cannot do — what no AI currently does well — is rhetoric. It can write a function. It can write a class. It cannot design a system. It cannot decide where the boundaries between layers should be. It cannot determine which responsibilities belong in which stage of a pipeline.

That's your job. That's what you spent Days 7–8 learning. That architectural judgment is what separates a $50/hour code monkey from a $150–$250/hour systems architect. And it's what makes the 10-80-10 model work: you provide the rhetoric (architecture), AI provides the vocabulary and grammar (implementation), and you verify the result.

You're ready for Week 2.

---

**Day 8 of 365. Week 1 complete. 15 projects. The foundation is set.** 🚀
