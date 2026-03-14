# DAY 9 — Monday, March 9, 2026
## Lecture: Nested Data Structures and Composition — Objects Inside Objects

**System**: Mac Studio M3 Ultra 256GB (GLM-4.7-Flash via Continue)  
**Phase**: Foundation — you write, AI reviews more aggressively  
**Commute**: CS50 Week 2 (Arrays)  
**Evening Session**: 7:00–9:00 PM (2 hours) — Build 1 project  
**Today's theme**: How real-world data naturally nests, and how Python models that nesting through composition

---

## WHAT CHANGES THIS WEEK

Before we get into today's lecture, let me explain what's different about Week 2.

Last week, you used AI to explain concepts before coding and review your code after. That stays. But this week, you add a critical new step: **after the AI reviews your code, you implement its suggestions yourself.** This is not optional. It's the most important learning activity of the week.

Here's the workflow for every project from now on:

```
1. Read the lecture and design questions
2. Write the code yourself (no AI generation)
3. Get it working — test it, fix bugs
4. Select all code → Cmd+L → "What would a senior developer change?"
5. Read the AI's suggestions carefully
6. IMPLEMENT THE CHANGES YOURSELF
7. Commit the improved version
```

Step 6 is where the real learning happens. The AI might say "your search function does a linear scan — use a dictionary for O(1) lookup." You don't ask the AI to rewrite it. You figure out how to restructure your code based on the principle it described. This is the beginning of the review-and-improve muscle that the 10-80-10 workflow depends on.

---

## OPENING LECTURE: WHY DATA NESTS

Think about a recipe. Not in code — just in your head. Picture a recipe card.

A recipe has a name, a description, a prep time, a cook time, a number of servings, and a list of tags (like "vegetarian", "quick", "Italian"). It also has a list of ingredients. And it has a list of steps.

Now think about one ingredient. An ingredient has a name ("flour"), an amount (2), and a unit ("cups"). An ingredient is its own little bundle of data.

And think about one step. A step has a number (1, 2, 3...), instruction text ("Preheat oven to 375°F"), and maybe a duration in minutes.

So what is a recipe, really? It's **data that contains other data that contains other data.** A recipe contains a list of ingredients, and each ingredient contains three fields. A recipe contains a list of steps, and each step contains its own fields. This is **nesting** — data structures inside data structures.

This is not an edge case. This is how virtually all real-world data is shaped:

- A **company** has departments. Each department has employees. Each employee has a role, salary, and contact info.
- A **music playlist** has songs. Each song has a title, artist, album, and duration.
- A **patient record** has visits. Each visit has diagnoses, prescriptions, and notes. Each prescription has a medication, dosage, and frequency.

When you build AI systems for clients in a few months, you'll process nested data constantly. A PDF document has pages. Each page has paragraphs. Each paragraph has sentences. Your RAG pipeline chunks this nested structure into embeddings. If you can't model nesting cleanly in Python, you can't build these systems.

Let's formalize how Python handles nesting, because there are two approaches and you need to understand both.

---

## LECTURE: TWO WAYS TO MODEL NESTED DATA

### Approach 1: Nested Dictionaries and Lists

The simplest way to represent nested data in Python uses only built-in types — dictionaries and lists:

```python
recipe = {
    "name": "Spaghetti Carbonara",
    "servings": 4,
    "tags": ["Italian", "pasta", "quick"],
    "ingredients": [
        {"name": "spaghetti", "amount": 400, "unit": "g"},
        {"name": "guanciale", "amount": 200, "unit": "g"},
        {"name": "eggs", "amount": 4, "unit": ""},
        {"name": "parmesan", "amount": 100, "unit": "g"},
    ],
    "steps": [
        {"number": 1, "instruction": "Boil pasta in salted water", "minutes": 10},
        {"number": 2, "instruction": "Cook guanciale until crispy", "minutes": 8},
    ]
}
```

This works. You can access the first ingredient's name with `recipe["ingredients"][0]["name"]`. You can loop through all ingredients with `for ing in recipe["ingredients"]`. You can serialize the whole thing to JSON with `json.dump()` because dictionaries and lists are natively JSON-compatible.

**Advantages**: Simple. No class definitions needed. Direct JSON serialization. Good for quick scripts and data that comes from external sources (APIs, files) where you don't control the structure.

