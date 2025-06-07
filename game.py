import random
import time
import pygame # Required for drawing text
from team import TEAMS_DATA, get_team_by_id

# Helper to get font, similar to ui.py, can be centralized later
def get_game_font(size):
    return pygame.font.Font(None, size)

# Store the player's chosen team (can be set by a team selection screen later)
# For now, player is fixed as Team 1 from TEAMS_DATA
PLAYER_DEFAULT_TEAM_ID = 1

def start_quick_game():
    """
    Sets up a quick game by selecting a player team and a random AI opponent.
    Returns:
        dict: Information about the match.
    """
    player_team_data = get_team_by_id(PLAYER_DEFAULT_TEAM_ID)
    if not player_team_data:
        # Fallback if team 1 somehow doesn't exist
        player_team_data = {"id": 0, "name": "Default Player", "skin_id": 1, "color": (200,200,200)}

    available_opponents = [team for team in TEAMS_DATA if team["id"] != player_team_data["id"]]
    if not available_opponents:
        # Fallback if only one team exists or player team is not in TEAMS_DATA somehow
        opponent_team_data = {"id": -1, "name": "Default Opponent", "skin_id": 2, "color": (100,100,100)}
    else:
        opponent_team_data = random.choice(available_opponents)

    match_info = {
        'player_team': player_team_data,
        'opponent_team': opponent_team_data,
        'status': 'starting', # Possible statuses: starting, playing, finished
        'winner': None,
        'start_time': time.time() # For simulating game duration
    }
    print(f"Quick Game Started: {player_team_data['name']} vs {opponent_team_data['name']}")
    return match_info

def update_quick_game_state(match_info):
    """
    Updates the state of the quick game.
    For now, simulates game progression with a timer and randomly determines a winner.
    Args:
        match_info (dict): The current match information.
    """
    if match_info['status'] == 'starting':
        # Could have some initial countdown or setup phase
        match_info['status'] = 'playing'
        match_info['start_time'] = time.time() # Reset timer for playing phase

    elif match_info['status'] == 'playing':
        game_duration = 3 # seconds for the simulation
        if time.time() - match_info['start_time'] > game_duration:
            # Game finishes, determine winner
            winner_team = random.choice([match_info['player_team'], match_info['opponent_team']])
            match_info['winner'] = winner_team
            match_info['status'] = 'finished'
            print(f"Game Finished. Winner: {match_info['winner']['name']}")

def draw_quick_game(surface, match_info):
    """
    Displays information about the quick game on the screen.
    Args:
        surface: The Pygame surface to draw on.
        match_info (dict): The current match information.
    """
    font_large = get_game_font(60)
    font_medium = get_game_font(40)
    font_small = get_game_font(30)

    surface.fill((50, 50, 70)) # Dark background for game screen. Consider passing colors or using ui.py definitions

    player_name = match_info.get('player_team', {}).get('name', 'Player') # defensive access
    opponent_name = match_info.get('opponent_team', {}).get('name', 'Opponent')
    player_color = match_info.get('player_team', {}).get('color', (255,255,255))
    opponent_color = match_info.get('opponent_team', {}).get('color', (255,255,255))

    if match_info.get('status') == 'starting' or (match_info.get('status') == 'playing' and match_info.get('minigame_active') is not True) :
        # Show this if minigame is not yet active or if it's just starting phase
        # text = f"{player_name} vs {opponent_name}" # This was not used
        status_text = "Get Ready!" if match_info.get('status') == 'starting' else "Loading Minigame..."

        # Player team text (left)
        player_surf = font_medium.render(player_name, True, player_color)
        player_rect = player_surf.get_rect(center=(surface.get_width() * 0.25, surface.get_height() / 3))
        surface.blit(player_surf, player_rect)

        # Opponent team text (right)
        opponent_surf = font_medium.render(opponent_name, True, opponent_color)
        opponent_rect = opponent_surf.get_rect(center=(surface.get_width() * 0.75, surface.get_height() / 3))
        surface.blit(opponent_surf, opponent_rect)

        # "VS" text
        vs_surf = font_large.render("VS", True, (255,255,255))
        vs_rect = vs_surf.get_rect(center=(surface.get_width() / 2, surface.get_height() / 3))
        surface.blit(vs_surf, vs_rect)

        status_surf = font_small.render(status_text, True, (200,200,200))
        status_rect = status_surf.get_rect(center=(surface.get_width() / 2, surface.get_height() / 2))
        surface.blit(status_surf, status_rect)

    elif match_info.get('status') == 'finished' and match_info.get('winner'):
        winner_name = match_info['winner']['name']
        winner_color = match_info['winner'].get('color', (255,255,0))

        text_content = f"{winner_name} Wins!"
        result_surf = font_large.render(text_content, True, winner_color)
        result_rect = result_surf.get_rect(center=(surface.get_width() / 2, surface.get_height() / 2))
        surface.blit(result_surf, result_rect)

        message_surf = font_small.render("Press Enter to return to menu.", True, (200,200,200))
        message_rect = message_surf.get_rect(center=(surface.get_width() / 2, surface.get_height() * 0.75))
        surface.blit(message_surf, message_rect)
    # If status is 'playing' and minigame is active, draw_player_match_minigame will be called by main.py instead of this part.


