import random
from team import TEAMS_DATA, get_team_by_id, get_random_teams

CUP_STAGES = ["Oitavas de Final", "Quartas de Final", "Semifinal", "Final"]
TEAMS_IN_CUP = 16 # Should be a power of 2, e.g., 8, 16, 32

def initialize_cup(player_selected_team_id):
    """
    Initializes a cup tournament with the player's selected team and AI opponents.
    Creates the first round of match pairings.
    """
    player_team = get_team_by_id(player_selected_team_id)
    if not player_team:
        print(f"Error: Player team with ID {player_selected_team_id} not found.")
        # Fallback to a default player team if not found
        player_team = {"id": 0, "name": "Default Player Team", "skin_id": 1, "color": (200, 200, 200)}

    # Select AI opponents, excluding the player's team
    num_ai_teams = TEAMS_IN_CUP - 1
    ai_teams = get_random_teams(num_ai_teams, exclude_teams_ids=[player_selected_team_id])

    if len(ai_teams) < num_ai_teams:
        print(f"Warning: Could not select {num_ai_teams} unique AI opponents. Cup might be smaller.")
        # Potentially handle this by reducing TEAMS_IN_CUP or erroring

    all_cup_teams = [player_team] + ai_teams
    random.shuffle(all_cup_teams) # Shuffle to randomize pairings

    # Create initial bracket for "Oitavas de Final"
    initial_matches = []
    for i in range(0, len(all_cup_teams), 2):
        if i + 1 < len(all_cup_teams): # Ensure there's a pair
            team1 = all_cup_teams[i]
            team2 = all_cup_teams[i+1]
            is_player_match = (team1['id'] == player_selected_team_id or team2['id'] == player_selected_team_id)
            initial_matches.append({
                'team1': team1,
                'team2': team2,
                'winner': None,
                'played': False,
                'is_player_match': is_player_match,
                'match_id': f"{CUP_STAGES[0]}_{len(initial_matches)+1}" # Unique ID for the match
            })
        else:
            # This case should ideally not happen if TEAMS_IN_CUP is a power of 2 and team selection works
            print(f"Warning: Odd number of teams ({len(all_cup_teams)}), team {all_cup_teams[i]['name']} gets a bye (not implemented).")


    cup_data = {
        'player_team': player_team,
        'current_stage_index': 0,
        'stages': {
            CUP_STAGES[0]: initial_matches
        },
        'advancing_teams': [], # Teams that won in the current round
        'status': 'active', # active, finished
        'cup_winner': None
    }
    return cup_data

def simulate_match(match_pairing):
    """
    Simulates a single match between two AI teams and determines a winner.
    Updates the match_pairing dictionary with the winner and sets played to True.
    """
    if match_pairing['played']: # Don't re-simulate
        return match_pairing

    # Simple random choice for winner
    winner = random.choice([match_pairing['team1'], match_pairing['team2']])
    match_pairing['winner'] = winner
    match_pairing['played'] = True
    # print(f"Simulated Match: {match_pairing['team1']['name']} vs {match_pairing['team2']['name']} -> Winner: {winner['name']}")
    return match_pairing

def advance_cup_stage(cup_data):
    """
    Processes the current stage's matches, simulates AI matches,
    and prepares the next stage if all current matches are played.
    """
    current_stage_name = CUP_STAGES[cup_data['current_stage_index']]
    current_matches = cup_data['stages'][current_stage_name]

    all_current_stage_matches_played = True

    # Simulate any unplayed AI matches in the current stage
    for match in current_matches:
        if not match['played'] and not match['is_player_match']:
            simulate_match(match) # Simulate AI vs AI

        if not match['played']: # If any match (could be player's) is still not played
            all_current_stage_matches_played = False

    if not all_current_stage_matches_played:
        # Waiting for player match or other simulations if any were deferred
        return cup_data

    # All matches in the current stage are now played, collect winners
    cup_data['advancing_teams'] = [match['winner'] for match in current_matches if match['winner']]

    if not cup_data['advancing_teams'] and len(current_matches) > 0 : # Should not happen if logic is correct
        print("Error: No advancing teams from a played stage!")
        cup_data['status'] = 'error'
        return cup_data

    if cup_data['current_stage_index'] < len(CUP_STAGES) - 1: # If not the final stage
        cup_data['current_stage_index'] += 1
        next_stage_name = CUP_STAGES[cup_data['current_stage_index']]

        new_matches = []
        advancing_teams_shuffled = list(cup_data['advancing_teams']) # Create a mutable copy
        random.shuffle(advancing_teams_shuffled)

        for i in range(0, len(advancing_teams_shuffled), 2):
            if i + 1 < len(advancing_teams_shuffled):
                team1 = advancing_teams_shuffled[i]
                team2 = advancing_teams_shuffled[i+1]
                is_player_match = (team1['id'] == cup_data['player_team']['id'] or \
                                   team2['id'] == cup_data['player_team']['id'])
                new_matches.append({
                    'team1': team1,
                    'team2': team2,
                    'winner': None,
                    'played': False,
                    'is_player_match': is_player_match,
                    'match_id': f"{next_stage_name}_{len(new_matches)+1}"
                })

        cup_data['stages'][next_stage_name] = new_matches
        cup_data['advancing_teams'] = [] # Clear for the next round of advancements
        print(f"Advanced to {next_stage_name}. New matches created.")

    else: # Final stage was just played
        if cup_data['advancing_teams']: # Winner of the final match
            cup_data['cup_winner'] = cup_data['advancing_teams'][0]
            cup_data['status'] = 'finished'
            print(f"Cup Finished! Winner: {cup_data['cup_winner']['name']}")
        else: # Should not happen
            print("Error: Final stage played but no winner found in advancing_teams.")
            cup_data['status'] = 'error'

    return cup_data

def get_next_player_match(cup_data):
    """
    Finds the next unplayed match for the player in the current stage.
    """
    if cup_data['status'] != 'active':
        return None

    current_stage_name = CUP_STAGES[cup_data['current_stage_index']]
    if current_stage_name not in cup_data['stages']:
        return None # Stage not initialized yet

    for match in cup_data['stages'][current_stage_name]:
        if match['is_player_match'] and not match['played']:
            return match
    return None
