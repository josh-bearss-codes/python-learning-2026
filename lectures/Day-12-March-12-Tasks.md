# DAY 12 — Thursday, March 12, 2026
## Lecture: Many-to-Many Relationships — When Objects Need to Know About Each Other

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue)  
**Phase**: Foundation — you write, AI reviews more aggressively  
**Commute**: CS50 Week 3 continued (Algorithms) or Talk Python To Me  
**Evening Session**: 7:00–9:00 PM (2 hours) — Build 1 project  
**Today's theme**: How to model relationships where A knows about B and B knows about A — without creating an architectural mess

---

## OPENING LECTURE: THE RELATIONSHIP PROBLEM

Every project you've built so far has had clean, one-directional relationships. A Recipe *has* Ingredients. An Account *has* Transactions. A Habit *has* completions. The arrow points one way: the parent knows about the child, and the child doesn't need to know about the parent.

Today we encounter a different beast: **bidirectional relationships.** Consider a university:

- A Student takes multiple Courses.
- A Course contains multiple Students.
- Each Student-Course pairing has its own data: the grade earned.

This is a **many-to-many** relationship. One student maps to many courses. One course maps to many students. And the relationship itself (the enrollment with a grade) carries data.

This is not an exotic edge case. Many-to-many relationships are everywhere:

- **Authors and Books**: One author writes many books. One book can have multiple authors.
- **Doctors and Patients**: One doctor treats many patients. One patient sees many doctors. Each visit has its own data (date, diagnosis, prescription).
- **Users and Roles** in software: One user can have multiple roles. One role is assigned to multiple users.
- **Documents and Tags** in your future RAG systems: One document has many tags. One tag applies to many documents.

The architectural question today is: **how do you model this in Python without creating a tangled dependency nightmare?**

Let me show you three approaches — one terrible, one functional, and one correct — so you understand why the correct approach exists.

---

## LECTURE: THREE WAYS TO MODEL MANY-TO-MANY (AND WHY TWO ARE WRONG)

### Approach 1: Circular References (The Trap)

The naive approach is to have each side hold references to the other:

```python
class Student:
    def __init__(self, name):
        self.name = name
        self.courses = []      # List of Course objects

class Course:
    def __init__(self, name):
        self.name = name
        self.students = []     # List of Student objects
```

Now when a student enrolls in a course:

```python
alice = Student("Alice")
math = Course("Math 101")

alice.courses.append(math)     # Alice knows about Math
math.students.append(alice)    # Math knows about Alice
```

This seems simple. But there are serious problems:

**Problem 1: Data duplication.** The relationship is stored in two places. If you remove Alice from math.students but forget to remove Math from alice.courses, your data is inconsistent. Every relationship change requires updating *both* sides, and forgetting one creates silent bugs.

**Problem 2: Where does the grade live?** Alice got a B+ in Math 101. Where do you put that? It doesn't belong on Alice (she has many grades, one per course). It doesn't belong on the Course (it has many grades, one per student). The grade belongs to the *relationship itself* — the enrollment. But our model has no object representing the enrollment.

**Problem 3: JSON serialization nightmare.** If Alice has a reference to Math, and Math has a reference to Alice, you have a circular reference. `json.dump()` will hit infinite recursion: Alice → Math → Alice → Math → ... crash.

**Problem 4: God objects.** Both Student and Course need methods to manage the relationship: `enroll()`, `drop()`, `get_grade()`, `set_grade()`. Responsibility for the relationship is split across two classes with no clear owner.

### Approach 2: One-Sided Ownership (Functional But Incomplete)

A slightly better approach is to pick one side as the owner:

```python
class Student:
    def __init__(self, name):
        self.name = name
        self.enrollments = {}  # {course_name: grade}
```

Now the Student owns all relationship data. This eliminates duplication and circular references. But the Course has no way to answer "who are my students?" without scanning every Student in the system. If you have 10,000 students and need the roster for one course, you're checking all 10,000. That's O(n) when it should be O(1).

### Approach 3: The Association Object (The Professional Solution)

The correct approach creates a **third class** that represents the relationship itself:

```python
class Enrollment:
    """The relationship between a Student and a Course.
    
    This is the 'join table' concept from databases, modeled as a Python object.
    Each enrollment is a fact: 'this student is in this course with this grade.'
    """
    def __init__(self, student_name, course_name, grade=None):
        self.student_name = student_name
        self.course_name = course_name
        self.grade = grade
```

