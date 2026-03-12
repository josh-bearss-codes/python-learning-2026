from inventory_system import Product

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