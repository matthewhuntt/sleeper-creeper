# main.py
import os
from dotenv import load_dotenv
import sleeper
import gemini

DATA_DIR = "../data"

def process_matchups(matchups, roster_id_to_name_map, player_map):
    """
    Processes matchup data to find results, individual player scores, and superlatives.
    """
    if not matchups:
        return None, None

    # Initialize variables for superlatives
    highest_score = {"name": None, "score": 0}
    lowest_score = {"name": None, "score": 999}
    closest_game = {"names": None, "margin": 999}
    biggest_blowout = {"names": None, "margin": 0}

    matchup_summaries = []

    for matchup in matchups:
        # Get manager names and scores for the current matchup
        manager1_id = matchup.get('roster_id')
        manager1_name = roster_id_to_name_map.get(manager1_id, f"Manager {manager1_id}")
        manager1_score = matchup.get('points', 0)

        # Each matchup object has a `matchup_id`. We need to find the opposing team.
        opponent = next((m for m in matchups if m.get('matchup_id') == matchup.get('matchup_id') and m.get('roster_id') != manager1_id), None)
        
        # This check prevents processing the same matchup twice
        if opponent and manager1_id > opponent.get('roster_id'):
            continue
            
        if not opponent:
            # Handle cases where a manager might not have an opponent for the week
            matchup_summaries.append(f"- {manager1_name} had a bye week or their opponent could not be found.")
            continue

        manager2_id = opponent.get('roster_id')
        manager2_name = roster_id_to_name_map.get(manager2_id, f"Manager {manager2_id}")
        manager2_score = opponent.get('points', 0)

        # Determine winner and loser
        if manager1_score > manager2_score:
            winner_name, winner_score = manager1_name, manager1_score
            loser_name, loser_score = manager2_name, manager2_score
        else:
            winner_name, winner_score = manager2_name, manager2_score
            loser_name, loser_score = manager1_name, manager1_score
        
        margin = abs(winner_score - loser_score)
        match_summary_line = f"- {winner_name} ({winner_score:.2f}) defeated {loser_name} ({loser_score:.2f}) by {margin:.2f} points."

        # --- Process individual player scores for both managers ---
        def get_roster_details(manager_matchup_data, manager_name):
            roster_str = f"\n  {manager_name}'s Roster:"
            players = manager_matchup_data.get('players', [])
            player_points = manager_matchup_data.get('players_points', {})
            starters = manager_matchup_data.get('starters', [])
            
            # Filter for starters only
            for player_id in starters:
                player_info = player_map.get(player_id)
                if not player_info:
                    player_name, pos = "Unknown Player", "N/A"
                else:
                    player_name = player_info.get('full_name', player_id)
                    pos = player_info.get('position', 'N/A')
                
                score = player_points.get(player_id, 0)
                roster_str += f"\n    - {player_name} ({pos}): {score:.2f} points"
            return roster_str

        manager1_roster_details = get_roster_details(matchup, manager1_name)
        manager2_roster_details = get_roster_details(opponent, manager2_name)
        
        # Combine the summary line with the detailed rosters
        full_match_details = f"{match_summary_line}{manager1_roster_details}{manager2_roster_details}\n"
        matchup_summaries.append(full_match_details)

        # --- Update superlatives ---
        if winner_score > highest_score["score"]: highest_score = {"name": winner_name, "score": winner_score}
        if loser_score > highest_score["score"]: highest_score = {"name": loser_name, "score": loser_score}
        if winner_score < lowest_score["score"]: lowest_score = {"name": winner_name, "score": winner_score}
        if loser_score < lowest_score["score"]: lowest_score = {"name": loser_name, "score": loser_score}
        if margin < closest_game["margin"]: closest_game = {"names": f"{winner_name} vs. {loser_name}", "margin": margin}
        if margin > biggest_blowout["margin"]: biggest_blowout = {"names": f"{winner_name}'s victory over {loser_name}", "margin": margin}

    # Compile the superlatives into a readable format
    superlatives_summary = (
        "\nWeekly Superlatives:\n"
        f"- Highest Score: {highest_score['name']} ({highest_score['score']:.2f})\n"
        f"- Lowest Score: {lowest_score['name']} ({lowest_score['score']:.2f})\n"
        f"- Biggest Blowout ({biggest_blowout['margin']:.2f} points): {biggest_blowout['names']}\n"
        f"- Closest Squeaker ({closest_game['margin']:.2f} points): {closest_game['names']}"
    )

    return "\n".join(matchup_summaries), superlatives_summary


def get_sleeper_data(league_id, week, refresh_players=False):
    """Fetches league data from Sleeper API."""
    users = sleeper.get_league_users(league_id)
    rosters = sleeper.get_league_rosters(league_id)
    matchups = sleeper.get_matchups(league_id, week)
    players = sleeper.get_players(refresh=refresh_players)
    
    if not users or not rosters or not matchups:
        raise ValueError("Failed to fetch complete data from Sleeper API.")
    
    return users, rosters, matchups, players


def generate_summary(users, rosters, matchups, players, week):
    """Generates a summary of the league data."""
    user_map = {user['user_id']: user['display_name'] for user in users}

    # Create a map of roster_id -> manager_name
    roster_id_to_name_map = {}
    for roster in rosters:
        owner_id = roster['owner_id']
        roster_id = roster['roster_id']
        if owner_id in user_map:
            roster_id_to_name_map[roster_id] = user_map[owner_id]

    print("Analyzing matchups and calculating superlatives...")
    matchup_details, superlatives = process_matchups(matchups, roster_id_to_name_map, players)
    
    if not matchup_details:
        print(f"Could not find any matchup data for week {week}.")
        return
        
    full_summary_data = f"Week {week} Matchup Summary:\n{matchup_details}\n{superlatives}"
    return full_summary_data


def main(refresh_players=False):
    """Main function to run the fantasy football recap generator."""

    load_dotenv()
    league_id = os.getenv("SLEEPER_LEAGUE_ID")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    league_member_info_filepath = DATA_DIR + "/league_member_info.txt"

    with open(league_member_info_filepath, "r") as f:
        league_member_info = f.read().strip()

    if not league_id or not gemini_api_key:
        print("Error: SLEEPER_LEAGUE_ID and GEMINI_API_KEY must be set in the .env file.")
        return

    while True:
        try:
            week = int(input("Enter the week number for the recap: "))
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    try:
        print("Fetching data from Sleeper...")
        users, rosters, matchups, players = get_sleeper_data(league_id, week, refresh_players)
        print("Data fetched successfully!")

        full_summary = generate_summary(users, rosters, matchups, players, week)
        
        print("Sending data to Gemini for the official recap... This may take a moment.")
        recap = gemini.generate_recap(gemini_api_key, full_summary, league_member_info=league_member_info)

        print("\n" + "="*50)
        print(f"      FANTASY FOOTBALL RECAP: WEEK {week}")
        print("="*50 + "\n")
        print(recap)
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your LEAGUE_ID, API Key, and network connection.")


if __name__ == "__main__":
    main()