Now the relationship has a home. The grade lives on the Enrollment. Neither Student nor Course needs to reference the other directly. A separate manager class (the Gradebook) holds the list of enrollments and can answer questions from either direction:

- "What courses is Alice in?" → Filter enrollments where student_name == "Alice"
- "Who's in Math 101?" → Filter enrollments where course_name == "Math 101"
- "What grade did Alice get in Math 101?" → Find the specific enrollment

This is called the **Mediator Pattern** — a third object manages the relationship between two other objects so they don't need to know about each other directly.

**If you've worked with relational databases**, this is exactly the same as a join table / association table / bridge table. In SQL:

```
students table:  id, name, email
courses table:   id, name, credits
enrollments table: student_id, course_id, grade   ← the join table
```

Your data engineering background makes this intuitive. The same principle applies in Python objects.

---

## LECTURE: WHY THE MEDIATOR PATTERN MATTERS FOR YOUR FUTURE

In two weeks, you start directing AI to write code. In two months, you start building AI systems for clients. The mediator pattern shows up everywhere:

**In RAG systems**: Documents and Chunks have a many-to-many relationship with Queries. An Embedding object sits in the middle, connecting a chunk to a vector representation with metadata (model used, timestamp, relevance score). The vector store is the mediator.

**In AI agent workflows**: Tools and Agents have a many-to-many relationship. A ToolCall object sits in the middle, recording which agent called which tool, with what parameters, and what result. The orchestrator is the mediator.

**In pipeline systems (your expertise)**: Data sources and destinations have a many-to-many relationship. Transformations sit in the middle, recording what was extracted from where, what was changed, and where it was loaded. The pipeline scheduler is the mediator.

When you write architectural specs in Week 3, you need to identify many-to-many relationships and specify the association object. AI won't do this on its own — it defaults to Approach 1 (circular references) or Approach 2 (one-sided ownership). Your job is to specify the mediator.

---

## LECTURE: WEIGHTED AVERAGES — THE MATH BEHIND GPA

Today's project calculates GPA (Grade Point Average). This requires understanding **weighted averages**, which are different from simple averages in an important way.

### Simple Average vs. Weighted Average

**Simple average**: Add all values, divide by count.

```python
grades = [3.7, 3.0, 4.0]
simple_avg = sum(grades) / len(grades)   # (3.7 + 3.0 + 4.0) / 3 = 3.57
```

This treats every grade equally. But should a 1-credit seminar count the same as a 4-credit core course? In academia, no — courses have different weights (credit hours), and the GPA is a **weighted average**.

**Weighted average**: Multiply each value by its weight, sum those products, divide by the sum of weights.

```python
# (grade × credits) for each course, divided by total credits
grades_and_credits = [(3.7, 4), (3.0, 1), (4.0, 3)]

total_quality_points = sum(grade * credits for grade, credits in grades_and_credits)
# (3.7 × 4) + (3.0 × 1) + (4.0 × 3) = 14.8 + 3.0 + 12.0 = 29.8

total_credits = sum(credits for _, credits in grades_and_credits)
# 4 + 1 + 3 = 8

weighted_gpa = total_quality_points / total_credits
# 29.8 / 8 = 3.725
```

Notice how the 4-credit course (3.7) pulls the GPA up more than the 1-credit course (3.0) pulls it down. The weighted average gives more influence to higher-credit courses, which is the correct behavior.

**Why this matters beyond GPA**: Weighted averages appear in data engineering and AI constantly. When you compute the relevance of a search result, you weight different signals (title match, body match, recency) by importance. When you evaluate model performance, you weight different benchmarks by their relevance to your use case. The math is always the same: `sum(value × weight) / sum(weights)`.

### Letter Grade to Grade Point Conversion

The GPA system maps letter grades to numeric values. Here's the standard scale:

```python
GRADE_POINTS = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0
}
```

This dictionary becomes a lookup table in your code. When a student gets a "B+" in a 3-credit course, the quality points are `3.3 × 3 = 9.9`. Your `Enrollment` object stores the letter grade; the grade-point conversion happens in the calculation logic.

---

## LECTURE: BUILDING COMPARISON OPERATORS FOR A DOMAIN MODEL

Yesterday you learned the mechanics of `__eq__`, `__lt__`, and `@total_ordering`. Today we apply them to a domain model where the comparison semantics require more thought.

### What Does "Equal" Mean for a Student?

This is a design question, not a Python question. Consider:

```python
student_a = Student("Alice Smith", "S001", "alice@uni.edu")
student_b = Student("Alice Smith", "S002", "alice.s@uni.edu")
student_c = Student("Alice Smith", "S001", "newemail@uni.edu")
```

