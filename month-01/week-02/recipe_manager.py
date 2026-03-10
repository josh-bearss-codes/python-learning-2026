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
        return {
            "name": self.name,
            "amount": self.amount,
            "unit": self.unit,
        }

    def __str__(self) -> str:
        # "400 g spaghetti" or "4 eggs" (no unit)
        return f"{self.amount} {self.unit} {self.name}"  if self.unit else f"{self.amount} {self.name}"


class Step:
    def __init__(self, number: int, instruction: str, duration_minutes: int = None):
        self.number = number
        self.instruction = instruction
        self.duration_minutes = duration_minutes

    def to_dict(self) -> dict:
        # Convert to dictionary for JSON
        return {
            "number": self.number,
            "instruction": self.instruction,
            "duration_minutes": self.duration_minutes
        }

    def __str__(self) -> str:
        # "1. Boil pasta in salted water (10 min)"
        # If no duration: "3. Mix eggs and parmesan"
        if self.duration_minutes:
            return f"{self.number}. {self.instruction} ({self.duration_minutes} min)" 
        else:
            return f"{self.number}. {self.instruction}"

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
        return query_lower in self.name.lower() or any(query_lower in tag.lower() for tag in self.tags)

    def to_dict(self) -> dict:
        # Convert entire recipe tree to nested dicts
        # ingredients become list of dicts
        # steps become list of dicts
        # Return a single dict representing the recipe
        # Include all nested data
        return {
            "name": self.name,
            "servings": self.servings,
            "ingredients": [ingredient.to_dict() for ingredient in self.ingredients],
            "steps": [step.to_dict() for step in self.steps],
            "description": self.description,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "tags": self.tags
        }

    def __str__(self) -> str:
        # Build the formatted recipe card display
        # Use the format from the design questions above
        result = '=' * 80 + '\n'
        result += f"{self.name}\n"
        result += '=' * 80 + '\n'
        result += f"Servings: {self.servings}. |  Prep Time: {self.prep_time} |   Cook Time: {self.cook_time}\n"
        result += f"Tags: {self.tags}\n\n"
        result += "INGREDIENTS:\n"
        for ingredient in self.ingredients:
            result += f"  • {ingredient.__str__()}\n"
        result += "STEPS:\n"
        for step in self.steps:
            result += f"  • {step.__str__()}\n"
        result += '=' * 80
        return result


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
        try:
            with self.filepath.open("r") as f:
                recipes_dict = json.load(f)
                recipes = []
                for recipe_dict in recipes_dict:
                    recipe = self._dict_to_recipe(recipe_dict)
                    recipes.append(recipe)
                return recipes
        except FileNotFoundError:
            with self.filepath.open("w") as f:
                json.dump([], f)
                return []
        except json.JSONDecodeError:
            return []
        except Exception as e:
            print(f"Error loading recipes: {e}")
            return []

    def save_recipes(self, recipes: list) -> None:
        """Convert object tree to dicts, write JSON."""
        # [recipe.to_dict() for recipe in recipes]
        # json.dump with indent=2 for readability
        recipe_dicts = [recipe.to_dict() for recipe in recipes]
        with self.filepath.open("w") as f:
            json.dump(recipe_dicts, f, indent=2)

    def _dict_to_recipe(self, data: dict):
        """Convert a nested dictionary back into a Recipe with proper objects.
        
        This is where ** unpacking shines:
        ingredients = [Ingredient(**d) for d in data["ingredients"]]
        """
        # Build Ingredient objects from the ingredient dicts
        # Build Step objects from the step dicts
        # Build and return Recipe object
        ingredients = [Ingredient(**d) for d in data["ingredients"]]
        steps = [Step(**d) for d in data["steps"]]
        return Recipe(name=data["name"], servings=data["servings"], ingredients=ingredients, steps=steps, 
                       description=data["description"], prep_time=data["prep_time"], 
                       cook_time=data["cook_time"], tags=data["tags"])


# ──────────────────────────────────────
# BUSINESS LOGIC — operations on recipes
# ──────────────────────────────────────

