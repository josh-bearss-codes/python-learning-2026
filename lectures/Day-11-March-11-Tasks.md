# DAY 11 — Wednesday, March 11, 2026
## Lecture: The Python Data Model — Teaching Your Objects to Compare, Sort, and Think

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue)  
**Phase**: Foundation — you write, AI reviews more aggressively  
**Commute**: CS50 Week 3 (Algorithms — sorting and searching)  
**Evening Session**: 7:00–9:00 PM (2 hours) — Build 1 project  
**Today's theme**: How Python lets you teach your objects to behave like built-in types — comparable, sortable, and self-aware

---

## OPENING LECTURE: THE SECRET LANGUAGE PYTHON SPEAKS WITH YOUR OBJECTS

Every time you write `3 < 5`, Python isn't doing what you think it's doing. It's not comparing two numbers with some magical built-in mechanism. It's calling a method: `(3).__lt__(5)`. The integer `3` is an object, and it has a method called `__lt__` (short for "less than") that knows how to compare itself to another value.

This might seem like an academic curiosity, but it's one of the most powerful ideas in Python. It means **you can teach your own objects to respond to operators.** When you write a `Product` class, you can define what `<` means for products. When you write `sorted(products)`, Python calls those comparison methods to determine the order. Your objects participate in the same system that integers and strings use.

This system is called the **Python Data Model**, and the special methods that power it are called **dunder methods** (short for "double underscore"). You've already used a few:

| Dunder Method | You've Used It | What It Does |
|--------------|---------------|-------------|
| `__init__` | Every class since Day 5 | Called when creating a new object |
| `__str__` | Most classes since Day 5 | Called by `print()` and `str()` |
| `__repr__` | Not yet (today!) | Called in the REPL and debugger |

Today we add the comparison dunders — the methods that let your objects understand `<`, `>`, `==`, `<=`, `>=`, and `!=`. Once your objects understand these, they automatically work with `sorted()`, `min()`, `max()`, and all of Python's sorting and filtering infrastructure.

---

## LECTURE: COMPARISON OPERATORS — WHAT PYTHON ACTUALLY DOES

### The Six Comparison Operators

When you write a comparison expression, Python translates it to a method call on the left operand:

| Expression | Python Calls | Method Name | Meaning |
|-----------|-------------|-------------|---------|
| `a == b` | `a.__eq__(b)` | "equal" | Is a equal to b? |
| `a != b` | `a.__ne__(b)` | "not equal" | Is a not equal to b? |
| `a < b` | `a.__lt__(b)` | "less than" | Is a less than b? |
| `a > b` | `a.__gt__(b)` | "greater than" | Is a greater than b? |
| `a <= b` | `a.__le__(b)` | "less than or equal" | Is a less than or equal to b? |
| `a >= b` | `a.__ge__(b)` | "greater than or equal" | Is a greater than or equal to b? |

Each method takes `self` (the left operand) and `other` (the right operand) and returns `True` or `False`.

### How This Works With Built-in Types

You've been using these operators since Day 1 without knowing they were method calls:

```python
# When you write:
5 < 10

# Python executes:
(5).__lt__(10)    # Returns True

# When you write:
"apple" < "banana"

# Python executes:
"apple".__lt__("banana")   # Returns True (alphabetical order)

# When you write:
date(2026, 3, 11) > date(2026, 3, 10)

# Python executes:
date(2026, 3, 11).__gt__(date(2026, 3, 10))   # Returns True (chronological order)
```

Every type in Python — integers, floats, strings, dates — implements these methods. That's why you can compare them with `<` and `>`. The operators aren't magic — they're method calls that each type defines for itself.

### Defining Comparison on Your Own Classes

Here's where it gets powerful. Let's say you have a `Product` class and you want products to be sortable by price:

```python
class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
    
    def __eq__(self, other):
        """Two products are equal if they have the same name."""
        if not isinstance(other, Product):
            return NotImplemented
        return self.name == other.name
    
    def __lt__(self, other):
        """A product is 'less than' another if its price is lower."""
        if not isinstance(other, Product):
            return NotImplemented
        return self.price < other.price
```

Now this works:

```python
apple = Product("Apple", 1.50, 100)
laptop = Product("Laptop", 999.99, 5)

print(apple < laptop)          # True (1.50 < 999.99)
print(apple == laptop)         # False (different names)
print(apple > laptop)          # Hmm... this might NOT work yet!
```