Are `student_a` and `student_b` equal? Same name, different IDs. **No** — they're different students who happen to share a name. Student ID is the unique identifier.

Are `student_a` and `student_c` equal? Same ID, different email. **Yes** — it's the same student who updated their email. The ID is what defines identity.

This is a fundamental OOP concept: **identity vs. equality**. Two objects are *identical* if they're the same object in memory (`is` operator). Two objects are *equal* if they represent the same real-world entity (`==` operator). For students, equality means same student ID.

```python
def __eq__(self, other):
    if not isinstance(other, Student):
        return NotImplemented
    return self.student_id == other.student_id
```

### What Does "Less Than" Mean for a Student?

This depends on context. Students might be sorted by:
- Name (alphabetical roster)
- GPA (academic standing)
- Student ID (administrative ordering)

There's no single "natural" ordering that makes sense in all cases. When no single ordering is clearly dominant, you have two options:

**Option A**: Pick one as the natural ordering and use `key` functions for alternatives.

```python
# Natural ordering: alphabetical by last name, then first name
def __lt__(self, other):
    if not isinstance(other, Student):
        return NotImplemented
    return (self.last_name, self.first_name) < (other.last_name, other.first_name)

# Alternative: sort by GPA in the caller
sorted(students, key=lambda s: s.gpa, reverse=True)
```

**Option B**: Don't define `__lt__` at all. Always use explicit `key` functions.

```python
# No __lt__ on Student — sorting always requires explicit key
by_name = sorted(students, key=lambda s: (s.last_name, s.first_name))
by_gpa = sorted(students, key=lambda s: s.gpa, reverse=True)
by_id = sorted(students, key=lambda s: s.student_id)
```

**For today's project, use Option A**: define `__lt__` for alphabetical ordering (the most common way to display a roster), and use `key` functions for GPA-based or ID-based sorting in the presentation layer. This gives you practice with both approaches.

### What Does "Less Than" Mean for a Course?

Courses have a natural ordering: by course code. "CS101" comes before "CS201" which comes before "MATH101". This is straightforward alphabetical ordering on the course code.

```python
def __lt__(self, other):
    if not isinstance(other, Course):
        return NotImplemented
    return self.course_code < other.course_code
```

---

## LECTURE: `__hash__` — THE HIDDEN PARTNER OF `__eq__`

When you define `__eq__` on a class, Python automatically makes your objects **unhashable** — they can't be used in sets or as dictionary keys. This is a safety mechanism.

Why? Because sets and dictionaries use hash values to organize their contents. If two objects are equal (`__eq__` returns True), they *must* have the same hash value. If you change `__eq__` without updating `__hash__`, sets and dicts will behave incorrectly — they might store "duplicate" objects or fail to find objects that should match.

The fix is simple: define `__hash__` to be consistent with `__eq__`:

```python
class Student:
    def __eq__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.student_id == other.student_id
    
    def __hash__(self):
        return hash(self.student_id)
```

**The rule**: Whatever attributes you use in `__eq__`, use the same attributes in `__hash__`. If equality is based on `student_id`, hash on `student_id`. This guarantees consistency.

Now your students work in sets:

```python
enrolled = {alice, bob, charlie}
if alice in enrolled:          # Uses __hash__ for O(1) lookup, __eq__ for confirmation
    print("Found")
```

And as dictionary keys:

```python
student_advisors = {alice: "Dr. Smith", bob: "Dr. Jones"}
print(student_advisors[alice])  # "Dr. Smith"
```

**When can you skip `__hash__`?** If your objects will never be used in sets or as dictionary keys, you don't strictly need it. But defining it is good practice and takes one line.

---

## PROJECT 19: `student_gradebook.py` (~2 hours)

### The Problem

Build a gradebook system for a small college. The system manages students, courses, and enrollments (the association between them). It records grades, calculates GPAs using weighted averages (credit hours), generates class rosters, identifies honor roll students, and produces academic reports. All data persists to JSON.

### Concepts to Learn and Use

- **Many-to-many relationships** via an association object (Enrollment)
- **Mediator pattern** — the Gradebook class manages relationships between Students and Courses
- **Weighted average** — GPA calculation using credit hours as weights
- **`__eq__` and `__hash__` together** — identity based on student ID / course code
- **`__lt__` with `@total_ordering`** — natural ordering for roster display
- **`__repr__` and `__str__`** — both representations for each class
- **Dictionary as lookup table** — grade points mapping
- **`statistics` module** — `statistics.mean()`, `statistics.median()` for class statistics
- **Filtering with list comprehensions** — honor roll, failing students, by major
- **Multiple sort orders** — by name (natural), by GPA, by enrollment date