**Disadvantages**: No guarantees about structure. Nothing stops you from writing `recipe["ingredients"][0]["naem"]` (typo) — you'll get a `KeyError` at runtime, not a helpful error at development time. No methods on the data — if you want to scale a recipe's ingredients, you need a standalone function, not a method on the recipe. No autocomplete in your IDE — the editor doesn't know what keys exist.

### Approach 2: Composition with Classes

The OOP approach creates classes for each concept and **composes** them — objects contain other objects:

```python
class Ingredient:
    def __init__(self, name, amount, unit):
        self.name = name
        self.amount = amount
        self.unit = unit
    
    def scale(self, factor):
        return Ingredient(self.name, self.amount * factor, self.unit)
    
    def __str__(self):
        if self.unit:
            return f"{self.amount} {self.unit} {self.name}"
        return f"{self.amount} {self.name}"

class Recipe:
    def __init__(self, name, servings, ingredients, steps, tags=None):
        self.name = name
        self.servings = servings
        self.ingredients = ingredients   # list of Ingredient objects
        self.steps = steps               # list of Step objects
        self.tags = tags or []
    
    def scale_to(self, new_servings):
        factor = new_servings / self.servings
        scaled_ingredients = [ing.scale(factor) for ing in self.ingredients]
        return Recipe(self.name, new_servings, scaled_ingredients, self.steps, self.tags)
```

Now `Recipe` contains `Ingredient` objects and `Step` objects. This is **composition** — the "has-a" relationship. A Recipe *has* Ingredients. An Ingredient is not a type of Recipe (that would be inheritance — a different relationship we'll discuss below). A Recipe is *composed of* Ingredients.

**Advantages**: Type safety — `ingredient.name` gives you autocomplete and catches typos at development time. Methods live on the data they operate on — `ingredient.scale(2)` is clearer than `scale_ingredient(ingredient, 2)`. Structure is guaranteed — every Ingredient has `name`, `amount`, `unit`. Every Recipe has `ingredients`, `steps`, etc.

**Disadvantages**: More code upfront. Requires `to_dict()` methods for JSON serialization (or use `@dataclass` with `asdict()`). Must reconstruct objects when loading from JSON.

### When to Use Which

This is a judgment call, not a rule. But here's a practical guideline:

- **Data from external sources** (API responses, JSON files, CSV) → start with dicts. Convert to classes only if you need methods or validation.
- **Data your application creates and manages** → use classes. You control the structure, so make it explicit.
- **Quick prototyping** → dicts. Move to classes when the code stabilizes.
- **Anything a client will maintain** → classes. They're self-documenting and harder to misuse.

Today's project uses **both approaches deliberately**. Recipes are stored as nested dictionaries in JSON (because that's the natural file format). Inside the running program, they're represented as class instances (because we need methods like `scale_to()`). The data layer translates between the two. This is the same pattern you used in yesterday's pipeline: external format ↔ internal model.

---

## LECTURE: COMPOSITION vs. INHERITANCE — THE MOST MISUNDERSTOOD CONCEPT IN OOP

Since you asked for deeper OOP explanations, let me address something that confuses almost every programmer when they first learn OOP.

Object-oriented programming has two primary mechanisms for building relationships between classes: **composition** and **inheritance**. Beginners almost always reach for inheritance first because it seems intuitive. I'm going to explain why composition is almost always the better choice, and why today's project uses it exclusively.

### Inheritance: "Is-A" Relationships

Inheritance says one class *is a specialized version of* another class:

```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return "..."

class Dog(Animal):         # Dog IS AN Animal
    def speak(self):
        return "Woof!"

class Cat(Animal):         # Cat IS AN Animal
    def speak(self):
        return "Meow!"
```

`Dog` inherits everything from `Animal` and overrides the `speak()` method. You create a Dog with `my_dog = Dog("Rex")`, and it automatically has `self.name` because it inherited `__init__` from Animal.

This seems clean. The problem is that real-world relationships rarely fit the "is-a" pattern as neatly as textbook examples suggest. Consider:

```python
class Recipe:
    ...

class ItalianRecipe(Recipe):     # Is this useful?
    ...

class VegetarianRecipe(Recipe):  # What about vegetarian Italian?
    ...
```

What if a recipe is both Italian AND vegetarian? Do you create `VegetarianItalianRecipe`? What about quick vegetarian Italian? Inheritance doesn't scale when objects have multiple dimensions of variation. This is called the **diamond problem** and it has caused more bad software architecture than perhaps any other design mistake.