### The Problem: You Need All Six, But Writing All Six Is Tedious

If you only define `__lt__` and `__eq__`, Python can't automatically figure out `__gt__`, `__le__`, `__ge__`, and `__ne__`. You might expect that if `a < b` is `True`, then `b > a` is also `True`. Logically, yes. But Python doesn't make that assumption — it calls `b.__gt__(a)`, and if `b` doesn't have a `__gt__` method, you get an error or unexpected behavior.

You *could* write all six methods manually:

```python
class Product:
    def __eq__(self, other): return self.price == other.price
    def __ne__(self, other): return self.price != other.price
    def __lt__(self, other): return self.price < other.price
    def __gt__(self, other): return self.price > other.price
    def __le__(self, other): return self.price <= other.price
    def __ge__(self, other): return self.price >= other.price
```

That's six methods that all do essentially the same thing with different operators. This is repetitive and error-prone — if you change the comparison logic (say, sort by name instead of price), you have to change all six.

### The Solution: `@total_ordering`

Python provides a decorator called `@total_ordering` from the `functools` module. It says: "If you define `__eq__` and ONE of `__lt__`, `__le__`, `__gt__`, or `__ge__`, I'll automatically generate the rest."

```python
from functools import total_ordering

@total_ordering
class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
    
    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.name == other.name
    
    def __lt__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.price < other.price
```

Now **all six** comparison operators work:

```python
apple = Product("Apple", 1.50, 100)
banana = Product("Banana", 0.75, 200)
laptop = Product("Laptop", 999.99, 5)

print(apple < laptop)      # True   ← you defined this
print(laptop > apple)       # True   ← @total_ordering generated this
print(banana <= apple)      # True   ← @total_ordering generated this
print(apple >= banana)      # True   ← @total_ordering generated this
print(apple != banana)      # True   ← @total_ordering generated this
```

**You write 2 methods (`__eq__` + `__lt__`). Python generates the other 4.** This is the standard approach in professional Python.

### The `isinstance` Check and `NotImplemented`

You'll notice each comparison method starts with:

```python
if not isinstance(other, Product):
    return NotImplemented
```

Two concepts here:

**`isinstance(other, Product)`** checks whether `other` is a Product object. This prevents nonsensical comparisons like `Product("Apple", 1.50, 100) < "hello"`. Without this check, `self.price < other.price` would crash with `AttributeError: 'str' object has no attribute 'price'`.