### Reference Material

- Python docs — `__hash__`: https://docs.python.org/3/reference/datamodel.html#object.__hash__
- Python docs — `statistics`: https://docs.python.org/3/library/statistics.html
- Python docs — `functools.total_ordering`: https://docs.python.org/3/library/functools.html#functools.total_ordering
- Real Python — operator overloading: https://realpython.com/operator-function-overloading/
- Real Python — Python `__hash__()`: https://realpython.com/python-hash-table/

### Design Questions (Answer These BEFORE You Code)

1. **What are the entities and how do they relate?**

   ```
   Student ←──── Enrollment ────→ Course
     │               │               │
     │          (the join)           │
     │         - letter_grade        │
     │         - semester            │
     │                               │
     └── student_id (identity)       └── course_code (identity)
         name, email, major              name, credits, department
   ```

   Students and Courses don't reference each other directly. The Gradebook holds all three collections and answers questions by querying Enrollments.

2. **What is the `__eq__` / `__hash__` contract for each class?**

   | Class | Equality based on | Hash based on |
   |-------|------------------|---------------|
   | `Student` | `student_id` | `student_id` |
   | `Course` | `course_code` | `course_code` |
   | `Enrollment` | `student_id` + `course_code` (compound key) | `(student_id, course_code)` |

   Two Enrollments are equal if they link the same student to the same course. This prevents duplicate enrollments — if you try to add Alice to Math 101 twice, the system should recognize the duplicate.

3. **How does GPA calculation work step by step?**

   For Student "Alice" with these enrollments:
   ```
   CS101 (3 credits) — A  → 4.0 × 3 = 12.0 quality points
   MATH201 (4 credits) — B+ → 3.3 × 4 = 13.2 quality points
   ENG101 (3 credits) — A- → 3.7 × 3 = 11.1 quality points
   ```
   
   Total quality points: 12.0 + 13.2 + 11.1 = 36.3  
   Total credits: 3 + 4 + 3 = 10  
   GPA: 36.3 / 10 = **3.63**

   Only enrollments with assigned grades count. Enrollments where grade is `None` (in-progress) are excluded from GPA calculation but included in the credit load.

4. **What queries should the Gradebook answer?**
   
   From the Student direction:
   - What courses is this student in?
   - What is this student's GPA?
   - What is this student's total credit load?
   - Is this student on the honor roll? (GPA ≥ 3.5)
   
   From the Course direction:
   - Who's enrolled in this course?
   - What's the average grade in this course?
   - What's the grade distribution (how many A's, B's, C's)?
   
   Across both:
   - All students on the honor roll, sorted by GPA
   - All students failing any course (grade F), sorted by name
   - All courses in a department
   - Overall institution GPA

5. **How does the JSON structure look?**

   Since Enrollment is the association object, store all three collections separately:
   ```json
   {
       "students": [
           {"student_id": "S001", "first_name": "Alice", "last_name": "Smith", "email": "...", "major": "CS"}
       ],
       "courses": [
           {"course_code": "CS101", "name": "Intro to CS", "credits": 3, "department": "CS"}
       ],
       "enrollments": [
           {"student_id": "S001", "course_code": "CS101", "letter_grade": "A", "semester": "Spring 2026"}
       ]
   }
   ```
   
   When loading, reconstruct the three collections as separate lists. The Gradebook links them via ID/code lookups — the same way a database joins tables.

### Ask GLM-4.7-Flash Before Coding

`Cmd+L` → "Explain these Python concepts:

1. The relationship between `__eq__` and `__hash__` — why does Python make objects unhashable when you define `__eq__`? How do I define `__hash__` consistently with `__eq__`? What happens if I get this wrong?

2. How do you model a many-to-many relationship in Python using an association object (like a join table in a database)? Explain the concept and why it's better than having circular references between two classes.

3. How to compute a weighted average in Python — the formula and a simple code example with `sum()` and a list of tuples.

Explain each concept clearly with examples. Don't write my program."

### Skeletal Structure

Build bottom-up: data models → association object → persistence → business logic → presentation.