# --- Player Match Minigame ---
MINIGAME_BAR_WIDTH = 200
MINIGAME_BAR_HEIGHT = 30
MINIGAME_TARGET_ZONE_WIDTH = 40 # Width of the success zone
MINIGAME_SCREEN_WIDTH_FOR_POS = 800 # Assume fixed screen width for positioning calculations for now


def start_player_match_minigame(match_info):
    """
    Initializes the state for the player match mini-game.
    Args:
        match_info: Dictionary containing player and opponent team info.
    Returns:
        dict: The initial state of the mini-game.
    """
    # Center the bar and target zone for now
    bar_start_x = (MINIGAME_SCREEN_WIDTH_FOR_POS - MINIGAME_BAR_WIDTH) / 2
    target_zone_percentage_start = random.randint(15, 65) # Target zone starts somewhere in the bar

    minigame_state = {
        'bar_pos': 0,  # Percentage of bar width, 0 to 100
        'bar_speed': random.choice([2, 3, 4, -2, -3, -4]), # Speed and direction (percentage per frame)
        'target_zone_start': target_zone_percentage_start, # Percentage
        'target_zone_end': target_zone_percentage_start + (MINIGAME_TARGET_ZONE_WIDTH / MINIGAME_BAR_WIDTH * 100), # Percentage
        'status': 'active',  # 'active', 'finished'
        'result': None,  # 'win', 'loss'
        'bar_display_x': bar_start_x, # For drawing
        'bar_display_y': 300 # Fixed Y position for the bar for now
    }
    # Ensure target_zone_end is not beyond 100
    if minigame_state['target_zone_end'] > 100:
        minigame_state['target_zone_end'] = 100
        minigame_state['target_zone_start'] = 100 - (MINIGAME_TARGET_ZONE_WIDTH / MINIGAME_BAR_WIDTH * 100)

    print(f"Minigame started. Target: {minigame_state['target_zone_start']}-{minigame_state['target_zone_end']}")
    return minigame_state

def update_player_match_minigame(minigame_state, action_pressed):
    """
    Updates the mini-game state based on player input and game logic.
    Args:
        minigame_state: The current state of the mini-game.
        action_pressed (bool): True if the player pressed the action key this frame.
    Returns:
        dict: The updated mini-game state.
    """
    if minigame_state['status'] == 'active':
        minigame_state['bar_pos'] += minigame_state['bar_speed']

        # Bounce bar
        if minigame_state['bar_pos'] > 100:
            minigame_state['bar_pos'] = 100
            minigame_state['bar_speed'] *= -1
        elif minigame_state['bar_pos'] < 0:
            minigame_state['bar_pos'] = 0
            minigame_state['bar_speed'] *= -1

        if action_pressed:
            if minigame_state['target_zone_start'] <= minigame_state['bar_pos'] <= minigame_state['target_zone_end']:
                minigame_state['result'] = 'win'
            else:
                minigame_state['result'] = 'loss'
            minigame_state['status'] = 'finished'
            print(f"Minigame action! Pos: {minigame_state['bar_pos']}, Result: {minigame_state['result']}")
    return minigame_state

