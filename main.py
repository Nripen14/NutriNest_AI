import json
import re
from pathlib import Path

from ai import call_gpt


BASE_DIR = Path(__file__).resolve().parent
FOOD_FILE = BASE_DIR / "food_data.json"
REPORT_FILE = BASE_DIR / "daily_report.json"


FALLBACK_FOODS = {
    "roti": {
        "calories": 100,
        "emoji": "🫓",
        "category": "grains",
        "serving": "1 medium roti",
    },
    "rice": {
        "calories": 200,
        "emoji": "🍚",
        "category": "grains",
        "serving": "1 cup cooked",
    },
    "egg": {
        "calories": 75,
        "emoji": "🥚",
        "category": "protein",
        "serving": "1 large egg",
    },
    "apple": {
        "calories": 95,
        "emoji": "🍎",
        "category": "fruits",
        "serving": "1 medium apple",
    },
    "water": {
        "calories": 0,
        "emoji": "💧",
        "category": "drinks",
        "serving": "1 glass",
    },
}


def load_food_database(filename=FOOD_FILE):
    """Load the food database, or use a small built-in list if needed."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("The food database must contain a JSON object.")

        # Keep only entries with a usable name and a dictionary of details.
        return {
            str(name).strip().lower(): details
            for name, details in data.items()
            if str(name).strip() and isinstance(details, dict)
        }

    except FileNotFoundError:
        print(f"\nI couldn't find {filename.name}, so I'll use a small sample food list.")
    except (json.JSONDecodeError, ValueError) as error:
        print(f"\nThere was a problem reading {filename.name}: {error}")
        print("I'll use a small sample food list instead.")

    return FALLBACK_FOODS.copy()


def get_positive_int(prompt):
    """Ask until the user enters a whole number greater than zero."""
    while True:
        value = input(prompt).strip()
        try:
            number = int(value)
            if number > 0:
                return number
            print("Please enter at least 1.")
        except ValueError:
            print("Please enter a whole number, such as 1 or 2.")


def show_categories(food_db):
    categories = sorted({
        details.get("category", "other")
        for details in food_db.values()
        if isinstance(details, dict)
    })

    print(f"\nI've loaded {len(food_db)} food items.")
    if categories:
        print("You can browse these categories:")
        print("  " + "  |  ".join(categories))


def display_category_items(food_db, category):
    matches = [
        (
            f"{details.get('emoji', '🍽️')} {name} — "
            f"{details.get('calories', '?')} kcal "
            f"({details.get('serving', 'serving not specified')})"
        )
        for name, details in food_db.items()
        if isinstance(details, dict)
        and details.get("category", "other") == category
    ]

    print(f"\n{category.title()} foods")
    print("-" * 40)
    if matches:
        for item in matches:
            print(f"  {item}")
    else:
        print("I couldn't find any foods in that category.")


def search_items(food_db, keyword):
    keyword = keyword.strip().lower()
    if not keyword:
        print("Type a word after 'search' to look for a food.")
        return

    matches = [
        f"{details.get('emoji', '🍽️')} {name} "
        f"({details.get('calories', '?')} kcal)"
        for name, details in food_db.items()
        if keyword in name and isinstance(details, dict)
    ]

    if matches:
        print("\nHere are the foods I found:")
        for item in matches:
            print(f"  {item}")
    else:
        print(f"I couldn't find a food matching '{keyword}'.")


def estimate_unknown_food(food_name):
    """Get a rough AI estimate for a food that is not in the local database."""
    prompt = (
        f"Estimate the calories in one ordinary serving of {food_name}. "
        "This is only a rough food-logging estimate, not a nutrition assessment. "
        "Reply with one whole number in kcal, with no extra words. "
        "If the food is too unclear to estimate, reply exactly UNKNOWN."
    )

    try:
        answer = call_gpt(prompt)
        if not isinstance(answer, str):
            answer = str(answer)

        answer = answer.strip()
        if answer.upper() == "UNKNOWN":
            return None

        # Accept a plain number, optionally followed by 'kcal'.
        match = re.fullmatch(r"(\d{1,4})\s*(?:kcal)?", answer, flags=re.IGNORECASE)
        if not match:
            print("The AI returned an unclear estimate, so I won't add it to your log.")
            return None

        calories = int(match.group(1))
        if calories < 0 or calories > 5000:
            print("That estimate looks unusual, so I won't add it to your log.")
            return None

        return calories

    except Exception as error:
        print(f"I couldn't get an AI estimate right now: {error}")
        return None


def log_daily_meals(food_db):
    total_calories = 0
    logged_meals = []

    categories = {
        details.get("category", "other")
        for details in food_db.values()
        if isinstance(details, dict)
    }

    print("\nLET'S LOG WHAT YOU'VE EATEN")
    print("-" * 40)
    print("Enter a food name to add it to your log.")
    print("You can also enter a category, use 'search <word>', or type 'done'.")
    print("Portions and calorie values are estimates, not exact measurements.\n")

    while True:
        choice = input("Food or command: ").strip().lower()

        if not choice:
            continue

        if choice in {"done", "finish", "quit"}:
            break

        if choice in categories:
            display_category_items(food_db, choice)
            continue

        if choice.startswith("search "):
            search_items(food_db, choice[7:])
            continue

        if choice in food_db:
            details = food_db[choice]
            try:
                per_serving = max(0, int(details.get("calories", 0)))
            except (TypeError, ValueError):
                print("The calorie information for this item is incomplete.")
                continue

            servings = get_positive_int(f"How many servings of {choice}? ")
            calories = per_serving * servings
            emoji = details.get("emoji", "🍽️")
            serving_text = details.get("serving", "serving not specified")
            estimate_source = "food database"

        else:
            print(f"\n'{choice}' isn't in the food list.")
            use_ai = input("Would you like a rough AI estimate? (y/n): ").strip().lower()
            if use_ai not in {"y", "yes"}:
                print("No problem. Try another food or search the database.")
                continue

            per_serving = estimate_unknown_food(choice)
            if per_serving is None:
                print("I couldn't make a reliable estimate. You can try another food.")
                continue

            servings = get_positive_int("How many servings? ")
            calories = per_serving * servings
            emoji = "🍴"
            serving_text = "one typical serving (AI estimate)"
            estimate_source = "AI estimate"

        total_calories += calories
        logged_meals.append({
            "item": choice,
            "emoji": emoji,
            "servings": servings,
            "calories_kcal_estimate": calories,
            "serving_description": serving_text,
            "estimate_source": estimate_source,
        })

        print(f"Added: {emoji} {servings} × {choice} — approximately {calories} kcal.")
        print(f"Your logged total so far: about {total_calories} kcal.\n")

    return total_calories, logged_meals


def get_ai_wellness_suggestions():
    """Generate friendly, general wellness ideas without giving medical advice."""
    prompt = (
        "You are a friendly, practical wellness companion for a college student. "
        "Write a short, supportive set of everyday wellness suggestions. "
        "Use a natural and conversational tone, not a clinical or preachy one. "
        "Include realistic meal ideas with familiar Indian foods, hydration, "
        "sleep, and enjoyable movement. Encourage balance, variety, and regular "
        "meals. Do not set calorie targets, recommend weight loss, prescribe "
        "supplements, diagnose symptoms, or suggest medical treatment. "
        "Use a few clear headings and concise bullet points. Avoid generic "
        "motivational slogans."
    )

    try:
        suggestions = call_gpt(prompt)
        return str(suggestions).strip() or "I don't have suggestions to share right now."
    except Exception as error:
        print(f"I couldn't load the wellness suggestions right now: {error}")
        return (
            "A few simple reminders for today:\n"
            "  • Try to include a variety of foods in your meals.\n"
            "  • Keep water nearby and drink regularly.\n"
            "  • Make room for enough sleep and some movement you enjoy."
        )


def save_report(total_calories, logged_meals):
    report = {
        "total_calories_kcal_estimate": total_calories,
        "note": (
            "Calorie values are approximate. Actual values vary with portion "
            "size, ingredients, and preparation. This food log is for general "
            "information and is not medical advice."
        ),
        "logged_meals": logged_meals,
    }

    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as out_file:
            json.dump(report, out_file, indent=4, ensure_ascii=False)
        print(f"\nYour food log has been saved to {REPORT_FILE.name}.")
    except OSError as error:
        print(f"\nI couldn't save your food log: {error}")


def main():
    print("\n" + "=" * 52)
    print("🥗  YOUR EVERYDAY HEALTH COMPANION")
    print("=" * 52)
    print("A simple place to log meals and get general wellness ideas.")
    print("This tool is for information only; it does not diagnose or treat illness.")

    food_db = load_food_database()
    show_categories(food_db)

    print("\nA FEW WELLNESS IDEAS")
    print("-" * 40)
    print(get_ai_wellness_suggestions())

    total, meals = log_daily_meals(food_db)
    save_report(total, meals)

    print("\nYOUR FOOD LOG AT A GLANCE")
    print("-" * 40)
    print(f"Food entries: {len(meals)}")
    print(f"Estimated calories logged: {total} kcal")

    if meals:
        print("\nWhat you added:")
        for meal in meals:
            print(
                f"  {meal['emoji']} {meal['servings']} × {meal['item']} "
                f"— about {meal['calories_kcal_estimate']} kcal"
            )
    else:
        print("You haven't added any foods yet.")

    print("\nThanks for checking in. Take care of yourself!")
    print("Remember: the calorie total is only an estimate, not a daily target.\n")


if __name__ == "__main__":
    main()