**`NotImplemented`** (note: NOT `NotImplementedError` — they're different things!) is a special sentinel value that tells Python: "I don't know how to compare myself to this other thing." Python will then try the reverse comparison — maybe the other object knows how to compare itself to a Product. If neither side can handle it, Python raises a `TypeError`.

This is a protocol — a shared agreement about how objects communicate when they can't handle a comparison. It's one of Python's most elegant design decisions.

### How `sorted()` Uses Comparison Operators

Here's the connection that makes all of this practical. When you write:

```python
products = [laptop, apple, banana]
sorted_products = sorted(products)
```

Python's sorting algorithm (Timsort) compares pairs of items using `<` (which calls `__lt__`). It never calls `__gt__` or `__ge__` directly during sorting — it only needs `__lt__` to determine order. That's why `@total_ordering` only requires `__eq__` + `__lt__` as the minimum.

But having all six operators means your objects also work with:

```python
cheapest = min(products)        # Uses __lt__ to find minimum
most_expensive = max(products)  # Uses __lt__ to find maximum

# Filtering with comparisons
expensive = [p for p in products if p.price > 100]

# Checking membership with ==
target = Product("Apple", 1.50, 100)
if target in products:          # Uses __eq__ to check membership
    print("Found it!")
```

Your objects become **first-class citizens** in Python's sorting and comparison infrastructure. They behave just like integers or strings.

### What About Sorting by MULTIPLE Criteria?

Sometimes you need to sort by price, and when prices are equal, by name. There are two approaches:

**Approach 1: Tuple comparison in `__lt__`**

```python
def __lt__(self, other):
    if not isinstance(other, Product):
        return NotImplemented
    return (self.price, self.name) < (other.price, other.name)
```

Python compares tuples element by element: first by price, then by name if prices are equal. This is called **lexicographic comparison** — the same way dictionaries sort words (first letter, then second letter if first is equal, etc.).

**Approach 2: Key function with `sorted()`**

```python
sorted(products, key=lambda p: (p.price, p.name))
```

This doesn't use your `__lt__` at all — the `key` function extracts comparison values. Both approaches work. Use `__lt__` when there's a single "natural" ordering for your objects. Use `key` when you need multiple different orderings.

For today's project, we'll use both: `__lt__` defines the natural ordering (by stock level, so lowest-stock items sort first for alerts), and `key` functions provide alternative orderings (by price, by name, by value) in the presentation layer.

---

## LECTURE: `__repr__` vs `__str__` — THE TWO FACES OF YOUR OBJECT

You've been writing `__str__` since Day 5. Today we add `__repr__`. Understanding the difference between them is important for debugging and professional Python.

**`__str__`**: The "pretty" representation. Called by `print()` and `str()`. Meant for end users.

```python
def __str__(self):
    return f"{self.name} — ${self.price:.2f} ({self.quantity} in stock)"
# Output: "Widget A — $29.99 (45 in stock)"
```

**`__repr__`**: The "developer" representation. Called in the Python REPL, in debuggers, and when objects appear in lists. Meant for programmers. The convention is that `__repr__` should look like valid Python code that could recreate the object:

```python
def __repr__(self):
    return f"Product(name='{self.name}', price={self.price}, quantity={self.quantity})"
# Output: "Product(name='Widget A', price=29.99, quantity=45)"
```

Why does this distinction matter?

```python
products = [Product("Apple", 1.50, 100), Product("Banana", 0.75, 200)]

print(products)
# With __repr__: [Product(name='Apple', price=1.5, quantity=100), Product(name='Banana', price=0.75, quantity=200)]
# Without __repr__: [<__main__.Product object at 0x104a5b290>, <__main__.Product object at 0x104a5b310>]

print(products[0])
# Uses __str__: "Apple — $1.50 (100 in stock)"
```

When you `print()` a single object, Python uses `__str__`. When you `print()` a list of objects, Python uses `__repr__` for each item inside the list. Without `__repr__`, you get useless memory addresses. With it, you can see exactly what's in your data.

**Rule of thumb**: Always define `__repr__`. Define `__str__` when you need a different user-friendly format. If you only define `__repr__`, Python will use it for both purposes.

---

## LECTURE: OBJECTS THAT ENFORCE BUSINESS RULES

Yesterday's Habit object tracked state over time. Today's Product object enforces **invariants** — conditions that must always be true. 

An invariant is a rule about data that your object guarantees. For a Product:

- Quantity can never be negative (you can't have -5 widgets in stock)
- Price must be positive (nothing costs -$10)
- Reorder point must be non-negative

In a naive implementation, nothing prevents bad data:

```python
class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price        # Could be -10!
        self.quantity = quantity   # Could be -5!
```

Someone could write `product.quantity = -50` and your system would silently accept it. Every function that uses the product would need to check for negative quantities. That's fragile — one forgotten check and you have corrupt data.

The OOP solution is to **make the object responsible for its own validity**. The Product class itself rejects invalid values:

```python
class Product:
    def __init__(self, name, price, quantity, reorder_point=10):
        self.name = name
        self.price = self._validate_positive(price, "price")
        self._quantity = self._validate_non_negative(quantity, "quantity")
        self.reorder_point = self._validate_non_negative(reorder_point, "reorder_point")
    
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
```

Now `Product("Widget", -10, 5)` raises a `ValueError` immediately. The object refuses to exist in an invalid state. This is called **defensive programming** — the object defends its own integrity.

### Property Setters: Guarding Changes After Creation

Validation in `__init__` prevents invalid objects from being created. But what about changes after creation?

```python
product = Product("Widget", 29.99, 50)
product.quantity = -10    # This bypasses __init__ validation!
```

The solution is a **property with a setter** — similar to `@property` (which you used yesterday as a getter), but with the added ability to validate new values:

```python
class Product:
    def __init__(self, name, price, quantity, reorder_point=10):
        self.name = name
        self.price = price
        self.quantity = quantity           # This calls the setter!
        self.reorder_point = reorder_point
    
    @property
    def quantity(self):
        """Get the current quantity."""
        return self._quantity
    
    @quantity.setter
    def quantity(self, value):
        """Set quantity with validation. Negative values are rejected."""
        if value < 0:
            raise ValueError(f"Quantity cannot be negative, got {value}")
        self._quantity = value
```

Notice the pattern:
- The actual data is stored in `self._quantity` (with underscore — a convention meaning "private, don't access directly")
- `@property` defines the getter: `product.quantity` reads `self._quantity`
- `@quantity.setter` defines the setter: `product.quantity = 50` runs validation, then sets `self._quantity`
- From the outside, it looks like a normal attribute access — `product.quantity = 50` — but validation runs automatically

**Even `__init__` goes through the setter.** When `__init__` writes `self.quantity = quantity`, it calls the setter method, which validates the value. This means validation happens at creation time AND at modification time — one piece of code, two protection points.

This is the full power of properties in Python: **attributes that look simple but behave intelligently.**

### `@staticmethod` — A Method That Doesn't Need `self` or `cls`

You noticed `@staticmethod` on the validation helpers. This is the third type of method (after regular methods and `@classmethod`):

| Decorator | First Parameter | Called On | Use Case |
|-----------|----------------|-----------|----------|
| *(none)* | `self` | Instance: `product.add_stock(10)` | Needs access to instance data |
| `@classmethod` | `cls` | Class: `Product.from_dict(d)` | Alternative constructors |
| `@staticmethod` | *(nothing)* | Either: `Product._validate_positive(x, "price")` | Utility that doesn't need instance or class |

A static method is just a regular function that lives inside a class for organizational purposes. `_validate_positive` doesn't need `self` (it doesn't access any instance data) and doesn't need `cls` (it doesn't create new instances). It's a pure utility function that validates a number. Putting it inside the class keeps it close to the code that uses it.

