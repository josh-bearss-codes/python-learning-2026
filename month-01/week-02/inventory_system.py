import json
from datetime import datetime
from enum import Enum
from functools import total_ordering
from collections import defaultdict
from pathlib import Path

INVENTORY_FILE = Path("inventory.json")


# ──────────────────────────────────────
# ENUMS — fixed sets of valid values
# ──────────────────────────────────────

class AlertLevel(Enum):
    """Stock alert levels. Ordered from most to least urgent."""
    OUT_OF_STOCK = "out_of_stock"
    CRITICAL = "critical"
    LOW = "low"
    OK = "ok"

class MovementType(Enum):
    """Types of stock movement."""
    RECEIVED = "received"       # New stock arrived
    SOLD = "sold"               # Sold to customer
    RETURNED = "returned"       # Customer return
    DAMAGED = "damaged"         # Damaged/disposed
    ADJUSTMENT = "adjustment"   # Manual count correction


# ──────────────────────────────────────
# DATA MODELS
# ──────────────────────────────────────

class StockMovement:
    """Records one stock change with context.
    
    This is an event in the product's history — similar to
    yesterday's habit completions, but with more metadata.
    """
    def __init__(self, quantity_change: int, movement_type: str,
                 reason: str = "", timestamp: str = None):
        self.quantity_change = quantity_change  # positive = stock in, negative = stock out
        self.movement_type = movement_type
        self.reason = reason
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict:
        # Convert to JSON-serializable dict
        return {
            "quantity_change": self.quantity_change,
            "movement_type": self.movement_type,
            "reason": self.reason,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        direction = "+" if self.quantity_change >= 0 else ""
        return f"StockMovement({direction}{self.quantity_change}, {self.movement_type}, '{self.timestamp[:10]}')"

    def __str__(self) -> str:
        direction = "+" if self.quantity_change >= 0 else ""
        return f"{self.timestamp[:10]} | {direction}{self.quantity_change:>5} | {self.movement_type:<12} | {self.reason}"


@total_ordering
class Product:
    """A product with validated attributes and comparison support.
    
    Invariants (always true):
      - price > 0
      - quantity >= 0
      - reorder_point >= 0
    
    Natural ordering: by quantity ascending (lowest stock first),
    so sorted(products) puts the most urgent items first.
    """

    def __init__(self, name: str, sku: str, price: float, quantity: int,
                 category: str = "General", reorder_point: int = 10,
                 movements: list = None):
        self.name = name
        self.sku = sku
        self.price = self._validate_positive(price, "price")
        self.reorder_point = self._validate_non_negative(reorder_point, "reorder_point")
        self._quantity = 0  # Initialize before setter
        self.quantity = quantity  # Goes through the setter for validation
        self.category = category
        self.movements = movements or []

    # ── Validated Property ────────────────

    @property
    def quantity(self) -> int:
        """Current stock quantity."""
        return self._quantity

    @quantity.setter
    def quantity(self, value: int):
        """Set quantity with validation. Rejects negative values."""
        value = self._validate_non_negative(value, "quantity")
        self._quantity = value

    # ── Derived Properties ────────────────

    @property
    def stock_value(self) -> float:
        """Total value of this product's stock: quantity × price."""
        return round(self.quantity * self.price, 2)

    @property
    def alert_level(self) -> AlertLevel:
        """Current alert level based on quantity vs reorder point.
        
        Business rules:
          quantity == 0              → OUT_OF_STOCK
          quantity <= reorder_point / 2  → CRITICAL (below half of reorder point)
          quantity <= reorder_point      → LOW
          quantity > reorder_point       → OK
        """
        if self.quantity == 0:
            return AlertLevel.OUT_OF_STOCK
        elif self.quantity <= self.reorder_point // 2:
            return AlertLevel.CRITICAL
        elif self.quantity <= self.reorder_point:
            return AlertLevel.LOW
        else:
            return AlertLevel.OK

    @property
    def needs_reorder(self) -> bool:
        """True if stock is at or below reorder point."""
        return self.quantity <= self.reorder_point

    # ── Stock Operations ──────────────────

    def add_stock(self, amount: int, movement_type: str = MovementType.RECEIVED.value,
                  reason: str = "") -> None:
        """Add stock. Records the movement."""
        if amount <= 0:
            raise ValueError(f"Amount to add must be positive, got {amount}")
        self.quantity += amount
        self.movements.append(
            StockMovement(amount, movement_type, reason)
        )

    def remove_stock(self, amount: int, movement_type: str = MovementType.SOLD.value,
                     reason: str = "") -> bool:
        """Remove stock if sufficient quantity exists.
        
        Returns True if successful, False if insufficient stock.
        Does NOT allow quantity to go negative — this is a business rule
        enforced at the operation level.
        """
        if amount <= 0:
            raise ValueError(f"Amount to remove must be positive, got {amount}")
        if amount > self.quantity:
            return False  # Insufficient stock
        self.quantity -= amount
        self.movements.append(
            StockMovement(-amount, movement_type, reason)
        )
        return True

    # ── Comparison Operators ──────────────

    def __eq__(self, other) -> bool:
        """Two products are equal if they have the same SKU.
        
        SKU (Stock Keeping Unit) is the unique identifier.
        Two products could have the same name but different SKUs
        (different sizes, colors, etc.)
        """
        if not isinstance(other, Product):
            return NotImplemented
        return self.sku == other.sku

    def __lt__(self, other) -> bool:
        """Natural ordering: by quantity ascending.
        
        This means sorted(products) puts lowest-stock items first.
        Ties broken by name alphabetically.
        
        Why this ordering? In an inventory system, the most important
        items are the ones running low. Sorting by quantity ascending
        means the items needing attention appear at the top.
        """
        if not isinstance(other, Product):
            return NotImplemented
        return (self.quantity, self.name) < (other.quantity, other.name)

    # ── Display ───────────────────────────

    def __repr__(self) -> str:
        """Developer representation — useful in debugger and REPL."""
        return f"Product(sku='{self.sku}', name='{self.name}', qty={self.quantity}, price={self.price})"

    def __str__(self) -> str:
        """User-friendly display."""
        alert = self.alert_level.value.upper()
        return f"{self.sku:<10} {self.name:<20} ${self.price:>8.2f}  Qty: {self.quantity:>5}  [{alert}]"

    # ── Serialization ─────────────────────

    def to_dict(self) -> dict:
        # Convert product and its movements to JSON-serializable dict
        return {
            "name" : self.name,
            "sku" : self.sku,
            "price" : self.price,
            "reorder_point" : self.reorder_point,
            "quantity" : self.quantity,
            "category" : self.category,
            "alert_level" : self.alert_level.value,
            "stock_value" : self.stock_value,
            "movements" : self.movements
        }

    @classmethod
    def from_dict(cls, data: dict):
        # Reconstruct Product from dict, including StockMovement list
        return Product(**data)

    # ── Validation Helpers ────────────────

    @staticmethod
    def _validate_positive(value, field_name):
        if value <= 0:
            raise ValueError(f"{field_name} must be positive, got {value}")
        return value

    @staticmethod
    def _validate_non_negative(value, field_name):
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative, got {value}")
        return value


# ──────────────────────────────────────
# DATA LAYER — persistence
# ──────────────────────────────────────

class InventoryStore:
    def __init__(self, filepath: Path = INVENTORY_FILE):
        self.filepath = filepath

    def load(self) -> list:
        # Read JSON, reconstruct Product objects with from_dict
        try:
            with open (self.filepath, 'r') as file:
                data = json.load(file)
                return [Product.from_dict(item) for item in data if isinstance(item, dict)]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
        except Exception as e:
            print(f"An error occurred while loading the inventory: {e}")
            return []

    def save(self, products: list) -> None:
        # Convert all products to dicts, write JSON
        try: 
            with open(self.filepath, 'w') as file:
                data = [product.to_dict() for product in products]
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"An error occurred while saving the inventory to {self.filepath}: {e}")
        
        
# ──────────────────────────────────────
# BUSINESS LOGIC — inventory operations and reporting
# ──────────────────────────────────────