```python
import json
from functools import total_ordering
from collections import defaultdict
from pathlib import Path

GRADEBOOK_FILE = Path("gradebook.json")

GRADE_POINTS = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0
}

HONOR_ROLL_GPA = 3.5


# ──────────────────────────────────────
# DATA MODELS
# ──────────────────────────────────────

@total_ordering
class Student:
    """Represents a student. Identity = student_id.
    Natural ordering = alphabetical by last name, then first name.
    """

    def __init__(self, student_id: str, first_name: str, last_name: str,
                 email: str = "", major: str = "Undeclared"):
        # YOUR IMPLEMENTATION

    def __eq__(self, other) -> bool:
        # Equal if same student_id

    def __hash__(self) -> int:
        # Hash on student_id (consistent with __eq__)

    def __lt__(self, other) -> bool:
        # Alphabetical: (last_name, first_name)

    def __repr__(self) -> str:
        # Developer representation

    def __str__(self) -> str:
        # User representation: "Alice Smith (S001) — CS"

    @property
    def full_name(self) -> str:
        # "Alice Smith"

    def to_dict(self) -> dict:
        # JSON serialization

    @classmethod
    def from_dict(cls, data: dict):
        # JSON deserialization


@total_ordering
class Course:
    """Represents a course. Identity = course_code.
    Natural ordering = alphabetical by course_code.
    """

    def __init__(self, course_code: str, name: str, credits: int,
                 department: str = "General"):
        # YOUR IMPLEMENTATION

    def __eq__(self, other) -> bool:
        # Equal if same course_code

    def __hash__(self) -> int:
        # Hash on course_code

    def __lt__(self, other) -> bool:
        # Alphabetical by course_code

    def __repr__(self) -> str:
        # Developer representation

    def __str__(self) -> str:
        # User representation: "CS101: Intro to CS (3 credits)"

    def to_dict(self) -> dict:
        # JSON serialization

    @classmethod
    def from_dict(cls, data: dict):
        # JSON deserialization


class Enrollment:
    """The association between a Student and a Course.
    
    This is the 'join table' — it represents the fact that
    a specific student is enrolled in a specific course,
    with an optional grade and semester.
    
    Identity = (student_id, course_code) compound key.
    """

    def __init__(self, student_id: str, course_code: str,
                 letter_grade: str = None, semester: str = ""):
        # YOUR IMPLEMENTATION

    @property
    def grade_points(self):
        """Convert letter grade to numeric grade points.
        Returns None if no grade assigned yet (in-progress enrollment).
        """
        # Look up self.letter_grade in GRADE_POINTS dict
        # Return None if letter_grade is None

    def __eq__(self, other) -> bool:
        # Equal if same student_id AND same course_code

    def __hash__(self) -> int:
        # Hash on (student_id, course_code) tuple

    def __repr__(self) -> str:
        # Developer representation

    def __str__(self) -> str:
        # "S001 in CS101: A (Spring 2026)"

    def to_dict(self) -> dict:
        # JSON serialization

    @classmethod
    def from_dict(cls, data: dict):
        # JSON deserialization


# ──────────────────────────────────────
# DATA LAYER — persistence
# ──────────────────────────────────────

class GradebookStore:
    """Handles loading/saving all three collections to a single JSON file."""

    def __init__(self, filepath: Path = GRADEBOOK_FILE):
        self.filepath = filepath

    def load(self) -> tuple:
        """Load all data from JSON.
        Returns: (list[Student], list[Course], list[Enrollment])
        """
        # Handle missing file
        # Read JSON
        # Reconstruct each collection using from_dict()
        # Return three lists

    def save(self, students: list, courses: list, enrollments: list) -> None:
        """Save all three collections to JSON."""
        # Convert each collection to list of dicts
        # Write single JSON with "students", "courses", "enrollments" keys


# ──────────────────────────────────────
# BUSINESS LOGIC — the Gradebook as Mediator
# ──────────────────────────────────────

class Gradebook:
    """Manages students, courses, and the enrollments between them.
    
    This is the MEDIATOR — it manages the many-to-many relationship
    so that Student and Course never reference each other directly.
    
    All queries about 'which students are in which courses' go through
    the Gradebook, not through Student or Course objects.
    """

    def __init__(self, store: GradebookStore = None):
        self.store = store or GradebookStore()
        self.students, self.courses, self.enrollments = self.store.load()

    def _save(self):
        """Internal helper — save current state."""
        self.store.save(self.students, self.courses, self.enrollments)

    # ── Entity Management ────────────────

    def add_student(self, student: Student) -> bool:
        """Add a student. Reject if student_id already exists.
        Uses __eq__ on Student to check for duplicates.
        """
        # Check if student already in self.students (uses __eq__)
        # Append and save if new
        # Return True/False

    def add_course(self, course: Course) -> bool:
        """Add a course. Reject if course_code already exists."""
        # Same pattern as add_student

    def find_student(self, student_id: str):
        """Find a student by ID. Returns Student or None."""
        # Linear search — fine for small datasets

    def find_course(self, course_code: str):
        """Find a course by code. Returns Course or None."""
        # Linear search

    # ── Enrollment Management (the Mediator's core job) ────

    def enroll(self, student_id: str, course_code: str,
               semester: str = "") -> bool:
        """Enroll a student in a course.
        
        Validates:
          - Student exists
          - Course exists
          - Not already enrolled (checks Enrollment.__eq__)
        """
        # Validate both entities exist
        # Create Enrollment
        # Check for duplicate using __eq__
        # Append and save

    def assign_grade(self, student_id: str, course_code: str,
                     letter_grade: str) -> bool:
        """Assign or update a grade for an enrollment.
        
        Validates:
          - Enrollment exists
          - Grade is valid (exists in GRADE_POINTS)
        """
        # Find the enrollment
        # Validate grade string
        # Update and save

    def drop_course(self, student_id: str, course_code: str) -> bool:
        """Remove an enrollment. Returns True if found and removed."""
        # Find and remove the enrollment
        # Save

    # ── Queries from the Student direction ────

    def get_student_enrollments(self, student_id: str) -> list:
        """All enrollments for a student."""
        # Filter self.enrollments by student_id

    def get_student_courses(self, student_id: str) -> list:
        """All Course objects a student is enrolled in."""
        # Get enrollments → extract course_codes → find Course objects

    def calculate_gpa(self, student_id: str) -> float:
        """Calculate weighted GPA for a student.
        
        Only enrollments with assigned grades are included.
        Weight = course credit hours.
        
        Formula:
          sum(grade_points × credits) / sum(credits)
        
        Returns 0.0 if no graded enrollments exist.
        """
        # Get enrollments for this student
        # Filter to only those with a grade (letter_grade is not None)
        # For each graded enrollment:
        #   - Look up the course to get credits
        #   - Calculate grade_points × credits
        # Sum quality points / sum credits
        # Handle division by zero

    def get_student_credits(self, student_id: str) -> int:
        """Total credit hours a student is enrolled in."""
        # Sum credits of all enrolled courses

    def is_honor_roll(self, student_id: str) -> bool:
        """True if student's GPA >= HONOR_ROLL_GPA and has graded courses."""
        # Calculate GPA, compare to threshold

    # ── Queries from the Course direction ────

    def get_course_roster(self, course_code: str) -> list:
        """All Student objects enrolled in a course, sorted alphabetically.
        Uses Student.__lt__ for natural ordering.
        """
        # Get enrollments → extract student_ids → find Student objects
        # sorted() uses __lt__ automatically

    def get_course_average(self, course_code: str) -> float:
        """Average grade points in a course (simple average, not weighted)."""
        # Get enrollments for this course
        # Filter to graded only
        # Average the grade points
        # Handle empty case

    def get_grade_distribution(self, course_code: str) -> dict:
        """Count of each letter grade in a course.
        Returns: {"A": 3, "B+": 2, "C": 1, ...}
        """
        # Use collections.Counter or defaultdict

    # ── Cross-cutting queries ────

    def get_honor_roll(self) -> list:
        """All students on the honor roll, sorted by GPA descending.
        
        Uses key function for GPA-based sorting (not natural __lt__ ordering).
        """
        # Filter students where is_honor_roll is True
        # Sort by GPA descending using key=lambda

    def get_failing_students(self) -> list:
        """Students who have an F in any course."""
        # Find enrollments with grade "F"
        # Get unique students
        # Sort alphabetically (uses __lt__)

    def get_all_students_sorted(self, sort_by: str = "name") -> list:
        """Return all students sorted by specified criteria.
        
        Demonstrates multiple sort orders:
          'name' → uses natural __lt__ ordering
          'gpa'  → uses key function
          'id'   → uses key function
        """
        if sort_by == "name":
            return sorted(self.students)           # Uses __lt__
        elif sort_by == "gpa":
            return sorted(self.students,
                         key=lambda s: self.calculate_gpa(s.student_id),
                         reverse=True)
        elif sort_by == "id":
            return sorted(self.students,
                         key=lambda s: s.student_id)
        return sorted(self.students)


# ──────────────────────────────────────
# PRESENTATION
# ──────────────────────────────────────

class GradebookApp:
    def __init__(self):
        self.gradebook = Gradebook()

    def run(self):
        while True:
            print("\n--- Student Gradebook ---")
            print("1. Add student")
            print("2. Add course")
            print("3. Enroll student in course")
            print("4. Assign grade")
            print("5. View student transcript")
            print("6. View course roster")
            print("7. View all students (choose sort order)")
            print("8. Honor roll")
            print("9. Course grade distribution")
            print("10. Quit")

            choice = input("\nChoose: ").strip()
            # Route to methods

    def view_transcript(self):
        """Display a student's full academic record.
        
        Example output:
        
        ═══════════════════════════════════════
        TRANSCRIPT: Alice Smith (S001)
        Major: Computer Science
        ═══════════════════════════════════════
        
        Course           Credits  Grade  Points
        ───────────────────────────────────────
        CS101             3       A      12.0
        MATH201           4       B+     13.2
        ENG101            3       A-     11.1
        ───────────────────────────────────────
        Total Credits: 10
        Quality Points: 36.3
        GPA: 3.63
        Honor Roll: ✓
        ═══════════════════════════════════════
        """
        # Ask for student ID
        # Get student, enrollments, calculate GPA
        # Display formatted transcript

    def view_roster(self):
        """Display a course roster with grades.
        
        Example output:
        
        CS101: Intro to CS (3 credits)
        ───────────────────────────────
        Student              Grade
        ───────────────────────────────
        Alice Smith          A
        Bob Johnson          B+
        Charlie Davis        —  (in progress)
        ───────────────────────────────
        Class average: 3.65
        Enrolled: 3 students
        """
        # Ask for course code
        # Get roster (sorted by __lt__), enrollments
        # Display formatted roster

    def view_all_students(self):
        """Display all students with a user-chosen sort order.
        Demonstrates how __lt__ (name) and key functions (gpa, id) coexist.
        """
        # Ask: sort by (1) name, (2) GPA, (3) student ID
        # Call gradebook.get_all_students_sorted(sort_by=...)
        # Display with GPA for each

    # ... implement remaining menu methods


if __name__ == "__main__":
    app = GradebookApp()
    app.run()
```