def draw_player_match_minigame(surface, minigame_state, match_info):
    """
    Draws the player match mini-game.
    Args:
        surface: The Pygame surface to draw on.
        minigame_state: The current state of the mini-game.
        match_info: Dictionary containing player and opponent team info.
    """
    font_info = get_game_font(30)
    font_result = get_game_font(48)
    font_instr = get_game_font(24)

    # Team names
    player_team = match_info.get('player_team', match_info.get('team1', {'name': 'Player', 'color': (200,200,200)}))
    opponent_team = match_info.get('opponent_team', match_info.get('team2', {'name': 'Opponent', 'color': (200,200,200)}))

    # Use team1 and team2 if player_team/opponent_team not directly in match_info (like in cup matches)
    # This assumes player is team1 in the match_info if player_team is not explicitly set.
    # This logic needs to be robust depending on how match_info is structured for cup vs quick game.
    # For Cup matches, main.py determines who is player_team before calling.
    # For Quick Game, player_team should be in match_info.

    player_name_text = f"Player: {player_team['name']}"
    opponent_name_text = f"Opponent: {opponent_team['name']}"

    player_surf = font_info.render(player_name_text, True, player_team.get('color', (255,255,255)))
    opponent_surf = font_info.render(opponent_name_text, True, opponent_team.get('color', (255,255,255)))

    surface.blit(player_surf, (surface.get_width() / 2 - player_surf.get_width() - 20, 50))
    surface.blit(opponent_surf, (surface.get_width() / 2 + 20, 50))

    if minigame_state['status'] == 'active':
        # Draw the background bar
        bar_bg_rect = pygame.Rect(minigame_state['bar_display_x'], minigame_state['bar_display_y'],
                                  MINIGAME_BAR_WIDTH, MINIGAME_BAR_HEIGHT)
        pygame.draw.rect(surface, (100, 100, 100), bar_bg_rect) # Dark grey bar

        # Draw the target zone
        target_x_pos = minigame_state['bar_display_x'] + (minigame_state['target_zone_start'] / 100 * MINIGAME_BAR_WIDTH)
        target_rect_width = (minigame_state['target_zone_end'] - minigame_state['target_zone_start']) / 100 * MINIGAME_BAR_WIDTH
        target_zone_rect = pygame.Rect(target_x_pos, minigame_state['bar_display_y'],
                                       target_rect_width, MINIGAME_BAR_HEIGHT)
        pygame.draw.rect(surface, (0, 200, 0), target_zone_rect) # Green target zone

        # Draw the moving indicator
        indicator_x_pos = minigame_state['bar_display_x'] + (minigame_state['bar_pos'] / 100 * MINIGAME_BAR_WIDTH)
        indicator_width = 5 # Width of the moving indicator line
        indicator_rect = pygame.Rect(indicator_x_pos - indicator_width / 2, minigame_state['bar_display_y'],
                                     indicator_width, MINIGAME_BAR_HEIGHT)
        pygame.draw.rect(surface, (255, 0, 0), indicator_rect) # Red indicator

        instr_surf = font_instr.render("Pressione ESPAÇO na zona alvo!", True, (0,0,0))
        instr_rect = instr_surf.get_rect(center=(surface.get_width() / 2, minigame_state['bar_display_y'] + MINIGAME_BAR_HEIGHT + 30))
        surface.blit(instr_surf, instr_rect)

    elif minigame_state['status'] == 'finished':
        result_text = "Você Ganhou!" if minigame_state['result'] == 'win' else "Você Perdeu!"
        result_color = (0, 255, 0) if minigame_state['result'] == 'win' else (255, 0, 0)

        result_surf = font_result.render(result_text, True, result_color)
        result_rect = result_surf.get_rect(center=(surface.get_width() / 2, surface.get_height() / 2))
        surface.blit(result_surf, result_rect)

        instr_surf = font_instr.render("Pressione Enter para continuar.", True, (0,0,0))
        instr_rect = instr_surf.get_rect(center=(surface.get_width() / 2, surface.get_height() / 2 + 50))
        surface.blit(instr_surf, instr_rect)


# Placeholder for Game class from previous task, can be refactored or removed if not used by quick_game
# class Game: ... (Removed for brevity as it's not directly used by minigame)
