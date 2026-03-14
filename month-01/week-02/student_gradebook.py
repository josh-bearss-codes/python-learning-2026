import json
from functools import total_ordering
from collections import defaultdict, Counter
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
        self.student_id = student_id
        self.first_name =  first_name
        self.last_name = last_name
        self.email = email
        self.major = major

    def __eq__(self, other) -> bool:
        # Equal if same student_id
        if not isinstance(other, Student):
            return NotImplemented
        return self.student_id == other.student_id

    def __hash__(self) -> int:
        # Hash on student_id (consistent with __eq__)
        return hash(self.student_id)

    def __lt__(self, other) -> bool:
        # Alphabetical: (last_name, first_name)
        if not isinstance(other, Student):
            return NotImplemented
        return (self.last_name, self.first_name) < (other.last_name, other.first_name)

    def __repr__(self) -> str:
        # Developer representation
        return f"Student(student_id={self.student_id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, major={self.major})"

    def __str__(self) -> str:
        # User representation: "Alice Smith (S001) — CS"
        return f"{self.first_name} {self.last_name} ({self.student_id}) — {self.major}"

    @property
    def full_name(self) -> str:
        # "Alice Smith"
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> dict:
        # JSON serialization
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "major": self.major
        }

    @classmethod
    def from_dict(cls, data: dict):
        # JSON deserialization
        return cls(
            student_id=data["student_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            major=data["major"]
        )

@total_ordering
class Course:
    """Represents a course. Identity = course_code.
    Natural ordering = alphabetical by course_code.
    """

    def __init__(self, course_code: str, name: str, credits: int,
                 department: str = "General"):
        # YOUR IMPLEMENTATION
        self.course_code = course_code
        self.name = name
        self.credits = credits
        self.department = department

    def __eq__(self, other) -> bool:
        # Equal if same course_code
        if not isinstance(other, Course):
            return NotImplemented
        return self.course_code == other.course_code

    def __hash__(self) -> int:
        # Hash on course_code
        return hash(self.course_code)

    def __lt__(self, other) -> bool:
        # Alphabetical by course_code
        if not isinstance(other, Course):
            return NotImplemented
        return self.course_code < other.course_code

    def __repr__(self) -> str:
        # Developer representation
        return f"{self.__class__.__name__} (course_code={self.course_code}, name={self.name}, credits={self.credits}, department={self.department})"

    def __str__(self) -> str:
        # User representation: "CS101: Intro to CS (3 credits)"
        return f"{self.course_code}: {self.name} ({self.credits} credits)"

    def to_dict(self) -> dict:
        # JSON serialization
        return {
            "course_code": self.course_code,
            "name": self.name,
            "credits": self.credits,
            "department": self.department
        }

    @classmethod
    def from_dict(cls, data: dict):
        # JSON deserialization
        return cls(
            course_code=data["course_code"],
            name=data["name"],
            credits=data["credits"],
            department=data["department"]
        )


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
        self.student_id = student_id
        self.course_code = course_code
        self.letter_grade = letter_grade
        self.semester = semester

    @property
    def grade_points(self):
        """Convert letter grade to numeric grade points.
        Returns None if no grade assigned yet (in-progress enrollment).
        """
        # Look up self.letter_grade in GRADE_POINTS dict
        # Return None if letter_grade is None
        if self.letter_grade is None:
            return None
        return GRADE_POINTS.get(self.letter_grade, 0)  # Default to 0 if not found

    def __eq__(self, other) -> bool:
        # Equal if same student_id AND same course_code
        if not isinstance(other, Enrollment):
            return NotImplemented
        return (self.student_id, self.course_code) == (other.student_id, other.course_code)

    def __hash__(self) -> int:
        # Hash on (student_id, course_code) tuple
        return hash((self.student_id, self.course_code))

    def __repr__(self) -> str:
        # Developer representation
        return f"Enrollment(student_id={self.student_id}, course_code={self.course_code}, letter_grade={self.letter_grade}, semester={self.semester})"

    def __str__(self) -> str:
        # "S001 in CS101: A (Spring 2026)"
        return f"{self.student_id} in {self.course_code}: {self.letter_grade} ({self.semester})"

    def to_dict(self) -> dict:
        # JSON serialization
        return {
            "student_id": self.student_id,
            "course_code": self.course_code,
            "letter_grade": self.letter_grade,
            "semester": self.semester
        }

    @classmethod
    def from_dict(cls, data: dict):
        # JSON deserialization
        return cls(
            student_id=data["student_id"],
            course_code=data["course_code"],
            letter_grade=data["letter_grade"],
            semester=data["semester"]
        )


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
        if not self.filepath.exists():
            return [], [], []
        data = json.loads(self.filepath.read_text())
        students = [Student.from_dict(d) for d in data["students"]]
        courses = [Course.from_dict(d) for d in data["courses"]]
        enrollments = [Enrollment.from_dict(d for d in data["enrollments"])]
        return students, courses, enrollments

    def save(self, students: list, courses: list, enrollments: list) -> None:
        """Save all three collections to JSON."""
        # Convert each collection to list of dicts
        # Write single JSON with "students", "courses", "enrollments" keys
        data = {
            "students": [s.to_dict() for s in students],
            "courses": [c.to_dict() for c in courses],
            "enrollments": [e.to_dict() for e in enrollments]
        }
        self.filepath.write_text(json.dumps(data, indent=2))


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
        
        # Build lookup dictionaries for quick lookup
        self._student_by_id = {s.student_id: s for s in self.students}
        self.course_by_code = {c.course_code: c for c in self.courses}

        # Index enrollments by student and course
        self._enrollments_by_student = defaultdict(list)
        self._enrollments_by_course = defaultdict(list)
        for e in self.enrollments:
            self._enrollments_by_student[e.student_id].append(e)
            self._enrollments_by_course[e.course_id].append(e)

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
        if student in self.students:
            return False
        self.students.append(student)
        self._save()
        return True

    def add_course(self, course: Course) -> bool:
        """Add a course. Reject if course_code already exists."""
        # Same pattern as add_student
        if course in self.courses:
            return False
        self.courses.append(course)
        self._save()
        return True

    def find_student(self, student_id: str):
        """Find a student by ID. Returns Student or None."""
        # Linear search — fine for small datasets
        # Return Student or None
        return self._student_by_id.get(student_id)

    def find_course(self, course_code: str):
        """Find a course by code. Returns Course or None."""
        # Linear search
        return self._course_by_code.get(course_code)

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
        if not self.find_student(student_id):
            return False
        if not self.find_course(course_code):
            return False
        enrollment = Enrollment(student_id, course_code, semester)
        if enrollment in self.enrollments:
            return False
        self.enrollments.append(enrollment)
        self.save()
        return True

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
        if not self.find_enrollment(student_id, course_code):
            return False
        if letter_grade not in GRADE_POINTS:
            return False
        enrollment = self.find_enrollment(student_id, course_code)
        enrollment.letter_grade = letter_grade
        enrollment.save()
        return True

    def drop_course(self, student_id: str, course_code: str) -> bool:
        """Remove an enrollment. Returns True if found and removed."""
        # Find and remove the enrollment
        # Save
        if not self.find_enrollment(student_id, course_code):
            return False
        enrollment = self.find_enrollment(student_id, course_code)
        enrollment.delete()
        self.save()
        return True
    
    def find_enrollment(self, student_id: str, course_code: str, semester: str = ""):
    
        """Find enrollment by student_id, course_code, and optional semester."""
        for enrollment in self.enrollments:
            if (enrollment.student_id == student_id and 
                enrollment.course_code == course_code and
                (not semester or enrollment.semester == semester)):
                return enrollment
        return None

    # ── Queries from the Student direction ────

    def get_student_enrollments(self, student_id: str) -> list:
        """All enrollments for a student."""
        # Filter self.enrollments by student_id
        # Return list of Enrollment objects
        return self._enrollments_by_student.get(student_id, [])

    def get_student_courses(self, student_id: str) -> list:
        """All Course objects a student is enrolled in."""
        # Get enrollments → extract course_codes → find Course objects
        return [self.find_course(enrollment.course_code) for enrollment in self.get_student_enrollments(student_id)]

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
        enrollments = self.get_student_enrollments(student_id)
        total_quality_points = 0.0
        total_credits = 0

        for enrollment in enrollments:
            if enrollment.letter_grade is None:
                continue
            course = self.find_course(enrollment.course_code)
            grade_points = enrollment.grade_points
            if grade_points is None:
                continue
            # Calculate quality points for this enrollment
            total_quality_points += grade_points * course.credits
            total_credits += course.credits

        if total_credits == 0:
            return 0.0
        return round(total_quality_points / total_credits, 2)

    def get_student_credits(self, student_id: str) -> int:
        """Total credit hours a student is enrolled in."""
        # Sum credits of all enrolled courses
        enrollments = self.get_student_enrollments(student_id)
        total_credits = 0
        for enrollment in enrollments:
            course = self.find_course(enrollment.course_code)
            total_credits += course.credits
        return total_credits

    def is_honor_roll(self, student_id: str) -> bool:
        """True if student's GPA >= HONOR_ROLL_GPA and has graded courses."""
        # Calculate GPA, compare to threshold
        gpa = self.calculate_gpa(student_id)
        if gpa < HONOR_ROLL_GPA:
            return False        
        
        # Check if student has any graded courses
        enrollments = self.get_student_enrollments(student_id)
        for enrollment in enrollments:
            if enrollment.letter_grade is not None:
                return True
        return False
        

    # ── Queries from the Course direction ────

    def get_course_roster(self, course_code: str) -> list:
        """All Student objects enrolled in a course, sorted alphabetically.
        Uses Student.__lt__ for natural ordering.
        """
        # Get enrollments → extract student_ids → find Student objects
        # sorted() uses __lt__ automatically
        enrollments = self.get_student_enrollments(course_code)
        students = sorted([self.find_student(student_id) for student_id in enrollments])
        return students

    def get_course_average(self, course_code: str) -> float:
        """Average grade points in a course (simple average, not weighted)."""
        # Get enrollments for this course
        # Filter to graded only
        # Average the grade points
        # Handle empty case
        enrollments = self.get_student_enrollments(course_code)
        grades = [enrollment.letter_grade for enrollment in enrollments if enrollment.grade is not None]
        if not grades:
            return 0.0
        return sum(grades) / len(grades)

    def get_grade_distribution(self, course_code: str) -> dict:
        """Count of each letter grade in a course.
        Returns: {"A": 3, "B+": 2, "C": 1, ...}
        """
        # Use collections.Counter or defaultdict
        enrollments = self.get_student_enrollments(course_code)
        grades = [enrollment.grade for enrollment in enrollments]
        return Counter(grades) or defaultdict(int)

    # ── Cross-cutting queries ────

    def get_honor_roll(self) -> list:
        """All students on the honor roll, sorted by GPA descending.
        
        Uses key function for GPA-based sorting (not natural __lt__ ordering).
        """
        # Filter students where is_honor_roll is True
        # Sort by GPA descending using key=lambda
        students = [student for student in self.students if student.is_honor_roll]
        return sorted(students, key=lambda student: student gpa, reverse=True)

    def get_failing_students(self) -> list:
        """Students who have an F in any course."""
        # Find enrollments with grade "F"
        # Get unique students
        # Sort alphabetically (uses __lt__)
        enrollments = [enrollment for enrollment in self.enrollments if enrollment.grade == "F"]
        students = {enrollment.student_id for enrollment in enrollments}
        return sorted(students) 

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
            if choice == "1":
                self.add_student_prompt()
            elif choice == "2":
                self.add_course_prompt()
            elif choice == "3":
                self.enroll_student_prompt()
            elif choice == "4":
                self.assign_grade_prompt()
            elif choice == "5":
                self.view_transcript()
            elif choice == "6":
                self.view_roster()
            elif choice == "7":
                self.view_all_students()
            elif choice == "8":
                self.gradebook.get_honor_roll()
            elif choice == "9":
                self.course_grade_distribution()
            elif choice == "10":
                break
            else:
                print("Invalid choice. Please try again.")

    def add_student_prompt(self):
        """Prompt the user to add a student.
        # YOUR IMPLEMENTATION
        self.student_id = student_id
        self.first_name =  first_name
        self.last_name = last_name
        self.email = email
        self.major = major
        """
        student_id = input("Enter student ID: ")
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        email = input("Enter email: ")
        major = input("Enter major: ")
        student = Student(student_id, first_name, last_name, email, major)
        self.gradebook.add_student(student)
        self.gradebook._save()
        print(f"Student {student_id} added successfully to the gradebook.")
        return

    def add_course_prompt(self):
        """Prompt the user to add a course.
        # YOUR IMPLEMENTATION
        self.course_code = course_code
        self.name = name
        self.credits = credits
        self.department = department
        """
        course_code = input("Enter course code: ")
        name = input("Enter course name: ")
        credits = input("Enter number of credits: ")
        department = input("Enter department: ")
        course = Course(course_code, name, credits, department)
        self.gradebook.add_course(course)
        self.gradebook._save()
        print(f"Course {course_code} added successfully to the gradebook.")
        return
    
    def enroll_student_prompt(self):
        """Prompt the user to enroll a student in a course.
        # YOUR IMPLEMENTATION
        def enroll(self, student_id: str, course_code: str,
               semester: str = "") -> bool:
        Enroll a student in a course.
        """
        student_id = input("Enter student ID: ")
        course_code = input("Enter course code: ")
        semester = input("Enter semester (optional): ")
        if self.gradebook.enroll(student_id, course_code, semester):
            print(f"Student {student_id} enrolled in course {course_code} successfully.")
            return True
        else:
            print(f"Failed to enroll student {student_id } in course {course_code}.")
            return False
        
    def assign_grade_prompt(self):
        """Prompt the user to assign a grade to a student in a course.
        # YOUR IMPLEMENTATION
        def assign_grade(self, student_id: str, course_code: str,
                     letter_grade: str) -> bool:
        Assign or update a grade for an enrollment.
        
        Validates:
          - Enrollment exists
          - Grade is valid (exists in GRADE_POINTS)
        """
        student_id = input("Enter student ID: ")
        course_code = input("Enter course code: ")
        letter_grade = input("Enter letter grade: ")
        if self.gradebook.assign_grade(student_id, course_code, letter_grade):
            print(f"Grade {letter_grade} assigned to student {student_id} in course {course_code} successfully.")
            return True
        else:
            print(f"Failed to assign grade {letter_grade} to student {student_id} in course {course_code}.")
            return False

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
        # Display student's name, major, and transcript details
        # Calculate GPA, total credits, quality points
        # Check if student is on honor roll
             
        student_id = input("Enter student ID: ")
        student = self.gradebook.find_student(student_id)
        if not student:
            print("Student not found.")
            return
        
        enrollments = self.gradebook.get_student_enrollments(student_id)
        if not enrollments:
            print("No enrollments found for this student.")
            return
        
        gpa = self.gradebook.calculate_gpa(enrollments)
        total_credits = self.gradebook.get_student_credits(student_id)
        honor_roll = self.gradebook.is_honor_roll(student_id)

        print("="*80)
        print("TRANSCRIPT: {student.full_name} ({student_id})")
        print("Major:  {student.major}")
        print("="*80)
        print()
        print(f"{'Course':<15} {'Credits':>8} {'Grade':>6} {'Points':>8}")
        print("-" * 80)        
        total_quality_points = 0.0
        for enrollment in enrollments:
            course = self.gradebook.find_course(enrollment.course_code)
            if course is None:
                continue
            grade = enrollment.letter_grade or "—"
            grade_points = enrollment.grade_points or 0.0
            quality_points = grade_points * course.credits
            total_quality_points += quality_points

            print(f"{enrollment.course_code:<15} {course.credits:>8} {grade:>6} {quality_points:>8.1f}")

        print("="*80)
        print("Total Credits: {total_credits}")
        print("Quality Points: {total_quality_points:.1f}")
        print("GPA: {gpa:.2f}")
        print(f"Honor Roll: {'✓' if honor_roll else '✗'}")
        print("="*80)

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
        # Display class average
        # Display number of students enrolled
        course_code = input("Enter course code: ")
        course = self.gradebook.find_course(course_code)
        roster = self.gradebook.get_course_roster()
        enrollments = self.gradebook.get_student_enrollments()
        print(f"{course_code}: {course.course_name} ({course.credits})")
        print("──────────────────────────────────────")
        print("Student              Grade")
        print("──────────────────────────────────────")
        for student in sorted(roster):
            print(f"{student.name:<20} {student.grade}")
        print("──────────────────────────────────────")
        print(f"Class average: {self.gradebook.get_course_average():.2f}")
        if student.id in enrollments:
            print(f"Enrolled: {enrollments}")
        return

    def view_all_students(self):
        """Display all students with a user-chosen sort order.
        Demonstrates how __lt__ (name) and key functions (gpa, id) coexist.
        """
        # Ask: sort by (1) name, (2) GPA, (3) student ID
        # Call gradebook.get_all_students_sorted(sort_by=...)
        # Display with GPA for each
        sort_by = input("Sort by (1) name, (2) GPA, (3) student ID: ")
        if sort_by == "1":
            students = self.gradebook.get_all_students_sorted(sort_by="name")
        elif sort_by == "2":
            students = self.gradebook.get_all_students_sorted(sort_by="gpa")
        elif sort_by == "3":
            students = self.gradebook.get_all_students_sorted(sort_by="id")
        else:
            print("Invalid sort option.")
        for student in students:
            print(f"{student.name} - GPA: {student.gpa:.2f}")

    # ... implement remaining menu methods

if __name__ == "__main__":
    app = GradebookApp()
    app.run()