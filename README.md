# Sleeper Creeper

**Sleeper Creeper** is a Python tool that generates witty, insightful weekly recaps for your fantasy football league using the Sleeper API and Google Gemini AI. It fetches league data, analyzes matchups, and produces a recap with superlatives and commentary.

---

## Features

- Fetches league, roster, matchup, and player data from the Sleeper API
- Analyzes weekly matchups, scores, and player performances
- Generates a recap using Google Gemini AI
- Highlights superlatives: highest/lowest scores, closest game, biggest blowout
- Caches player data locally for efficiency

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/sleeper-creeper.git
cd sleeper-creeper
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv sleeper-creeper
source sleeper-creeper/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory with the following:

```
SLEEPER_LEAGUE_ID=your_league_id_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Add League Member Info

If you want to give the LLM additional context about your league members, create a file at `data/league_member_info.txt` with a brief description of each member. The format
{past champioships}; {relationships to other members}; {additional facts} is recommended.

---

## Usage

Run the main script:

```bash
python src/main.py
```

- Enter the week number when prompted.
- The script will fetch data, analyze matchups, and generate a recap.

---

## Notes

- Requires Python 3.7+
- Make sure you have valid Sleeper and Gemini API keys.
- Player data is cached in `data/sleeper_players.json` for faster subsequent runs.

---

## Project Structure

```
sleeper-creeper/
├── data/
│   ├── league_member_info.txt
│   └── sleeper_players.json
├── src/
│   ├── main.py
│   ├── sleeper.py
│   └── gemini.py
├── .env
├── requirements.txt
└── readme.md
```

---

## License

MIT License

---

## Acknowledgements

- [Sleeper API](https://docs.sleeper.com/)