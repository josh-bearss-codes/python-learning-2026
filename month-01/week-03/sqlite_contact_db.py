import sqlite3
from pathlib import Path
from datetime import date

DB_FILE = Path("contacts.db")


# ──────────────────────────────────────
# DATA LAYER — Database operations
# ──────────────────────────────────────

class ContactDatabase:
    """SQLite database manager for contacts with phone numbers.
    
    Manages the connection lifecycle and provides CRUD operations.
    Uses context manager pattern (with statement) for safe connection handling.
    
    Two tables:
      contacts — core contact info (name, email, city, notes, date_added)
      phone_numbers — multiple phones per contact (type, number, contact_id FK)
    
    Foreign keys enabled. Cascade delete on contact removal.
    Row factory set to sqlite3.Row for named column access.
    """

    def __init__(self, db_path: Path = DB_FILE):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a new connection with proper settings.
        
        Always:
        - Enable foreign keys (PRAGMA foreign_keys = ON)
        - Set row_factory to sqlite3.Row for named access
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if they don't exist.
        
        Called once on initialization.
        Uses IF NOT EXISTS so it's safe to call multiple times.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE,
                        city TEXT,
                        notes TEXT DEFAULT '',
                        date_added TEXT DEFAULT (date('now'))
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS phone_numbers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        contact_id INTEGER NOT NULL,
                        phone_type TEXT NOT NULL DEFAULT 'cell',
                        number TEXT NOT NULL,
                        FOREIGN KEY (contact_id) REFERENCES contacts(id) 
                            ON DELETE CASCADE
                    )
                """)

        except Exception as e:
            raise ValueError(f"Error adding contact: {e}")
        finally:
            cursor.close()

    # ── Create ────────────────────────────

    def add_contact(self, name: str, email: str = None,
                    city: str = None, notes: str = "",
                    phones: list | None = None) -> int:
        """Add a new contact with optional phone numbers.
        
        This is a TRANSACTION: both the contact and all phone numbers
        are inserted together. If any insert fails, nothing is saved.
        
        Args:
            name: Contact name (required)
            email: Email address (must be unique if provided)
            city: City name
            notes: Free text notes
            phones: List of (phone_type, number) tuples
                    e.g., [("cell", "555-0100"), ("work", "555-0200")]
        
        Returns:
            The new contact's ID
        
        Raises:
            sqlite3.IntegrityError: if email already exists
        """
        # INSERT into contacts
        # Get the new contact's ID with cursor.lastrowid
        # INSERT each phone number with that contact_id
        # Commit the transaction
        # Return the new ID
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                            """
                            INSERT INTO contacts (name, email, city, notes) VALUES (?, ?, ?, ?)
                            """, (name, email, city, notes))

                contact_id = cursor.lastrowid
                if phones is None:
                    phones = []
                for phone in phones:
                    phone_type, number = phone
                    cursor.execute(
                                """
                                INSERT INTO phone_numbers (contact_id, phone_type, number) VALUES (?, ?, ?)
                                """, (contact_id, phone_type, number))
                return contact_id
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError("Email already exists")
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Error adding contact: {e}")
        finally:
            cursor.close()

    def add_phone(self, contact_id: int, phone_type: str, number: str) -> int:
        """Add a phone number to an existing contact.
        
        Returns the new phone number's ID.
        Raises ValueError if contact_id doesn't exist.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                               INSERT INTO phone_numbers (contact_id, phone_type,)
                               VALUES (?, ?, ?)
                               """, (contact_id, phone_type, number))
            return cursor.lastrowid

        except Exception as e:
            conn.rollback()
            raise ValueError(f"Error adding phone number: {e}")
        finally:
            cursor.close()

    # ── Read ──────────────────────────────

    def get_contact(self, contact_id: int) -> dict:
        """Get one contact with all their phone numbers.
        
        Uses a JOIN to fetch both contact info and phone numbers
        in a single query. Then groups the results into a dict.
        
        Returns:
            {
                "id": 1,
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "city": "Denver",
                "notes": "",
                "date_added": "2026-03-19",
                "phones": [
                    {"type": "cell", "number": "555-0100"},
                    {"type": "work", "number": "555-0200"},
                ]
            }
            
        Returns None if contact not found.
        """
        # SELECT contacts + phone_numbers with JOIN
        # Group results (multiple rows for multiple phones)
        # Return structured dict
        try:
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
                contact_row = cursor.fetchone()
                if not contact_row:
                    return None

                contact = dict(contact_row)
                cursor.execute("SELECT phone_type, number FROM phone_numbers WHERE contact_id = ?", (contact_id,))
                contact["phones"] = [{"type": r["phone_type"], "number": r["number"]} for r in cursor.fetchall()]

            return contact
        
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
        
    def list_contacts(self) -> list:
        """List all contacts with phone count.
        
        Uses a LEFT JOIN + GROUP BY to count phones per contact.
        Returns list of dicts with name, email, city, phone_count.
        
        LEFT JOIN (not regular JOIN) because we want contacts
        that have zero phone numbers to appear too.
        
        SQL:
            SELECT contacts.*, COUNT(phone_numbers.id) as phone_count
            FROM contacts
            LEFT JOIN phone_numbers ON contacts.id = phone_numbers.contact_id
            GROUP BY contacts.id
            ORDER BY contacts.name
        """

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT contacts.*, COUNT(phone_numbers.id) as phone_count
                FROM contacts
                LEFT JOIN phone_numbers ON contacts.id = phone_numbers.contact_id
                GROUP BY contacts.id
                ORDER BY contacts.name
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append({
                        "id": row["id"],
                        "name": row["name"],
                        "email": row["email"],
                        "city": row["city"],
                        "phone_count": row["phone_count"]
                    })
            return results
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
        finally:
            cursor.close()
        
    def search_contacts(self, query: str) -> list:
        """Search contacts by name (case-insensitive partial match).
        
        Uses SQL LIKE with wildcards:
            WHERE name LIKE '%query%'
        
        The % means "any characters before/after the query."
        """
        # Use: WHERE name LIKE ? with parameter f"%{query}%"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                sql = """
                SELECT id, name, city, email 
                FROM contacts
                WHERE name LIKE ?
                """
                
                cursor.execute(sql, (f"%{query}%",))
                rows = cursor.fetchall()
                results = []
                
                for row in rows:
                    results.append({
                        "name": row[1],
                        "city": row[2],
                        "email": row[3]
                        })

            return results
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
        finally:
            cursor.close()        

    def filter_by_city(self, city: str) -> list:
        """Get all contacts in a specific city."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = """
                SELECT id, name, city, email 
                FROM contacts
                WHERE city = ?
                """
                cursor.execute(query, (city,))
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append({
                        "name": row[1],
                        "city": row[2],
                        "email": row[3]
                        })
            
            return results
        
        except Exception as e:
            print(f"Error occurred {e}")    
            return None
        finally:
            cursor.close()

    def get_city_counts(self) -> list:
        """Count contacts per city.
        
        SQL:
            SELECT city, COUNT(*) as count 
            FROM contacts 
            WHERE city IS NOT NULL
            GROUP BY city 
            ORDER BY count DESC
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = """
                SELECT city, COUNT(*) as count 
                FROM contacts 
                WHERE city IS NOT NULL
                GROUP BY city 
                ORDER BY count DESC
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append({
                        "city": row[0],
                        "count": row[1]
                        })
            
            return results
        except Exception as e:
            print(f"Error occurred {e}")
            return None
        finally:
            cursor.close()
            
    # ── Update ────────────────────────────

    def update_contact(self, contact_id: int, **kwargs) -> bool:
        """Update one or more fields on a contact.
        
        Uses **kwargs to accept any combination of fields:
            update_contact(1, name="Alice B.", city="Boulder")
        
        Builds the SQL dynamically:
            UPDATE contacts SET name = ?, city = ? WHERE id = ?
        
        Only allows updating valid columns to prevent SQL injection.
        """
        valid_columns = {"name", "email", "city", "notes"}
        # Filter kwargs to only valid columns
        # Build SET clause dynamically
        # Execute with parameterized values
        # Return True if a row was updated (cursor.rowcount > 0)
        # Return False if no row was updated
        # Return False if no row was deleted
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                valid_columns = {"name", "email", "city", "notes"}
                update_fields = {k: v for k, v in kwargs.items() if k in valid_columns}
                if not update_fields:
                    return False  # nothing to update
                set_clause = ", ".join([f"{col} = ?" for col in update_fields.keys()])
                query = f"UPDATE contacts SET {set_clause} WHERE id = ?"
                cursor.execute(query, (*update_fields.values(), contact_id))

            if cursor.rowcount > 0:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()

    def update_phone(self, phone_id: int, phone_type: str = None,
                     number: str = None) -> bool:
        """Update a phone number's type or number."""
        # Similar to update_contact, but for phones
        # Use phone_type and number as kwargs
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                kwargs = {'phone_type': phone_type, 'number': number}
                valid_columns = ['phone_type', 'number']
                update_fields = {k: v for k, v in kwargs.items() if k in valid_columns}
                if not update_fields:
                    return False  # nothing to update
                set_clause = ", ".join([f"{col} = ?" for col in update_fields.keys()])
                query = f"UPDATE phone_numbers SET {set_clause} WHERE id = ?"
                cursor.execute(query, (*update_fields.values(), phone_id))
                
                if cursor.rowcount > 0:
                    return True
                else:
                    return False
                
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()

    # ── Delete ────────────────────────────

    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact and all their phone numbers.
        
        Phone numbers are automatically deleted via ON DELETE CASCADE.
        Returns True if a contact was actually deleted.
        """
        # DELETE FROM contacts WHERE id = ?
        # Check cursor.rowcount > 0
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "DELETE FROM contacts WHERE id = ?"
                cursor.execute(query, (contact_id,))
                if cursor.rowcount > 0:
                    return True
                else:
                    return False
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()

    def delete_phone(self, phone_id: int) -> bool:
        """Delete a single phone number."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "DELETE FROM phone_numbers WHERE id = ?"
                cursor.execute(query, (phone_id,))

                if cursor.rowcount > 0:
                    return True
                else:
                    return False
                
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()

    # ── Statistics ────────────────────────

    def get_stats(self) -> dict:
        """Database statistics.
        
        Returns:
            total_contacts, total_phones, contacts_with_email,
            contacts_without_phones, cities_represented
        
        Each stat is a single SQL query.
        """
        queries = {
            "total_contacts": "SELECT COUNT(*) FROM contacts",
            "total_phones": "SELECT COUNT(*) FROM phone_numbers",
            "contacts_with_email": "SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL",
            "contacts_without_phones": "SELECT COUNT(*) FROM contacts WHERE id NOT IN (SELECT DISTINCT contact_id FROM phone_numbers)",
            "cities_represented": "SELECT COUNT(DISTINCT city) FROM contacts WHERE city IS NOT NULL"
        }
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                results = {}
                for label, sql in queries.items():
                    cursor.execute(sql)
                    results[label] = cursor.fetchone()[0]
                return results
                
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return None
        except TypeError:
            print("Invalid input. Please enter a valid number.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            cursor.close()
# ──────────────────────────────────────
# PRESENTATION
# ──────────────────────────────────────

class ContactApp:
    """Terminal interface for the contact database."""

    def __init__(self):
        self.db = ContactDatabase()

    def run(self):
        """Main menu loop."""
        while True:
            print("\n--- Contact Database ---")
            print("1. Add contact")
            print("2. View contact")
            print("3. List all contacts")
            print("4. Search contacts")
            print("5. Update contact")
            print("6. Delete contact")
            print("7. Add phone number")
            print("8. Filter by city")
            print("9. Statistics")
            print("10. Quit")

            choice = input("\nChoose: ").strip()
            # Route to methods
            if choice == "1":
                self.add_contact_prompt()
            elif choice == "2":
                self.view_contact_prompt()
            elif choice == "3":
                self.list_contacts_prompt()
            elif choice == "4":
                self.search_prompt()
            elif choice == "5":
                self.update_contact_prompt()
            elif choice == "6":
                self.delete_contact_prompt()
            elif choice == "7":
                self.add_phone_prompt()
            elif choice == "8":
                self.filter_by_city_prompt()
            elif choice == "9":
                self.stats_prompt()
            elif choice == "10":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def add_contact_prompt(self):
        """Gather contact info from user.
        
        Get name (required), email (optional), city (optional).
        Then ask: "Add phone numbers? (y/n)"
        Loop collecting (type, number) pairs until user says done.
        
        Handle IntegrityError if email already exists.
        """
        name = input("Enter contact's name: ")
        email = input("Enter contact's email (optional): ")
        city = input("Enter contact's city (optional): ")
        notes = input("Enter any notes (optional): ")
        phones = []
        add_phone_number = input("Add phone numbers? (y/n): ")

        while add_phone_number.lower() == "y":
            type = input("Enter phone type (e.g., home, work): ")
            number = input("Enter phone number: ")
            phones.append((type, number))
            add_phone_number = input("Add another phone number (y/n): ")
        self.db.add_contact(name, email or "", city or "", notes or "", phones or [])

        return

    def view_contact_prompt(self):
        """Display one contact with all phone numbers.
        
        Ask for contact ID or search by name.
        Display full contact card with all phones.
        """
        contact_id = input("Enter contact ID or search by name: ")
        if contact_id.isdigit():
            contact = self.db.get_contact(int(contact_id))
            print(contact)
            print("Phones:")
            for phone in contact.phones:
                print(f"  {phone.type}: {phone.number}")
        else:
            contact = self.db.search_contacts(contact_id)
            if contact:
                print(contact)
                print("Phones:")
                for phone in contact.phones:
                    print(f"  {phone.type}: {phone.number}")
        
        return


    def list_contacts_prompt(self):
        """Display all contacts in a table format.
        
        ┌────┬──────────────────┬──────────────────┬─────────┬────────┐
        │ ID │ Name             │ Email            │ City    │ Phones │
        ├────┼──────────────────┼──────────────────┼─────────┼────────┤
        │  1 │ Alice Johnson    │ alice@email.com  │ Denver  │      3 │
        │  2 │ Bob Smith        │ bob@email.com    │ Austin  │      1 │
        │  3 │ Carol White      │ None             │ Denver  │      0 │
        └────┴──────────────────┴──────────────────┴─────────┴────────┘
        """
        print("Listing all contacts:")
        print("-────────────────────────────────────────────────────────────────────────────────")
        print("ID | Name             | Email            | City    | Phones ")
        for contact in self.db.list_contacts():
            print(f"{contact['id']} | {contact['name']} | {contact['email']} | {contact['city']} | {len(contact['phones'])}")
            print("\n")
        print("-────────────────────────────────────────────────────────────────────────────────")

        return
        

    def search_prompt(self):
        """Search by name and display matching contacts."""
        print("Search for a contact by name:")
        name = input("Enter the name to search for :")
        for contact in self.db.search_contacts(name):
            print(f"{contact.id} | {contact.name} | {contact.email} | {contact.city} | {len(contact.phones)}")

        return
    
    def update_contact_prompt(self):
        """Update a contact's info.
        
        Show current values, ask which to change.
        Use the **kwargs pattern in update_contact().
        """
        print("Update a contact's info:")
        contact_id = input("Enter the contact ID to update: ")
        contact = self.db.get_contact(contact_id)
        if contact:
            print(f"Current contact info: {contact}")
            new_info = {}
            for field in ["name", "email", "city"]:
                new_value = input(f"Enter new {field} (leave blank to keep current): ")
                if new_value:
                    new_info[field] = new_value
                    self.db.update_contact(contact_id, **new_info)
        return

    def delete_contact_prompt(self):
        """Delete a contact with confirmation.
        
        Show the contact's name and phone count before asking "Are you sure?"
        Mention that phone numbers will be deleted too (cascade).
        """
        print("Delete a contact:")
        contact_id = input("Enter the contact ID to delete: ")
        contact = self.db.get_contact(contact_id)
        if contact:
            print(f"Current contact info: {contact}")
            if input("Are you sure? (y/n): ").lower() == 'y':
                self.db.delete_contact(contact_id)
                print("Contact and associated phone numbers deleted.")
            else:
                print("Deletion cancelled.")
        return

    def add_phone_prompt(self):
        """Add a phone number to an existing contact.
        
        Ask for contact ID (or search by name), phone type, number.
        """
        print("Add a phone number:")
        contact_id = input("Enter the contact ID to add a phone number: ")
        if contact := self.db.get_contact(contact_id):
            print(f"Current contact info: {contact}")
            phone_type = input("Enter the phone type (home, work, mobile): ")
            phone_number = input("Enter the phone number: ")
            self.db.add_phone(contact_id, phone_type, phone_number)

    def filter_by_city_prompt(self):
        """Show city counts, let user pick a city, show contacts in that city."""
        print("Filter contacts by city:")
        city_counts = self.db.get_city_counts()
        for item in city_counts:
            print(f"{city}: {item}")
            city = input("Enter the city to filter by city: ")
            if contacts := self.db.filter_by_city(city=city):
                print(f"Contacts in {city}:")
                for contact in contacts:
                    print(f"  {contact['name']}")
            else:
                print(f"No contacts found in {city}.")
        return

    def stats_prompt(self):
        """Display database statistics."""
        print("Database Statistics:")
        stats = self.db.get_stats()
        for label, value in stats.items():
            print(f"{label.replace('_', ' ').title()}: {value}")
        return

    # ── Display Helpers ───────────────────

    def display_contact_card(self, contact: dict):
        """Formatted display of one contact with phones.
        
        ═══════════════════════════════════════
        ALICE JOHNSON
        ═══════════════════════════════════════
        Email: alice@example.com
        City:  Denver
        Added: 2026-03-19
        
        Phone Numbers:
          📱 cell: 555-0100
          💼 work: 555-0200
          🏠 home: 555-0102
        
        Notes: Met at PyCon 2026
        ═══════════════════════════════════════
        """

        # Display the contact's name and other details
        print(f"{'═'*40}")
        print(f"{contact['name']}")
        print(f"{'═'*40}")
        print(f"Email: {contact.get('email', 'N/A')}")
        print(f"City:  {contact.get('city', 'N/A')}")
        print(f"Added: {contact.get('added', 'N/A')}")
        print('\n')
        print("Phone Numbers:")
        for label, number in contact.get('phone_numbers', {}).items():
            print(f"  {label}: {number}")
        print(f"Notes: {contact.get('notes', 'N/A')}")
        print(f"{'═'*40}")

        return

    def display_contact_row(self, contact, index: int = None):
        """One-line display for list views."""
        if index is not None:
            print(f"{index + 1}. {contact['name']}")
        else:
            print(f"{contact['name']}")

        return


if __name__ == "__main__":
    app = ContactApp()
    app.run()