### Composition: "Has-A" Relationships

Composition says one class *contains* another class:

```python
class Recipe:
    def __init__(self, name, ingredients, tags):
        self.name = name
        self.ingredients = ingredients  # Recipe HAS ingredients
        self.tags = tags                # Recipe HAS tags (including "Italian", "vegetarian")
```

An Italian vegetarian recipe? It's just a Recipe where `tags = ["Italian", "vegetarian"]`. No new class needed. No inheritance hierarchy to manage. Tags are data, not types.

**The principle**: Favor composition over inheritance. Use inheritance only when you genuinely have an "is-a" relationship where the child class changes *behavior* (methods), not just *data* (attributes). In practice, this means you'll use inheritance rarely — maybe 10% of the time — and composition constantly.

Today's project uses composition throughout:
- A `Recipe` **has** a list of `Ingredient` objects (composition)
- A `Recipe` **has** a list of `Step` objects (composition)
- A `Recipe` **has** a list of tag strings (composition)
- A `RecipeManager` **has** a list of `Recipe` objects (composition)
- A `RecipeStore` **has** a file path and knows how to persist (composition)

No class inherits from another. Every relationship is "has-a." This is professional Python.

### One More OOP Concept: Encapsulation

You've seen `self.name = name` many times now. Let me explain what `self` is doing at a deeper level, because understanding this unlocks everything else in OOP.

When you write:

```python
class Ingredient:
    def __init__(self, name, amount, unit):
        self.name = name
        self.amount = amount
        self.unit = unit
```

You're saying: "When someone creates an Ingredient, that specific instance carries its own `name`, `amount`, and `unit`." The word `self` refers to *that particular instance*. If you create two ingredients:

```python
flour = Ingredient("flour", 2, "cups")
sugar = Ingredient("sugar", 1, "cup")
```

Then `flour.name` is "flour" and `sugar.name` is "sugar". They're separate objects in memory, each with their own data. `self` is how the class refers to "whichever instance is being used right now."

**Why every method takes `self` as the first parameter**: When you call `flour.scale(2)`, Python translates that to `Ingredient.scale(flour, 2)`. The object before the dot becomes the first argument. That's why `self` appears in the method definition but not in the method call — Python passes it automatically.

**Encapsulation** is the idea that each object manages its own data and provides methods to interact with that data. Instead of reaching into an object and modifying its internals directly, you call methods that the object provides. The `scale()` method on Ingredient doesn't modify the original — it returns a new Ingredient with scaled values. This is a design choice that prevents accidental data corruption: the original recipe's ingredients stay intact when you scale a copy.

---

## PROJECT 16: `recipe_manager.py` (~2 hours)

### The Problem

Build a recipe management system. The user can add recipes with ingredients and steps, view recipes, scale recipes to different serving sizes (the ingredients adjust proportionally), search recipes by name or tag, and persist everything to a JSON file.

The scaling feature is the centerpiece. If a recipe serves 4 and the user wants to cook for 6, every ingredient amount should multiply by 1.5. This is a method on the Recipe class — not a standalone function — because scaling is an operation that belongs to the Recipe concept.

### Concepts to Learn and Use

- **Composition** — Recipe contains Ingredient and Step objects. RecipeManager contains Recipe objects. RecipeStore handles persistence. No inheritance anywhere.
- **Nested data serialization** — converting objects-inside-objects to dictionaries-inside-dictionaries for JSON, and back again when loading
- **List comprehensions for transformation** — `[ing.scale(factor) for ing in self.ingredients]` creates a new list of scaled ingredients in one expression
- **Search with multiple criteria** — finding recipes that match a name substring OR contain a specific tag. This introduces the concept of flexible querying over your data.
- **`round()` for clean numbers** — when you scale 400g by 1.5, you get 600.0. When you scale 3 eggs by 1.5, you get 4.5. Ingredient amounts should be rounded sensibly.
- **`any()` and `all()` built-ins** — `any(tag in recipe.tags for tag in search_tags)` returns True if the recipe has any of the search tags. `all()` returns True only if every condition is True.
- **f-string formatting for display** — building a nicely formatted recipe card on the terminal

### Reference Material

- Python docs — `any()` and `all()`: https://docs.python.org/3/library/functions.html#any
- Python docs — list comprehensions: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
- Python docs — `round()`: https://docs.python.org/3/library/functions.html#round
- Real Python — composition vs inheritance: https://realpython.com/inheritance-composition-python/