---

## PROJECT 18: `inventory_system.py` (~2 hours)

### The Problem

Build an inventory management system for a small business. Products have names, SKUs (stock keeping units), prices, quantities, categories, and reorder points. The system tracks stock levels, generates low-stock alerts, records stock movements (additions and removals with reasons), and produces reports sorted and filtered in various ways.

### Concepts to Learn and Use

- **Comparison dunder methods** — `__eq__`, `__lt__` with `@total_ordering`
- **`__repr__`** — developer-friendly object representation
- **Property setters** — `@property` + `@xxx.setter` for validated attribute access
- **`@staticmethod`** — utility methods that don't need `self` or `cls`
- **Business rule enforcement** — objects that reject invalid state
- **`Enum` class** — defining fixed sets of valid values (stock movement types, alert levels)
- **`dataclass` with `@total_ordering`** — combining dataclasses with comparison operators
- **Multiple sort orders** — natural ordering via `__lt__` plus alternative orderings via `key` functions
- **`filter()` function** — an alternative to list comprehensions for filtering
- **Formatted tabular output** — professional-looking reports with alignment

### Reference Material

- Python docs — `functools.total_ordering`: https://docs.python.org/3/library/functools.html#functools.total_ordering
- Python docs — rich comparison methods: https://docs.python.org/3/reference/datamodel.html#object.__lt__
- Python docs — `property`: https://docs.python.org/3/library/functions.html#property
- Python docs — `enum`: https://docs.python.org/3/library/enum.html
- Real Python — operator and dunder methods: https://realpython.com/operator-function-overloading/
- Real Python — Python property: https://realpython.com/python-property/

### Design Questions (Answer These BEFORE You Code)

1. **What are the entities and their relationships?**

   | Class | Responsibility | Key Relationships |
   |-------|---------------|-------------------|
   | `Product` | Represents one product with validated attributes and comparison operators | Has stock movements (list of StockMovement) |
   | `StockMovement` | Records one stock change — when, how much, why | Belongs to a Product |
   | `AlertLevel` | Enum: OK, LOW, CRITICAL, OUT_OF_STOCK | Used by Product to classify its stock status |
   | `Inventory` | Manages the collection of products, generates alerts and reports | Has Products (list of Product) |
   | `InventoryStore` | JSON persistence | Translates between objects and JSON |
   | `InventoryApp` | Presentation — menus, reports, user interaction | Has Inventory |