class Inventory:
    def __init__(self, store: InventoryStore = None):
        self.store = store or InventoryStore()
        self.products = self.store.load()

    def add_product(self, product: Product) -> None:
        # Check for duplicate SKU using __eq__
        # Append, save
        for p in self.products:
            if p == product:
                print(f"Product with SKU {product.sku} already exists.")
                return
        self.products.append(product)
        self.store.save(self.products)
        print(f"Product {product.name} added to inventory.")

    def find_by_sku(self, sku: str):
        # Return Product or None
        for p in self.products:
            if p.sku == sku:
                return p
        return None

    def find_by_name(self, query: str) -> list:
        # Partial, case-insensitive name search
        for p in self.products:
            if query.lower() in p.name.lower():
                return p
        return None

    def find_by_category(self, category: str) -> list:
        # Filter by category
        return [p for p in self.products if p.category == category]

    def get_low_stock(self) -> list:
        """All products that need reordering, sorted by urgency.
        
        Uses the natural ordering (via __lt__) — sorted() puts
        lowest-stock items first automatically.
        """
        low = [p for p in self.products if p.needs_reorder]
        return sorted(low)  # __lt__ sorts by quantity ascending

    def get_stock_value_report(self) -> list:
        """All products sorted by stock value (highest first).
        
        Uses key function for this alternative ordering,
        since the natural ordering is by quantity, not value.
        """
        return sorted(self.products, key=lambda p: p.stock_value, reverse=True)

    def get_category_summary(self) -> dict:
        """Summary by category: product count, total value, alert counts.
        
        Uses defaultdict to accumulate per-category statistics.
        """
        summary = defaultdict(lambda: {"count": 0, "value": 0.0, "alerts": 0})
        for p in self.products:
            cat = summary[p.category]
            cat["count"] += 1
            cat["value"] += p.stock_value
            if p.needs_reorder:
                cat["alerts"] += 1
        return dict(summary)

    def get_total_value(self) -> float:
        """Total inventory value across all products."""
        return round(sum(p.stock_value for p in self.products), 2)


