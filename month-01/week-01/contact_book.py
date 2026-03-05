import json

CONTACTS_FILE = "contacts.json"

def load_contacts():
    try:
        with open(CONTACTS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        # Return empty contacts if JSON is corrupted
        print("Warning: Contacts file is corrupted. Starting with empty contact book.")
        return {}
    
def save_contacts(contacts):
    try:
        with open(CONTACTS_FILE, 'w') as file:
            json.dump(contacts, file, indent=4)
        return True
    except Exception as e:
        print(f"Error saving contacts: {e}")
        return False

def add_contact(contacts, name, phone, email):
    if name in contacts:
        return False
    contacts[name] = {
        "phone": phone,
        "email": email
        }
    return True

def view_contact(contacts, name):
    return contacts.get(name, None)

def search_contacts(contacts, keyword):
    results = {}
    for name, contact in contacts.items():
        if (keyword.lower() in name.lower() 
            or keyword.lower() in contact["phone"].lower() 
            or keyword.lower() in contact["email"].lower()):
            results[name] = contact
    return results  # Moved outside the loop

def delete_contact(contacts, name):
    if name in contacts:
        del contacts[name]
        return True
    return False

def main():
    contacts = load_contacts()
    
    while True:
        print("\nContact Book")
        print("1. Add Contact")
        print("2. View Contact")
        print("3. Search Contacts")
        print("4. Delete Contact")
        print("5. Exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            name = input("Enter name: ").strip()
            phone = input("Enter phone number: ").strip()
            email = input("Enter email: ").strip()
            
            if not name:
                print("Name cannot be empty.")
                continue
                
            if add_contact(contacts, name, phone, email):
                save_contacts(contacts)  # Save after adding
                print("Contact added successfully.")
            else:
                print("Contact already exists.")
        
        elif choice == '2':
            name = input("Enter name: ").strip()
            contact = view_contact(contacts, name)
            if contact:
                print(f"Name: {name}")
                print(f"Phone: {contact['phone']}")
                print(f"Email: {contact['email']}")
            else:
                print("Contact not found.")
                
        elif choice == '3':
            keyword = input("Enter search keyword: ").strip()
            if not keyword:
                print("Please enter a search keyword.")
                continue
                
            results = search_contacts(contacts, keyword)
            if results:
                print(f"\nFound {len(results)} contact(s):")
                for name, contact in results.items():
                    print(f"Name: {name}, Phone: {contact['phone']}, Email: {contact['email']}")
            else:
                print("No contacts found.")
                
        elif choice == '4':
            name = input("Enter name: ").strip()
            if delete_contact(contacts, name):
                save_contacts(contacts)  # Save after deleting
                print("Contact deleted successfully.")
            else:
                print("Contact not found.")

        elif choice == '5':
            save_contacts(contacts)  # Save before exiting
            print("Exiting Contact Book.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