2. **What business rules does a Product enforce?**
   - Price must be positive (> 0)
   - Quantity cannot be negative (≥ 0)
   - Reorder point must be non-negative (≥ 0)
   - Stock removals that would make quantity negative are rejected (you can't sell 10 items if you only have 3)
   - Every stock change is recorded as a StockMovement with a timestamp and reason

3. **What is the natural sort order for Products?**
   
   For an inventory system, the most useful natural ordering is **by stock urgency** — products closest to running out should sort first. This means sorting by the ratio of current quantity to reorder point:
   
   - Out of stock (quantity = 0) → highest urgency
   - Below reorder point → high urgency
   - Near reorder point → medium urgency
   - Well stocked → low urgency
   
   For simplicity, you can sort by quantity ascending (lowest stock first). The `__lt__` method defines this.

4. **What is an Enum and why use it here?**
   
   An `Enum` defines a fixed set of named constants:
   
   ```python
   from enum import Enum
   
   class AlertLevel(Enum):
       OK = "ok"
       LOW = "low"
       CRITICAL = "critical"
       OUT_OF_STOCK = "out_of_stock"
   ```
   
   Why not just use strings? Because strings are typo-prone. Nothing stops someone from writing `"critcal"` or `"Out_Of_Stock"`. An Enum is a closed set — only `AlertLevel.OK`, `AlertLevel.LOW`, `AlertLevel.CRITICAL`, and `AlertLevel.OUT_OF_STOCK` exist. Anything else is an error. This prevents an entire category of bugs.
   
   Enums also give you clean comparisons: `if product.alert_level == AlertLevel.CRITICAL` reads like English.

5. **What reports should the system produce?**
   - **Stock overview** — all products with quantity, reorder point, alert level, sorted by urgency
   - **Low stock report** — only products at LOW or CRITICAL level
   - **Stock value report** — products sorted by total value (quantity × price), showing how much capital is tied up in inventory
   - **Category summary** — total products, total value, and alert counts per category
   - **Movement history** — recent stock changes for a specific product

### Ask GLM-4.7-Flash Before Coding

`Cmd+L` → "Explain these Python concepts:

1. `functools.total_ordering` — what does this decorator do? Why would I use it instead of writing all six comparison methods manually? Show a minimal example.

2. Property setters — how does `@property` work together with `@xxx.setter` to create a validated attribute? Show how the setter is called both during `__init__` and when assigning a new value later.

3. Python's `Enum` class — how do I define one, how do I compare enum values, and how do I serialize them to strings for JSON storage?

Explain each concept clearly with examples. Don't write my program."

### Write Your Code

```python
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
        pass

    @classmethod
    def from_dict(cls, data: dict):
        # Reconstruct Product from dict, including StockMovement list
        pass

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
        pass

    def save(self, products: list) -> None:
        # Convert all products to dicts, write JSON
        pass


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
        pass

    def find_by_sku(self, sku: str):
        # Return Product or None
        pass

    def find_by_name(self, query: str) -> list:
        # Partial, case-insensitive name search
        pass

    def find_by_category(self, category: str) -> list:
        # Filter by category
        pass

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
            # Route to methods

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
    # low_stock_report, value_report, category_summary,
    # product_details, search_prompt


if __name__ == "__main__":
    app = InventoryApp()
    app.run()
```

### Test Your Comparison Operators

After building the system, test that comparisons work correctly:

```python
# In a Python shell or test section:
p1 = Product("Widget A", "WA-001", 29.99, 5)     # Low stock
p2 = Product("Widget B", "WB-001", 49.99, 50)    # Well stocked
p3 = Product("Widget C", "WC-001", 19.99, 0)     # Out of stock

# Natural ordering (by quantity)
print(p3 < p1 < p2)                # True: 0 < 5 < 50

# sorted() uses __lt__ automatically
products = [p2, p1, p3]
for p in sorted(products):
    print(p)
# Should print: Widget C (0), Widget A (5), Widget B (50)

# min() and max() work
print(min(products).name)          # "Widget C" (lowest quantity)
print(max(products).name)          # "Widget B" (highest quantity)

# Equality by SKU
p4 = Product("Widget A Deluxe", "WA-001", 39.99, 10)
print(p1 == p4)                    # True — same SKU
print(p1 == p2)                    # False — different SKU

# Try to create an invalid product
try:
    bad = Product("Bad", "BAD-001", -10, 5)
except ValueError as e:
    print(f"Caught: {e}")          # "price must be positive, got -10"

# Try to remove too much stock
print(p1.remove_stock(100))        # False — only 5 in stock
print(p1.quantity)                 # Still 5 — unchanged
```

### Ask GLM-4.7-Flash After Coding — The Review Step

Select all code → `Cmd+L` →

"Review this inventory system as a senior developer. Specifically evaluate:

1. Are my comparison operators (`__eq__` on SKU, `__lt__` on quantity/name) well-designed? Is the tuple comparison approach for multi-criteria sorting correct?
2. Does `@total_ordering` correctly generate the other four operators from my `__eq__` and `__lt__`?
3. Is my property setter for quantity correctly validating both during `__init__` and on later assignment?
4. Is my use of Enum for AlertLevel and MovementType appropriate? Am I serializing them correctly for JSON?
5. Does my `__repr__` follow the convention of looking like valid Python code?
6. Is the `remove_stock` method correctly preventing negative quantities? What edge cases might I be missing?
7. What would a senior developer change about this code?"

**Read the suggestions. Implement the changes yourself. Commit the improved version.**

```bash
git add . && git commit -m "Project 18: inventory_system.py — @total_ordering, comparison dunders, property setters, enums, business rules"
```

---

## CLOSING LECTURE: YOUR OBJECTS ARE NOW FULL CITIZENS

Before today, your objects could store data (`__init__`), display themselves (`__str__`), and convert to dictionaries (`to_dict`). After today, they can also **compare themselves** (`__eq__`, `__lt__`), **validate themselves** (property setters), **describe themselves to developers** (`__repr__`), and **enforce business rules** (rejecting invalid state).

This is the Python Data Model in action. Your Product objects participate in the same system as integers and strings. `sorted()` works. `min()` works. `max()` works. `==` works. `in` works. Your objects are **first-class citizens.**

When you direct AI to write code in Week 3, you'll specify things like "Products should sort by stock urgency, enforce non-negative quantities via property setters, and use Enum for alert levels." AI will generate the implementation. Your job will be to verify that the comparison operators are correct, that the property setters actually prevent invalid state, and that the enums are properly serialized. That verification requires understanding what these features actually do — which is exactly what today built.

The Python Data Model has dozens more dunder methods: `__add__`, `__len__`, `__contains__`, `__iter__`, `__getitem__`, and many more. You'll encounter them as needed. But the comparison and representation dunders you learned today are the most commonly used after `__init__` and `__str__`.

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 11
- [ ] Day number: 11
- [ ] Hours coded: 2
- [ ] Projects completed: 1 (inventory_system)
- [ ] Key concepts: __eq__, __lt__, @total_ordering, __repr__, property setters, @staticmethod, Enum, isinstance, NotImplemented, business rule enforcement
- [ ] AI review: What was the most useful suggestion? What change did you make?
- [ ] Mood/energy (1–5): ___

### Preview tomorrow (Day 12 — Thursday):
- **Commute**: CS50 Week 3 continued or Talk Python To Me
- **Evening (7:00–9:00 PM)**: `student_gradebook.py`
  - Students, courses, enrollments, GPA calculation
  - **OOP focus**: Multiple classes with bidirectional relationships — a Student has Courses, and a Course has Students. How do you model this without creating circular dependencies?
  - **New concepts**: Class relationships beyond simple composition, weighted averages, data aggregation across related objects

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

1. **The Python Data Model** — Python translates operators to dunder method calls: `a < b` becomes `a.__lt__(b)`
2. **The six comparison dunders** — `__eq__`, `__ne__`, `__lt__`, `__gt__`, `__le__`, `__ge__` and what each maps to
3. **`@total_ordering`** — define `__eq__` + `__lt__`, get the other four for free
4. **Tuple comparison for multi-criteria sorting** — `(self.quantity, self.name) < (other.quantity, other.name)` compares element by element
5. **`isinstance()` and `NotImplemented`** — type checking in comparisons and the protocol for "I can't compare to this type"
6. **`__repr__` vs `__str__`** — developer representation vs user representation, and when Python uses each
7. **Property setters** — `@property` + `@xxx.setter` for validated attributes that look like normal attributes from the outside
8. **`@staticmethod`** — utility methods that don't need `self` or `cls`, used for validation helpers
9. **`Enum`** — fixed sets of named constants that prevent typo-based bugs
10. **Business rule enforcement** — objects that reject invalid state both at creation and modification
11. **Natural ordering vs alternative ordering** — `__lt__` defines one default sort; `key` functions provide alternatives

---

**Day 11 of 365. Your objects can now compare, sort, validate, and defend themselves. They're not passive data containers anymore — they're intelligent participants in Python's type system.** 🚀