### Understanding the Mediator in Action

Look at `view_transcript()` and trace how data flows:

```
User asks: "Show transcript for S001"
  → GradebookApp asks Gradebook for student S001
    → Gradebook searches self.students using Student.__eq__
  → GradebookApp asks Gradebook for enrollments for S001
    → Gradebook filters self.enrollments by student_id
  → GradebookApp asks Gradebook to calculate GPA for S001
    → Gradebook gets enrollments for S001
    → For each enrollment, Gradebook looks up the Course for credits
    → Gradebook computes weighted average
  → GradebookApp formats and displays the result
```

Notice: at no point does a Student object know about its Courses. At no point does a Course object know about its Students. The Gradebook mediates every query. This is clean, testable, and serializable — no circular references anywhere.

### Add Test Data After Building

Create a realistic dataset to test all your queries:

```
Students:
  S001 - Alice Smith, CS major
  S002 - Bob Johnson, Math major
  S003 - Charlie Davis, CS major
  S004 - Diana Lee, English major

Courses:
  CS101  - Intro to CS (3 credits, CS dept)
  CS201  - Data Structures (4 credits, CS dept)
  MATH201 - Linear Algebra (4 credits, Math dept)
  ENG101 - English Composition (3 credits, English dept)

Enrollments:
  Alice  → CS101 (A), CS201 (B+), MATH201 (A-), ENG101 (A)
  Bob    → MATH201 (A), CS101 (C+), ENG101 (B)
  Charlie → CS101 (B), CS201 (F), ENG101 (A-)
  Diana  → ENG101 (A+), MATH201 (B-), CS101 (B+)
```

