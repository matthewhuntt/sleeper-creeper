import requests
import json
import os

BASE_URL = "https://api.sleeper.app/v1"
DATA_DIR = "../data"
PLAYER_DATA_FILE = DATA_DIR + "/sleeper_players.json"

def get_current_week():
    """Fetches the current NFL week from the Sleeper API."""
    response = requests.get(f"{BASE_URL}/state/nfl")
    response.raise_for_status()
    return response.json().get('week', None)

def get_league_users(league_id):
    """Fetches all users in a league."""
    response = requests.get(f"{BASE_URL}/league/{league_id}/users")
    response.raise_for_status()
    return response.json()

def get_league_rosters(league_id):
    """Fetches all rosters in a league."""
    response = requests.get(f"{BASE_URL}/league/{league_id}/rosters")
    response.raise_for_status()
    return response.json()

def get_matchups(league_id, week):
    """Fetches all matchups for a given week."""
    response = requests.get(f"{BASE_URL}/league/{league_id}/matchups/{week}")
    response.raise_for_status()
    return response.json()

def get_players(refresh=False):
    """
    Fetches all NFL players from the Sleeper API.
    It caches the data in a local JSON file to avoid repeated calls.
    
    Args:
        refresh (bool): If True, it forces a fresh download of player data.
    """
    if refresh or not os.path.exists(PLAYER_DATA_FILE):
        print("Fetching fresh player data from Sleeper API...")
        try:
            response = requests.get(f"{BASE_URL}/players/nfl")
            response.raise_for_status()
            player_data = response.json()
            with open(PLAYER_DATA_FILE, 'w') as f:
                json.dump(player_data, f, indent=2)
            print(f"Player data saved to {PLAYER_DATA_FILE}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching player data: {e}")

            if os.path.exists(PLAYER_DATA_FILE):
                print("Falling back to existing local player data.")
                with open(PLAYER_DATA_FILE, 'r') as f:
                    player_data = json.load(f)
            else:
                raise
    else:
        print(f"Loading player data from local file ({PLAYER_DATA_FILE}).")
        with open(PLAYER_DATA_FILE, 'r') as f:
            player_data = json.load(f)
    
    return player_data
