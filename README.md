# AI Health Assistant

A beginner-friendly Python project using a JSON food database and an AI API.

## Files
- `main.py`: menu, food search, meal logging, wellness suggestions, report saving.
- `ai.py`: connection to the `NotOpenAI` client.
- `food_data.json`: starter food database. Add the rest of your validated food records here.
- `daily_report.json`: created automatically when the program runs.
- `notopenai/`: copy the supplied support folder here unchanged.

## Setup
1. Install Python 3.10 or later.
2. Keep `main.py`, `ai.py`, `food_data.json`, and the supplied `notopenai/` folder in this same project folder.
3. Set your API key as an environment variable. Do not publish it.

Linux/macOS:
```bash
export CIP_API_KEY="your_api_key_here"
python main.py
```

Windows PowerShell:
```powershell
$env:CIP_API_KEY="your_api_key_here"
python main.py
```

## Expand the food database
`food_data.json` is a valid starter database, not the complete 270+ item list. Add the remaining entries from your supplied list inside the outer `{ }`, ensuring:
- every key is a quoted food name;
- every value has valid JSON fields;
- commas separate entries, but there is no comma after the final entry;
- calorie values and serving descriptions are approximate and clearly defined.

Example:
```json
"masala dosa": {
  "calories": 250,
  "emoji": "🥞",
  "category": "breakfast",
  "serving": "1 medium dosa"
}
```

## Notes
- Food calorie estimates vary with portion size, recipe, and preparation.
- Unknown foods may receive an AI-generated rough estimate.
- The app does not calculate weight-loss targets or provide medical diagnoses or treatment.
- AI output can be inaccurate; use it as general educational information only.