class RecipeManager:
    def __init__(self, store: RecipeStore = None):
        self.store = store or RecipeStore()
        self.recipes = self.store.load_recipes()

    def add_recipe(self, recipe: Recipe) -> None:
        # Append to list, save
        self.recipes.append(recipe)
        self.store.save_recipes(self.recipes)

    def delete_recipe(self, name: str) -> bool:
        # Find by name, remove, save
        # Return True if found and deleted, False if not found
        recipe = next((r for r in self.recipes if r.name.lower() == name.lower()), None)
        if recipe:
            self.recipes.remove(recipe)
            self.store.save_recipes(self.recipes)
            return True
        return False

    def search(self, query: str) -> list:
        """Return all recipes matching the query."""
        return [r for r in self.recipes if r.matches_search(query)]

    def get_recipe(self, name: str):
        """Find a recipe by exact name (case-insensitive)."""
        # Return the recipe or None
        for recipe in self.recipes:
            if recipe.name.lower() == name.lower():
                return recipe
        return None

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
        tags = sorted(set(tag for recipe in self.recipes for tag in recipe.tags))
        return tags

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
            if choice == '1':
                self.add_recipe_prompt()
            elif choice == '2':
                self.view_all()
            elif choice == '3':
                self.view_details()
            elif choice == '4':
                self.scale_prompt()
            elif choice == '5':
                self.search_prompt()
            elif choice == '6':
                self.browse_tags()
            elif choice == '7':
                self.delete_recipe_prompt()
            elif choice == '8':
                break
            else:
                print("Invalid choice. Please try again.")

    def add_recipe_prompt(self):
        # Get recipe name, description, servings, prep_time, cook_time
        recipe_name = input("Enter recipe name: ")
        description = input("Enter recipe description: ")
        servings = float(input("Enter number of servings: "))
        prep_time = float(input("Enter preparation time: "))
        cook_time = float(input("Enter cooking time: "))
        # Get ingredients in a loop (name, amount, unit) until user types "done"
        ingredients = []
        while True:
            ingredient_name = input("Enter ingredient name (or 'done' to finish): ")
            if ingredient_name.lower() == 'done':
                break
            amount = float(input("Enter amount: "))
            unit = input("Enter unit: ")
            # Create Ingredient object, add to recipe
            ingredients.append(Ingredient(ingredient_name, amount, unit))
        # Get steps in a loop (instruction, optional duration) until "done"
        steps = []
        while True:
            step_number = len(steps) + 1
            step_instruction = input("Enter step instruction (or 'done' to finish): ")
            if step_instruction.lower() == 'done':
                break
            duration = int(input("Enter duration (optional): "))
            # Create Step object, add to recipe
            steps.append(Step(step_number, step_instruction, duration))
        # Get tags as comma-separated string, split into list
        tags = input("Enter tags (comma-separated): ").split(',')
        # Create Recipe object, pass to manager
        self.manager.add_recipe(Recipe(recipe_name, servings, ingredients, steps, description, prep_time, cook_time, tags))
        print("Recipe added successfully.")
    
    def delete_recipe_prompt(self):
        # Ask for recipe name
        recipe_name = input("Enter the name of the recipe you want to delete:")
        # Find the recipe in the manager's list
        # If found, ask for confirmation to delete
        if recipe_name in self.manager.recipes:            
            confirm = input(f"Are you sure you want to delete '{recipe_name}'? (yes/no)")
            # Delete the recipe from the manager's list
            # Confirm deletion
            if confirm.lower() == 'yes':
                self.manager.delete_recipe(recipe_name)
                print("Recipe deleted successfully.")
            # If not confirmed, cancel deletion
            else:
                print("Deletion cancelled.")
        # If not found, inform user
        else:
            print("Recipe not found.")

    def view_all(self):
        # Show numbered list of recipe names with servings and tags
        # Brief format: "1. Spaghetti Carbonara (4 servings) [Italian, pasta]"
        for index, recipe in enumerate(self.manager.recipes):
            print(f"{index + 1}. {recipe.name} ({recipe.servings} servings) [{', '.join(recipe.tags)}]")

    def view_details(self):
        # Ask for recipe name
        # Print the full recipe card using Recipe.__str__()
        recipe_name = input("Enter the recipe name to view details: ")
        recipe = self.manager.get_recipe(recipe_name)
        if recipe:
            print(recipe.__str__())
        else:
            print("Recipe not found.")

    def scale_prompt(self):
        # Ask for recipe name and desired servings
        # Get scaled recipe from manager
        # Display the scaled version
        # Note: "Original recipe unchanged"
        recipe_name = input("Enter the recipe name to scale: ")
        desired_servings = int(input("Enter the desired servings: "))
        scaled_recipe = self.manager.get_scaled(recipe_name, desired_servings)
        if scaled_recipe:
            print(scaled_recipe.__str__())
        else:
            print("Recipe not found.")


    def search_prompt(self):
        # Ask for search term
        # Display matching recipes
        search_term = input("Enter search term: ")
        matching_recipes = self.manager.search(search_term)
        if matching_recipes:
            for recipe in matching_recipes:
                print(recipe.__str__())
        else:
            print("No recipes found matching the search term.")

    def browse_tags(self):
        # Show all available tags
        # User picks one, show matching recipes
        tags = self.manager.get_all_tags()
        if tags:
            print("Available tags:")
            for tag in tags:
                print(tag)
        tag_choice = input("Enter a tag to browse: ")
        matching_recipes = self.manager.search(tag_choice)
        if matching_recipes:
            for recipe in matching_recipes:
                print(recipe.__str__())


if __name__ == "__main__":
    app = RecipeApp()
    app.run()