### Design Questions (Answer These BEFORE You Code)

1. **What are the classes and what does each own?**

   | Class | Responsibility | Contains |
   |-------|---------------|----------|
   | `Ingredient` | Represents one ingredient with scaling capability | name, amount, unit |
   | `Step` | Represents one instruction step | number, instruction, duration_minutes (optional) |
   | `Recipe` | Represents a complete recipe with scaling and display | name, description, servings, prep_time, cook_time, ingredients (list of Ingredient), steps (list of Step), tags (list of str) |
   | `RecipeStore` | Handles JSON persistence — loading and saving | filepath, knows how to convert between dicts and objects |
   | `RecipeManager` | Manages the collection — add, search, scale, delete | recipes (list of Recipe), store (RecipeStore) |
   | `RecipeApp` | Presentation — menus and user interaction | manager (RecipeManager) |

   Six classes, each with a single clear responsibility. No class does two jobs.

2. **How does scaling work mathematically?**
   
   The scale factor is `new_servings / original_servings`. If a recipe serves 4 and you want 6, the factor is 1.5. Every ingredient amount is multiplied by this factor.

   But should scaling modify the original recipe or create a new one? **Create a new one.** The original recipe should remain unchanged. This is important: if you scale a recipe and then save it, you've lost the original. Instead, `scale_to()` returns a *new* Recipe object with scaled ingredients but the same steps.

   Think about it from the user's perspective: "Show me this recipe for 6 people" is a temporary view, not a permanent change to the recipe.

3. **How does the nested serialization work?**

   When saving to JSON, you need to convert the entire object tree to dictionaries:
   ```
   Recipe.to_dict() returns:
   {
       "name": "...",
       "servings": 4,
       "ingredients": [
           ingredient.to_dict() for each ingredient
           → {"name": "flour", "amount": 2, "unit": "cups"}
       ],
       "steps": [
           step.to_dict() for each step
           → {"number": 1, "instruction": "...", "duration_minutes": 10}
       ],
       "tags": ["Italian", "pasta"]
   }
   ```

   When loading from JSON, you need to reconstruct objects from dictionaries:
   ```python
   # In RecipeStore._dict_to_recipe():
   ingredients = [Ingredient(**ing_dict) for ing_dict in data["ingredients"]]
   steps = [Step(**step_dict) for step_dict in data["steps"]]
   recipe = Recipe(ingredients=ingredients, steps=steps, **rest_of_data)
   ```

   The `**` operator unpacks a dictionary into keyword arguments. `Ingredient(**{"name": "flour", "amount": 2, "unit": "cups"})` is identical to `Ingredient(name="flour", amount=2, unit="cups")`. This is a powerful pattern for converting between dicts and objects.

4. **How does search work?**
   
   The user should be able to search by:
   - Name (partial, case-insensitive): "carb" matches "Spaghetti Carbonara"
   - Tag: "vegetarian" finds all vegetarian recipes
   - Both: flexible query that checks name AND tags

   Implementation: `search_term.lower() in recipe.name.lower()` for name matching. `any(search_term.lower() == tag.lower() for tag in recipe.tags)` for tag matching. Combine with `or` to match either.

5. **How should a recipe display on screen?**

   Think about a recipe card:
   ```
   ════════════════════════════════════════
   Spaghetti Carbonara
   ════════════════════════════════════════
   Servings: 4  |  Prep: 10 min  |  Cook: 20 min
   Tags: Italian, pasta, quick

   INGREDIENTS:
     • 400 g spaghetti
     • 200 g guanciale
     • 4 eggs
     • 100 g parmesan
     • 2 pinch black pepper

   STEPS:
     1. Boil pasta in salted water (10 min)
     2. Cook guanciale until crispy (8 min)
     3. Mix eggs and parmesan
     4. Combine everything off-heat
   ════════════════════════════════════════
   ```

   This display logic belongs in either the Recipe class (as a `display()` or `__str__` method) or in the presentation layer. Either is acceptable — for a project this size, putting it on Recipe as `__str__` is fine.

### Ask GLM-4.7-Flash Before Coding

`Cmd+L` → "Explain two Python concepts:

1. The double-asterisk `**` operator when used with dictionaries — how does `**dict` unpack a dictionary into keyword arguments? Show how this works with a function call and with a class constructor.