# ──────────────────────────────────────
# PRESENTATION
# ──────────────────────────────────────

class InventoryApp:
    def __init__(self):
        self.inventory = Inventory()

    def run(self):
        # Show alert summary on startup
        # Main menu loop
        self._show_alerts_on_startup()

        while True:
            print("\n--- Inventory System ---")
            print("1. View all products")
            print("2. Add new product")
            print("3. Add stock (receive)")
            print("4. Remove stock (sell)")
            print("5. Low stock report")
            print("6. Stock value report")
            print("7. Category summary")
            print("8. Product details & history")
            print("9. Search products")
            print("10. Quit")

            choice = input("\nChoose: ").strip()
            # Route to methods based on user input
            if choice == '1':
                self.view_all()
            elif choice == '2':
                self.add_product_prompt()
            elif choice == '3':
                self.add_stock_prompt()
            elif choice == '4':
                self.remove_stock_prompt()
            elif choice == '5':
                self.low_stock_report()
            elif choice == '6':
                self.stock_value_report()
            elif choice == '7':
                self.category_summary()
            elif choice == '8':
                self.product_details()
            elif choice == '9':
                self.search_prompt()
            elif choice == '10':
                break
            else:
                print("\nInvalid choice. Please try again.")

    def _show_alerts_on_startup(self):
        """Display any low-stock alerts when app opens."""
        low = self.inventory.get_low_stock()
        if low:
            print(f"\n⚠️  {len(low)} product(s) need attention:")
            for p in low[:5]:  # Show top 5 most urgent
                print(f"   {p}")
        else:
            print("\n✅ All stock levels healthy")

    def view_all(self):
        """Display all products in a formatted table.
        
        Demonstrates formatted output with column headers and alignment.
        """
        products = sorted(self.inventory.products, key=lambda p: p.name)
        print(f"\n{'SKU':<10} {'Name':<20} {'Price':>10} {'Qty':>7} {'Value':>10} {'Status':>14}")
        print("─" * 75)
        for p in products:
            alert = p.alert_level.value.upper()
            print(f"{p.sku:<10} {p.name:<20} ${p.price:>8.2f} {p.quantity:>6} ${p.stock_value:>9.2f}  [{alert}]")
        print("─" * 75)
        print(f"{'Total inventory value:':>50} ${self.inventory.get_total_value():>9.2f}")

    # ... implement remaining menu methods:
    # add_product_prompt, add_stock_prompt, remove_stock_prompt,
    # low_stock_report, stock_value_report, category_summary,
    # product_details, search_prompt
    def add_product_prompt(self):
        # Implement the logic to prompt the user to add a new product
        try:
            input("Press Enter to add a new product...")
            # Add your code here to handle the addition of a new product
            # For example, you can call a method to add a product to the inventory
            name = input("Enter the name of the product: ")
            sku = input("Enter the SKU of the product: ")
            price = float(input("Enter the price of the product: "))
            reorder_point = int(input("Enter the reorder point of the product: "))
            quantity = int(input("Enter the quantity of the product: "))
            category = input("Enter the category of the product: ")

            product_id = Product(name, sku, price, reorder_point, quantity, category)
            self.inventory.add_product(product_id)
        except Exception as e:
            print(f"Error adding product: {e}")
            input("Press Enter to continue...")
            return
        input("Product added successfully. Press Enter to continue...")
        return
    
    def add_stock_prompt(self):
        # Implement the logic to prompt the user to add stock to an existing product
        try:
            input("Press Enter to add stock to an existing product...")
            # Add your code here to handle the addition of stock to an existing product
            # For example, you can call a method to add stock to the product
            product_id =self.inventory.find_by_name(input("Enter the name of the product: "))
            quantity = int(input("Enter the quantity to add to the product: "))
            product_id.add_stock(quantity)
        except Exception as e:
            print(f"Error adding stock: {e}")
            input("Press Enter to continue...")
            return
        input("Stock added successfully. Press Enter to continue...")
        return
    
    def remove_stock_prompt(self):
        # Implement the logic to prompt the user to remove stock from an existing product
        try:
            input("Press Enter to remove stock from an existing product...")
            # Add your code here to handle the removal of stock from an existing product
            # For example, you can call a method to remove stock from the product
            product_id = self.inventory.find_by_name(input("Enter the name of the product: "))
            quantity = int(input("Enter the quantity to remove from the product: "))
            product_id.remove_stock(quantity)
        except Exception as e:
            print(f"Error removing stock: {e}")
            input("Press Enter to continue...")
            return
        input("Stock removed successfully. Press Enter to continue...")
        return
    
    def low_stock_report(self):
        # Implement the logic to generate a low stock report
        try:
            input("Press Enter to generate a low stock report...")
            # Add your code here to generate a low stock report
            # For example, you can call a method to generate the report and display it
            low_stock_report = self.inventory.get_low_stock()
            print("Low Stock Report:")
            for product in low_stock_report:
                print(f"Product Name: {product.name}, Quantity: {product.quantity}")
        except Exception as e:
           print(f"Error generating low stock report: {e}")
           print("Press Enter to continue...")
           return
        input("Low stock report generated successfully. Press Enter to continue...")
        return
    
    def stock_value_report(self):
        # Implement the logic to generate a stock value report
        try:
            input("Press Enter to generate a stock value report...")
            # Add your code here to generate a stock value report 
            value_report = self.inventory.get_stock_value_report()
            print("Stock Value Report:")
            for product in value_report:
                print(f"Product Name: {product.name}, Value: {product.value}")
        except Exception as e:
            print(f"Error generating stock value report: {e}")
            print("Press Enter to continue...")
            return
        input("Stock value report generated successfully Press Enter to continue...")
        return
    
    def category_summary(self):
        """
        Generate and display a category summary report for the inventory.
        Shows each category with the number of products and their details.
        """
        # Implement the logic to generate a category summary report
        try:
            input("Press Enter to generate a category summary report...")
            # Add your code here to generate a category summary report

            # Check if inventory is empty or no products available
            if not self.inventory or not self.inventory.products:
                print("Inventory is empty or no products available.")
                print("Press Enter to continue...")
                return
            
            # Generate category summary report
            category_summary = self.inventory.get_category_summary()
            print("Category Summary Report:")
            for category, products in category_summary.items():
                print(f"Category: {category}")
                for product in products:
                    print(f"  Product Name: {product.name}, Quantity: {product.quantity}")

            # Display the category summary report
            print("Press Enter to continue...")
            return
        except Exception as e:
            print(f"Error generating category summary report: {e}")
            print("Press Enter to continue...")
            return
    
    def product_details(self):
        # Implement the logic to display product details
        try:
            input("Press Enter to view product details...")
            # Add your code here to display product details
            product_id = input("Enter the product SKU to view details: ")
            product = self.inventory.find_by_sku(product_id)
            if product:
                print(f"Product Details:")
                print(f" Product Name: {product.name}")
                print(f" SKU: {product.sku}")
                print(f" Quantity: {product.quantity}")
                print(f" Price: {product.price}")
                print(f" Category: {product.category}")
        except Exception as e:
            print(f"Error displaying product details: {e}")
            print("Press Enter to continue...")
            return
        input("Press Enter to continue...")
        return
    
    def search_prompt(self):
        # Implement the logic to prompt the user for search criteria
        try:
            input("Press Enter to search for products...")
            # Add your code here to prompt the user for search criteria
            search_criteria = input("Enter search criteria (e.g., name, category, SKU): ")
            if search_criteria:
                if search_criteria == "name":
                    search_term = input("Enter product name to search: ")
                    for product in self.inventory.products:
                        if product.find_by_name(search_term) is not None:
                            print(f"Product found: {product.name}")
                            break
                elif search_criteria == "category":
                    search_term = input("Enter product category to search: ")
                    for product in self.inventory.products:
                        if product.find_by_category(search_term) is not None:
                            print(f"Product found: {product.name}")
                            break
                elif search_criteria == "SKU":
                    search_term = input("Enter SKU to search: ")
                    for product in self.inventory.products:
                        if product.find_by_sku(search_term) is not None:
                            print(f"Product found: {product.name}")
                            break
                else:
                    print("Invalid search criteria. Please choose from 'name', 'category', or 'SKU'.")
            else:
                print("No search criteria provided.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return

if __name__ == "__main__":
    app = InventoryApp()
    app.run()