Verify:
- Alice's GPA: (4.0×3 + 3.3×4 + 3.7×4 + 4.0×3) / (3+4+4+3) = 52.0/14 = **3.71** → Honor roll ✓
- Bob's GPA: (4.0×4 + 2.3×3 + 3.0×3) / (4+3+3) = 31.9/10 = **3.19** → Not honor roll
- Charlie's GPA: (3.0×3 + 0.0×4 + 3.7×3) / (3+4+3) = 20.1/10 = **2.01** → Not honor roll, failing CS201
- sorted(students) by name: Alice, Bob, Charlie, Diana (uses `__lt__`)
- sorted by GPA: Alice (3.71), Bob (3.19), Diana (?), Charlie (2.01)
- CS101 roster: Alice (A), Bob (C+), Charlie (B), Diana (B+) — sorted alphabetically by `__lt__`

### Ask GLM-4.7-Flash After Coding — The Review Step

Select all code → `Cmd+L` →

"Review this gradebook system as a senior developer. Specifically evaluate:

1. Is my many-to-many relationship correctly modeled? Does the Gradebook properly mediate between Students and Courses without either side referencing the other?
2. Are my `__eq__` and `__hash__` implementations consistent for each class? Would my objects work correctly in sets and as dictionary keys?
3. Is my GPA calculation correct — am I using weighted averages with credit hours as weights? Am I handling edge cases (no graded courses, all F's, zero credits)?
4. Is my `@total_ordering` setup correct on Student and Course? Does `sorted()` produce the right order?
5. How efficient are my queries? If I had 10,000 students and 500 courses, what would need to change? (Hint: the linear scans in `find_student` and `find_course` would need to become dictionary lookups.)
6. What would a senior developer change about this code?"

**Read the suggestions. Implement the changes yourself. Commit the improved version.**

```bash
git add . && git commit -m "Project 19: student_gradebook.py — many-to-many, mediator pattern, weighted GPA, __eq__/__hash__, @total_ordering"
```

---

## CLOSING LECTURE: RELATIONSHIPS ARE ARCHITECTURE

Today you learned that the hardest part of OOP isn't syntax — it's deciding how objects relate to each other. The many-to-many relationship between Students and Courses could have been modeled three ways. The wrong ways (circular references, one-sided ownership) create bugs, serialization nightmares, and confused responsibility. The right way (association object + mediator) is clean, testable, and scalable.

Here's the meta-lesson: **when you see two things that need to know about each other, introduce a third thing that knows about both.** This principle appears everywhere:

| Domain | Thing A | Thing B | The Mediator |
|--------|---------|---------|-------------|
| Gradebook | Student | Course | Enrollment |
| E-commerce | Customer | Product | Order |
| RAG system | Document | Query | Embedding/Retrieval |
| Kafka pipeline | Producer | Consumer | Topic/Partition |
| AI agents | Agent | Tool | ToolCall |

You already think in mediators professionally — a Kafka Topic mediates between producers and consumers. Today you implemented the same pattern in application code. When you write specs for AI in Week 3, identifying the mediator is one of your most valuable architectural decisions.

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 12
- [ ] Day number: 12
- [ ] Hours coded: 2
- [ ] Projects completed: 1 (student_gradebook)
- [ ] Key concepts: many-to-many relationships, association objects, mediator pattern, __eq__ + __hash__, weighted averages, compound keys, multiple sort orders
- [ ] AI review: What was the most useful suggestion? What change did you make?
- [ ] Mood/energy (1–5): ___

### Preview tomorrow (Day 13 — Friday):
- **Commute**: Talk Python To Me or Python Bytes
- **Evening (7:00–9:00 PM)**: `file_organizer.py`
  - Automatically organize files by type and date — your first program that interacts with the real filesystem
  - **New concepts**: `os`, `pathlib`, `shutil` — reading directories, moving files, creating folders, matching patterns
  - **OOP focus**: Objects that represent file system operations — rules, actions, and logging
  - Last weeknight project of Week 2!

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

1. **Many-to-many relationships** — when A maps to many B's and B maps to many A's, and the relationship itself carries data
2. **Association object pattern** — creating a third class (Enrollment) to represent the relationship, eliminating circular references
3. **Mediator pattern** — a class (Gradebook) that manages relationships so the participating classes (Student, Course) don't reference each other
4. **`__eq__` and `__hash__` consistency** — if you define `__eq__`, you must define `__hash__` using the same attributes, or objects won't work in sets/dicts
5. **Compound keys** — using a tuple of attributes `(student_id, course_code)` for both equality and hashing when identity requires multiple fields
6. **Weighted averages** — `sum(value × weight) / sum(weights)`, used for GPA and countless data engineering aggregations
7. **Grade point lookup tables** — using a dictionary as a mapping from letter grades to numeric values
8. **Natural ordering vs. query-specific ordering** — `__lt__` for one default sort, `key` functions for alternatives, demonstrated side by side
9. **Why circular references are dangerous** — data duplication, serialization crashes, split responsibility
10. **The "introduce a third thing" principle** — when two objects need to know about each other, create a mediator

---

**Day 12 of 365. Objects don't just exist — they relate. And the architecture of those relationships defines whether your system is clean or chaotic.** 🚀