2. The `any()` and `all()` built-in functions — how do they work with generator expressions? Give examples of checking if any item in a list meets a condition, and if all items meet a condition.

Concept explanations only. Don't write my program."

### Write Your Code

Build bottom-up: data models first, then persistence, then business logic, then presentation.

```python
import json
from pathlib import Path

RECIPES_FILE = Path("recipes.json")


# ──────────────────────────────────────
# DATA MODELS — the things in your domain
# ──────────────────────────────────────

class Ingredient:
    def __init__(self, name: str, amount: float, unit: str = ""):
        self.name = name
        self.amount = amount
        self.unit = unit

    def scale(self, factor: float):
        """Return a NEW Ingredient with scaled amount. Does not modify self."""
        scaled_amount = round(self.amount * factor, 2)
        return Ingredient(self.name, scaled_amount, self.unit)

    def to_dict(self) -> dict:
        # Convert to dictionary for JSON

    def __str__(self) -> str:
        # "400 g spaghetti" or "4 eggs" (no unit)


class Step:
    def __init__(self, number: int, instruction: str, duration_minutes: int = None):
        self.number = number
        self.instruction = instruction
        self.duration_minutes = duration_minutes

    def to_dict(self) -> dict:
        # Convert to dictionary for JSON

    def __str__(self) -> str:
        # "1. Boil pasta in salted water (10 min)"
        # If no duration: "3. Mix eggs and parmesan"


class Recipe:
    def __init__(self, name: str, servings: int, ingredients: list,
                 steps: list, description: str = "", prep_time: int = 0,
                 cook_time: int = 0, tags: list = None):
        self.name = name
        self.servings = servings
        self.ingredients = ingredients  # list of Ingredient objects
        self.steps = steps              # list of Step objects
        self.description = description
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.tags = tags or []

    def scale_to(self, new_servings: int):
        """Return a NEW Recipe scaled to different servings.
        
        Original recipe is NOT modified. This is important:
        scaling is a view operation, not a mutation.
        """
        factor = new_servings / self.servings
        scaled_ingredients = [ing.scale(factor) for ing in self.ingredients]
        return Recipe(
            name=self.name,
            servings=new_servings,
            ingredients=scaled_ingredients,
            steps=self.steps,       # Steps don't change when scaling
            description=self.description,
            prep_time=self.prep_time,
            cook_time=self.cook_time,
            tags=self.tags
        )

    def matches_search(self, query: str) -> bool:
        """Check if this recipe matches a search query.
        Matches against name (partial, case-insensitive) or tags.
        """
        query_lower = query.lower()
        # Check name
        # Check tags using any()
        # Return True if either matches

    def to_dict(self) -> dict:
        # Convert entire recipe tree to nested dicts
        # ingredients become list of dicts
        # steps become list of dicts

    def __str__(self) -> str:
        # Build the formatted recipe card display
        # Use the format from the design questions above


# ──────────────────────────────────────
# DATA LAYER — persistence
# ──────────────────────────────────────

class RecipeStore:
    def __init__(self, filepath: Path = RECIPES_FILE):
        self.filepath = filepath

    def load_recipes(self) -> list:
        """Load recipes from JSON, reconstruct object tree."""
        # Handle missing file (first run)
        # Read JSON → list of dicts
        # For each recipe dict:
        #   Create Ingredient objects from ingredient dicts
        #   Create Step objects from step dicts
        #   Create Recipe object
        # Return list of Recipe objects

    def save_recipes(self, recipes: list) -> None:
        """Convert object tree to dicts, write JSON."""
        # [recipe.to_dict() for recipe in recipes]
        # json.dump with indent=2 for readability

    def _dict_to_recipe(self, data: dict):
        """Convert a nested dictionary back into a Recipe with proper objects.
        
        This is where ** unpacking shines:
        ingredients = [Ingredient(**d) for d in data["ingredients"]]
        """
        # Build Ingredient objects from the ingredient dicts
        # Build Step objects from the step dicts
        # Build and return Recipe object


# ──────────────────────────────────────
# BUSINESS LOGIC — operations on recipes
# ──────────────────────────────────────

class RecipeManager:
    def __init__(self, store: RecipeStore = None):
        self.store = store or RecipeStore()
        self.recipes = self.store.load_recipes()

    def add_recipe(self, recipe: Recipe) -> None:
        # Append to list, save

    def delete_recipe(self, name: str) -> bool:
        # Find by name, remove, save
        # Return True if found and deleted, False if not found

    def search(self, query: str) -> list:
        """Return all recipes matching the query."""
        return [r for r in self.recipes if r.matches_search(query)]

    def get_recipe(self, name: str):
        """Find a recipe by exact name (case-insensitive)."""
        # Return the recipe or None

    def get_scaled(self, name: str, new_servings: int):
        """Return a scaled copy of a recipe. Original unchanged."""
        recipe = self.get_recipe(name)
        if recipe:
            return recipe.scale_to(new_servings)
        return None

    def get_all_tags(self) -> list:
        """Return sorted list of all unique tags across all recipes."""
        # Use a set to collect unique tags
        # Convert to sorted list


# ──────────────────────────────────────
# PRESENTATION — user interface
# ──────────────────────────────────────

class RecipeApp:
    def __init__(self):
        self.manager = RecipeManager()

    def run(self):
        while True:
            print("\n--- Recipe Manager ---")
            print("1. Add recipe")
            print("2. View all recipes")
            print("3. View recipe details")
            print("4. Scale recipe")
            print("5. Search recipes")
            print("6. Browse by tag")
            print("7. Delete recipe")
            print("8. Quit")

            choice = input("\nChoose: ").strip()
            # Route to appropriate method

    def add_recipe_prompt(self):
        # Get recipe name, description, servings, prep_time, cook_time
        # Get ingredients in a loop (name, amount, unit) until user types "done"
        # Get steps in a loop (instruction, optional duration) until "done"
        # Get tags as comma-separated string, split into list
        # Create Recipe object, pass to manager

    def view_all(self):
        # Show numbered list of recipe names with servings and tags
        # Brief format: "1. Spaghetti Carbonara (4 servings) [Italian, pasta]"

    def view_details(self):
        # Ask for recipe name
        # Print the full recipe card using Recipe.__str__()

    def scale_prompt(self):
        # Ask for recipe name and desired servings
        # Get scaled recipe from manager
        # Display the scaled version
        # Note: "Original recipe unchanged"

    def search_prompt(self):
        # Ask for search term
        # Display matching recipes

    def browse_tags(self):
        # Show all available tags
        # User picks one, show matching recipes


if __name__ == "__main__":
    app = RecipeApp()
    app.run()
```

