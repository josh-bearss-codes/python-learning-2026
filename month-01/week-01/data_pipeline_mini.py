# data_pipeline_mini.py
import csv
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple, Dict, DefaultDict
from collections import defaultdict
from decimal import Decimal

# ──────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────
INPUT_FILE = Path("./data/sales_raw.csv")
OUTPUT_DIR = Path("./data")
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
    errors: List[str] = field(default_factory=list)  # Any transformation issues

@dataclass
class RejectedRecord:
    """A record that failed validation, with reasons."""
    raw_data: dict
    reasons: List[str]
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

    def run(self, filepath: Path) -> List[RawRecord]:
        logger.info(f"EXTRACT: Reading from {filepath}")
        # Open file with csv.DictReader
        # Create a RawRecord for each row, tracking row_number
        # Log how many records were read
        # Return list of RawRecords
        records = []
        try:
            with open(filepath, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row_number, row in enumerate(reader, 1):
                    # Skip empty rows
                    if not any(row.values()):
                        logger.warning(f"EXTRACT: Skipping empty row {row_number}")
                        continue
                    
                    raw_data = dict(row)
                    raw_data['row_number'] = row_number
                    records.append(RawRecord(**raw_data))
                rows_read = sum(1 for _ in records)
                logger.info(f"EXTRACT: Read {rows_read} records")
            return records
            
        except Exception as e:
            logger.error(f"EXTRACT: Error reading from {filepath}: {e}")
            raise


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

    def run(self, raw_records: List[RawRecord]) -> List[CleanRecord]:
        logger.info(f"TRANSFORM: Processing {len(raw_records)} records")
        # For each RawRecord, call self._transform_one()
        # Log how many were processed
        # Return list of CleanRecords
        clean_records = []
        
        for raw_record in raw_records:
            clean_record = self._transform_one(raw_record)
            clean_records.append(clean_record)
            
        logger.info(f"TRANSFORM: {len(clean_records)} records processed")
        return clean_records

    def _transform_one(self, raw: RawRecord) -> CleanRecord:
        errors = []
        clean_record = {}

        # Normalize product name to title case
        product = raw.product.strip().title() if raw.product.strip() else ""
        if not product:
            errors.append("Product is required")
        clean_record["product"] = product
        
        # Normalize region to title case
        region = raw.region.strip().title() if raw.region.strip() else ""
        if not region:
            errors.append("Region is required")
        clean_record["region"] = region

        # Parse date — try each format, record error if none work
        date = self._parse_date(raw.date, errors)
        if not date:
            errors.append("Date is required")
        clean_record["date"] = date

        # Convert quantity to int — record error if it fails
        quantity = self._safe_int(raw.quantity, "quantity", errors)
        if not quantity:
            errors.append("Quantity is required")
            quantity = 0
        clean_record["quantity"] = quantity

        # Convert unit_price to float — record error if it fails
        unit_price = self._safe_float(raw.unit_price, "unit_price", errors)
        if not unit_price:
            errors.append("Unit price is required")
            unit_price = 0.0
        clean_record["unit_price"] = unit_price

        # Derive total (only if both parsed successfully)
        total = 0.0
        if quantity and unit_price:
            total = quantity * unit_price
            
        clean_record["total"] = total
        
        # Create CleanRecord with all fields
        return CleanRecord(
            date=clean_record["date"],
            product=clean_record["product"],
            quantity=clean_record["quantity"],
            unit_price=clean_record["unit_price"],
            region=clean_record["region"],
            total=clean_record["total"],
            row_number=raw.row_number,
            errors=errors
        )

    def _parse_date(self, date_str: str, errors: List[str]) -> str:
        # Try each format in DATE_FORMATS
        # Return canonical YYYY-MM-DD string
        # If none work, append to errors and return empty string
        if not date_str.strip():
            return ""
            
        for date_format in self.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_str.strip(), date_format)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
                
        errors.append(f"Invalid date format: {date_str}")
        return ""

    def _safe_int(self, value: str, field_name: str, errors: List[str]) -> Optional[int]:
        # Try int(value.strip()), return result
        # On failure, append error message, return None
        try:
            return int(value.strip())
        except (ValueError, TypeError):
            errors.append(f"Invalid {field_name}: {value.strip()}")
            return None

    def _safe_float(self, value: str, field_name: str, errors: List[str]) -> Optional[float]:
        # Try float(value.strip()), return result
        # On failure, append error message, return None
        try:
            return float(value.strip())
        except (ValueError, TypeError):
            errors.append(f"Invalid {field_name}: {value.strip()}")
            return None


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

    def run(self, records: List[CleanRecord]) -> Tuple[List[CleanRecord], List[RejectedRecord]]:
        logger.info(f"VALIDATE: Checking {len(records)} records")
        valid = []
        rejected = []

        for record in records:
            reasons = self._check_rules(record)
            if reasons:
                # Record failed — create RejectedRecord
                rejected.append(RejectedRecord(
                    raw_data=asdict(record),
                    reasons=reasons,
                    row_number=record.row_number
                ))
                logger.warning(f"REJECTED: {record.row_number} - {reasons}")
            else:
                # Record passed
                valid.append(record)

        logger.info(f"VALIDATE: {len(valid)} valid, {len(rejected)} rejected")
        return valid, rejected

    def _check_rules(self, record: CleanRecord) -> List[str]:
        reasons = []
        
        # Rule 1: product must not be empty
        if not record.product:
            reasons.append("Product cannot be empty")
            
        # Rule 2: quantity must be positive integer (> 0)
        if record.quantity <= 0:
            reasons.append("Quantity must be positive")
            
        # Rule 3: unit_price must be positive (> 0)
        if record.unit_price <= 0:
            reasons.append("Unit price must be positive")
            
        # Rule 4: region must not be empty
        if not record.region:
            reasons.append("Region cannot be empty")
            
        # Rule 5: date must have been successfully parsed (not empty)
        if not record.date:
            reasons.append("Date cannot be empty")
            
        # Rule 6: no transformation errors
        if record.errors:
            reasons.append("Transformation errors detected")
            
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

    def run(self, valid: List[CleanRecord], rejected: List[RejectedRecord], 
            clean_path: Path, rejected_path: Path) -> Dict[str, object]:
        logger.info(f"LOAD: Writing outputs")

        # Ensure output directory exists
        clean_path.parent.mkdir(parents=True, exist_ok=True)
        rejected_path.parent.mkdir(parents=True, exist_ok=True)

        # Write valid records to JSON
        # Use dataclasses.asdict() to convert dataclass → dict
        with open(clean_path, "w") as f:
            json.dump([asdict(record) for record in valid], f, indent=2)
            logger.info(f"LOAD: Wrote {len(valid)} valid records to {clean_path}")

        # Write rejected records to JSON
        with open(rejected_path, "w") as f:
            json.dump([asdict(record) for record in rejected], f, indent=2)
            logger.info(f"LOAD: Wrote {len(rejected)} rejected records to {rejected_path}")

        # Build and return summary statistics
        total_revenue = sum(record.total for record in valid)
        
        # Count records per region
        records_per_region = defaultdict(int)
        for record in valid:
            records_per_region[record.region] += 1
            
        # Count records per product
        records_per_product = defaultdict(int)
        for record in valid:
            records_per_product[record.product] += 1

        summary = {
            "records_extracted": len(valid) + len(rejected),
            "records_valid": len(valid),
            "records_rejected": len(rejected),
            "rejection_rate": len(rejected) / (len(valid) + len(rejected)),
            "total_revenue": total_revenue,
            "records_per_region": dict(records_per_region),
            "records_per_product": dict(records_per_product),

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
        logger.info(f"Input file: {input_file}")
        logger.info(f"Pipeline start time: {start_time}")
        logger.info("Pipeline stages:")
        logger.info("  1. Extract")
        logger.info("  2. Transform")
        logger.info("  3. Validate")
        logger.info("  4. Load")
        logger.info("=" * 50)
        logger.info("  Processing records...")
        logger.info("=" * 50)

        # Stage 1: Extract
        raw_records = self.extractor.run(input_file)
    
        # Stage 2: Transform
        clean_records = self.transformer.run(raw_records)
      
        # Stage 3: Validate
        valid, rejected = self.validator.run(clean_records)

        # Stage 4: Load
        summary = self.loader.run(valid, rejected, CLEAN_OUTPUT, REJECTED_OUTPUT)
        
        logger.info("=" * 50)
        logger.info("Pipeline completed.")
        logger.info(f"Pipeline end time: {datetime.now()}")

        # Add runtime to summary
        elapsed = (datetime.now() - start_time).total_seconds()
        summary["runtime_seconds"] = round(elapsed, 3)
        summary["runtime_minutes"] = round(elapsed / 60, 3)
        logger.info("=" * 50)
        logger.info("Pipeline summary:")
        for key, value in summary.items():
            logger.info(f"  {key}: {value}")
        logger.info("=" * 50)

        return summary


if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run(INPUT_FILE)