### Understanding What `scale_to()` Actually Does

Let me walk through this method in detail because it demonstrates several concepts at once:

```python
def scale_to(self, new_servings: int):
    factor = new_servings / self.servings
    scaled_ingredients = [ing.scale(factor) for ing in self.ingredients]
    return Recipe(
        name=self.name,
        servings=new_servings,
        ingredients=scaled_ingredients,
        steps=self.steps,
        ...
    )
```

**Line 1**: `factor = new_servings / self.servings`  
If the recipe serves 4 and we want 6: factor = 6/4 = 1.5

**Line 2**: `scaled_ingredients = [ing.scale(factor) for ing in self.ingredients]`  
This is a list comprehension that calls `.scale(1.5)` on every ingredient and collects the results. Each call to `ing.scale()` returns a **new** Ingredient — the original is untouched. So `scaled_ingredients` is a new list of new objects.

**Lines 3–8**: Return a **new** Recipe with the new servings and new ingredients, but the same steps, tags, name, etc. The original Recipe object is completely untouched.

This pattern — methods that return new objects instead of modifying existing ones — is called **immutability by convention**. The objects aren't technically immutable (you could still write `recipe.servings = 6`), but the methods are designed to never modify `self`. This prevents a whole category of bugs where one part of your code accidentally changes data that another part depends on.

### Test It With Sample Data

After building the app, add at least 2-3 recipes to test with. Here's one to add manually through your app:

```
Name: Spaghetti Carbonara
Description: Classic Roman pasta dish
Servings: 4
Prep time: 10
Cook time: 20
Ingredients:
  - spaghetti, 400, g
  - guanciale, 200, g
  - eggs, 4, (blank unit)
  - parmesan, 100, g
  - black pepper, 2, pinch
Steps:
  1. Boil pasta in salted water (10 min)
  2. Cook guanciale until crispy (8 min)
  3. Mix eggs and parmesan in a bowl
  4. Drain pasta, combine with guanciale off heat
  5. Add egg mixture and toss quickly
Tags: Italian, pasta, quick
```

Then test:
- **Scale to 6 servings**: spaghetti should be 600g, eggs should be 6, guanciale 300g
- **Scale to 2 servings**: spaghetti should be 200g, eggs should be 2, guanciale 100g
- **Scale to 1 serving**: spaghetti should be 100g, eggs should be 1, guanciale 50g
- **View original after scaling**: should still show 4 servings with original amounts (proving scale_to returns a new object)
- **Search "Italian"**: should find the recipe
- **Search "carb"**: should find it (partial name match)

### Ask GLM-4.7-Flash After Coding — THE NEW STEP

This is the Week 2 shift. After your code works, do a thorough AI review:

Select all code → `Cmd+L` →

"Review this recipe manager as a senior developer would. Specifically evaluate:

1. Is my composition correct — do objects contain other objects appropriately?
2. Does scale_to() properly return a new object without modifying the original?
3. Is my nested serialization (to_dict / from_dict with ** unpacking) clean?
4. Is my search implementation efficient for a small number of recipes? What would need to change for thousands of recipes?
5. What am I doing wrong or inefficiently?
6. What patterns should I be using that I'm not?"

**Read every suggestion carefully. Then implement the changes yourself.** Don't ask AI to rewrite the code. The act of interpreting feedback and applying it yourself is the learning.

Make the improvements, then commit the improved version:

```bash
git add . && git commit -m "Project 16: recipe_manager.py — composition, nested serialization, scaling, search"
```

---

## CLOSING LECTURE: COMPOSITION IS YOUR DEFAULT

Today's core lesson: when you need objects inside objects, reach for composition, not inheritance. A Recipe *has* Ingredients. A RecipeManager *has* Recipes. A RecipeStore *has* a filepath. Every relationship is "has-a." No class inherits from another.

When you start directing AI in Week 3, this matters for two reasons:

1. **AI loves inheritance.** If you ask AI to "build a recipe system with different recipe types," it will likely create `ItalianRecipe(Recipe)`, `AsianRecipe(Recipe)`, etc. That's almost always wrong. Tags or attributes are better than type hierarchies for categorization. Your job as architect is to specify composition in your specs so AI doesn't default to inheritance hierarchies.

2. **Nested serialization is everywhere.** Every API you'll consume returns nested JSON. Every document you'll process for RAG has nested structure. The pattern you learned today — `to_dict()` recursively converting objects to dicts, and `**` unpacking reconstructing objects from dicts — is something you'll use in virtually every project.

---

## END OF SESSION

### Push to GitHub:
```bash
git push
```

### Update your tracker:
- [ ] Date: March 9
- [ ] Day number: 9
- [ ] Hours coded: 2
- [ ] Projects completed: 1 (recipe_manager)
- [ ] Key concepts: composition, nested serialization, ** unpacking, any()/all(), immutable returns from scale_to(), AI code review workflow
- [ ] AI review: What was the most useful suggestion? What change did you make?
- [ ] Mood/energy (1–5): ___

### Preview tomorrow (Day 10 — Tuesday):
- **Commute**: CS50 Week 2 continued (or Talk Python to Me)
- **Evening (7:00–9:00 PM)**: `habit_tracker.py`
  - Daily habits with streak tracking and statistics
  - **New concepts**: date arithmetic with `timedelta`, calculating consecutive days, data analysis patterns
  - **OOP focus**: How objects track state over time — a habit "knows" its own history

---

## CONCEPTS YOU SHOULD KNOW AFTER TODAY

1. **Composition** — objects containing other objects ("has-a" relationship), the default way to model nested real-world data in Python
2. **Why composition beats inheritance for most cases** — tags are data, not types; multiple dimensions of variation break inheritance hierarchies
3. **`self` in depth** — how `self` refers to the specific instance, and why every method takes it as the first parameter
4. **Encapsulation** — objects managing their own data through methods rather than external code reaching into their internals
5. **Immutable return pattern** — `scale_to()` returns a new object instead of modifying the original, preventing accidental data corruption
6. **Nested serialization** — `to_dict()` recursively converting an object tree to dictionaries for JSON, and `**` unpacking to reconstruct objects from dictionaries
7. **`any()` and `all()`** — checking if any or all items in an iterable meet a condition, especially useful with generator expressions for search
8. **The AI review workflow** — write code → get AI review → implement suggestions yourself → commit improved version

---

**Day 9 of 365. Week 2 begins. Objects inside objects. The real world is nested — your code should be too.** 🚀
