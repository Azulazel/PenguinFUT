import pygame
from ui import (
    draw_main_menu,
    get_font,
    draw_cup_team_selection_screen,
    draw_tournament_bracket,
    display_message # For messages on top of bracket
)
from game import (
    start_quick_game,
    update_quick_game_state,
    draw_quick_game,
    start_player_match_minigame,
    update_player_match_minigame,
    draw_player_match_minigame
)
from team import TEAMS_DATA, get_team_by_id # For player team selection in cup
from cup import (
    initialize_cup,
    advance_cup_stage,
    get_next_player_match,
    simulate_match as simulate_cup_match, # Keep alias if cup still uses its own simulate
    CUP_STAGES
)

# Initialize Pygame, Font, and Mixer
pygame.mixer.pre_init(44100, -16, 2, 512) # fréquency, size, channels, buffer
pygame.init()
pygame.font.init()
pygame.mixer.init()


# Load Sounds
sounds_loaded = False
try:
    sound_menu_navigate = pygame.mixer.Sound("assets/sounds/menu_navigate.wav")
    sound_menu_select = pygame.mixer.Sound("assets/sounds/menu_select.wav")
    sound_minigame_action = pygame.mixer.Sound("assets/sounds/minigame_action.wav")
    sound_minigame_win = pygame.mixer.Sound("assets/sounds/minigame_win.wav")
    sound_minigame_loss = pygame.mixer.Sound("assets/sounds/minigame_loss.wav")
    sounds_loaded = True
    print("Sounds loaded successfully.")
except pygame.error as e:
    print(f"Warning: Could not load sounds. {e}")
    # Create dummy sound objects if loading fails, so play() calls don't error out
    class DummySound:
        def play(self): pass
    sound_menu_navigate = DummySound()
    sound_menu_select = DummySound()
    sound_minigame_action = DummySound()
    sound_minigame_win = DummySound()
    sound_minigame_loss = DummySound()


# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Penguin Battle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
LOADING_COLOR = (50, 50, 100) # Dark blue for loading - retained for cup_loading

# Game State
current_state = "main_menu"  # main_menu, quick_game_active, cup_team_selection, cup_active, cup_player_match, cup_finished, etc.
menu_options = ["Jogo Rápido", "Copa", "Sair"]
selected_menu_option = 0

# Quick Game Data
current_match_info = None

# Cup Data
current_cup_data = None
active_player_cup_match = None
PLAYER_CHOSEN_TEAM_ID_FOR_CUP = 1
selected_cup_team_index = 0
cup_team_scroll_offset = 0
TEAMS_PER_SELECTION_PAGE = 10

# Minigame State
current_minigame_state = None

# Font for messages
message_font = get_font(40)
small_font = get_font(30)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- Main Menu Event Handling ---
        if current_state == "main_menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_menu_option = (selected_menu_option - 1) % len(menu_options)
                    if sounds_loaded: sound_menu_navigate.play()
                elif event.key == pygame.K_DOWN:
                    selected_menu_option = (selected_menu_option + 1) % len(menu_options)
                    if sounds_loaded: sound_menu_navigate.play()
                elif event.key == pygame.K_RETURN:
                    if sounds_loaded: sound_menu_select.play()
                    selected_action = menu_options[selected_menu_option]
                    print(f"Menu Selected: {selected_action}")
                    if selected_action == "Jogo Rápido":
                        current_match_info = start_quick_game()
                        current_state = "quick_game_active"
                    elif selected_action == "Copa":
                        selected_cup_team_index = 0 # Reset selection
                        cup_team_scroll_offset = 0
                        current_state = "cup_team_selection"
                    elif selected_action == "Sair":
                        running = False

        # --- Quick Game Event Handling ---
        elif current_state == "quick_game_active":
            action_this_frame = False
            if current_match_info:
                if event.type == pygame.KEYDOWN:
                    if current_minigame_state and current_minigame_state.get('status') == 'active':
                        if event.key == pygame.K_SPACE:
                            action_this_frame = True
                            if sounds_loaded: sound_minigame_action.play()
                    elif current_match_info.get('status') == 'finished' or \
                         (current_minigame_state and current_minigame_state.get('status') == 'finished'):
                        if event.key == pygame.K_RETURN: # After minigame/match is done
                            current_state = "main_menu"
                            current_match_info = None
                            current_minigame_state = None

            # Minigame update is now part of general state updates section below event loop for quick game
            if current_minigame_state and current_minigame_state.get('status') == 'active':
                 current_minigame_state = update_player_match_minigame(current_minigame_state, action_this_frame)


        # --- Cup Team Selection Event Handling ---
        elif current_state == "cup_team_selection":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_cup_team_index = (selected_cup_team_index + 1) % len(TEAMS_DATA)
                    if sounds_loaded: sound_menu_navigate.play()
                    if selected_cup_team_index >= cup_team_scroll_offset + TEAMS_PER_SELECTION_PAGE:
                        cup_team_scroll_offset = selected_cup_team_index - TEAMS_PER_SELECTION_PAGE + 1
                    if selected_cup_team_index < cup_team_scroll_offset:
                         cup_team_scroll_offset = selected_cup_team_index
                elif event.key == pygame.K_UP:
                    selected_cup_team_index = (selected_cup_team_index - 1 + len(TEAMS_DATA)) % len(TEAMS_DATA)
                    if sounds_loaded: sound_menu_navigate.play()
                    if selected_cup_team_index < cup_team_scroll_offset:
                        cup_team_scroll_offset = selected_cup_team_index
                    elif selected_cup_team_index >= cup_team_scroll_offset + TEAMS_PER_SELECTION_PAGE:
                        cup_team_scroll_offset = selected_cup_team_index - TEAMS_PER_SELECTION_PAGE + 1
                elif event.key == pygame.K_RETURN:
                    if sounds_loaded: sound_menu_select.play()
                    PLAYER_CHOSEN_TEAM_ID_FOR_CUP = TEAMS_DATA[selected_cup_team_index]['id']
                    current_cup_data = initialize_cup(PLAYER_CHOSEN_TEAM_ID_FOR_CUP)
                    player_team_name = current_cup_data['player_team']['name']
                    print(f"Cup initialized. Player is {player_team_name}. Starting {CUP_STAGES[0]}.")
                    current_state = "cup_active"

        # --- Cup Player Match Event Handling (Placeholder) ---
        elif current_state == "cup_player_match":
            if event.type == pygame.KEYDOWN: # This is for RETURN after minigame is done
                if current_minigame_state and current_minigame_state.get('status') == 'finished':
                    if event.key == pygame.K_RETURN:
                        # Sound for advancing/confirming after minigame result already played by minigame win/loss
                        current_state = "cup_active"
                        active_player_cup_match = None
                        current_minigame_state = None
                # Spacebar for active minigame action is handled in the State Updates section for cup_player_match now

        # --- Cup Finished Event Handling ---
        elif current_state == "cup_finished":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    current_state = "main_menu"
                    current_cup_data = None


    # --- State Updates (outside event loop for continuous processing) ---
    if current_state == "quick_game_active" and current_match_info:
        # If match is 'playing' and minigame not started, start it
        if current_match_info.get('status') == 'playing' and not current_minigame_state:
            current_minigame_state = start_player_match_minigame(current_match_info)
            current_match_info['minigame_active'] = True # Flag to change drawing

        # If minigame is finished, determine overall match winner
        if current_minigame_state and current_minigame_state.get('status') == 'finished' and \
           current_match_info.get('status') == 'playing': # Ensure we only process this once
            if current_minigame_state.get('result') == 'win':
                current_match_info['winner'] = current_match_info['player_team']
                if sounds_loaded: sound_minigame_win.play()
            else:
                current_match_info['winner'] = current_match_info['opponent_team']
                if sounds_loaded: sound_minigame_loss.play()
            current_match_info['status'] = 'finished' # Mark match as finished
            current_match_info['minigame_active'] = False # Minigame interaction is done

        # Original timer logic (if any) from update_quick_game_state
        if not (current_minigame_state and current_match_info.get('minigame_active')):
             update_quick_game_state(current_match_info)

    # No update logic for "cup_team_selection" here, it's event-driven for navigation/selection.

    elif current_state == "cup_player_match":
        action_this_frame_cup = False
        # Proper event handling for cup minigame action (Spacebar)
        # This needs to be done in the main event loop, similar to quick_game_active state.
        # For now, we'll check here, but it's better to set a flag in the event loop.
        # Simplified: Assuming event loop sets action_this_frame_cup if space is pressed in this state.
        # The event loop section for cup_player_match needs to be added/adjusted for K_SPACE.
        # Let's assume it's done and action_this_frame_cup is correctly set.

        # Check for Spacebar press for cup minigame (Action key)
        # This part of the logic should be in the event handling section for current_state == "cup_player_match"
        # For now, action_this_frame_cup is assumed to be set correctly if space was pressed.
        # We'll add the actual event check now.
        for event in pygame.event.get(pygame.KEYDOWN): # Consume and check only keydown
            if event.key == pygame.K_SPACE:
                if current_minigame_state and current_minigame_state.get('status') == 'active':
                    action_this_frame_cup = True
                    if sounds_loaded: sound_minigame_action.play()
            else: # Post back other keydown events, or all non-keydown events
                 pygame.event.post(event)
        for event in pygame.event.get((pygame.QUIT, pygame.KEYUP)): # Handle quit and other event types
            pygame.event.post(event)


        if not current_minigame_state:
            if active_player_cup_match:
                current_minigame_state = start_player_match_minigame(active_player_cup_match)

        if current_minigame_state and current_minigame_state.get('status') == 'active':
            current_minigame_state = update_player_match_minigame(current_minigame_state, action_this_frame_cup)

        if current_minigame_state and current_minigame_state.get('status') == 'finished':
            # Winner determination for cup match based on minigame
            if active_player_cup_match and not active_player_cup_match.get('played'): # process only once
                player_is_team1 = active_player_cup_match['team1']['id'] == current_cup_data['player_team']['id']

                if current_minigame_state.get('result') == 'win':
                    active_player_cup_match['winner'] = current_cup_data['player_team']
                else: # Player lost
                    active_player_cup_match['winner'] = active_player_cup_match['team2'] if player_is_team1 else active_player_cup_match['team1']

                active_player_cup_match['played'] = True
                print(f"Cup Player Match ({active_player_cup_match['team1']['name']} vs {active_player_cup_match['team2']['name']}) minigame done. Winner: {active_player_cup_match['winner']['name']}")
                # Note: State transition back to cup_active happens on Enter press in event loop

    elif current_state == "cup_active":
        # This logic was moved up slightly to be before the drawing section in previous example,
        # but it's an update step so conceptually it fits here.
        if current_cup_data and current_cup_data.get('status') == 'active':
            player_match_pending = get_next_player_match(current_cup_data)
            if player_match_pending:
                active_player_cup_match = player_match_pending
                current_minigame_state = None # Ensure minigame is fresh for this match
                current_state = "cup_player_match"
                print(f"Next player cup match: {active_player_cup_match['team1']['name']} vs {active_player_cup_match['team2']['name']}")
            else:
                current_stage_name = CUP_STAGES[current_cup_data['current_stage_index']]
                all_matches_in_stage_played = all(m['played'] for m in current_cup_data['stages'][current_stage_name])
                if all_matches_in_stage_played:
                    current_cup_data = advance_cup_stage(current_cup_data)
                    if current_cup_data.get('status') == 'finished':
                        current_state = "cup_finished"
                    elif current_cup_data.get('status') == 'active':
                        new_stage_name = CUP_STAGES[current_cup_data['current_stage_index']]
                        print(f"Advanced to {new_stage_name} in cup. Simulating...")
                else:
                    # This implies AI matches might still be pending for simulation in current stage.
                    # advance_cup_stage in cup.py should handle simulating these if no player match is pending.
                    # If it's stuck here, review cup.py's advance_cup_stage logic for AI match simulation.
                    print(f"Waiting for AI matches in {current_stage_name} or player match logic error.")
                    current_cup_data = advance_cup_stage(current_cup_data) # Try to force simulation

    # --- Drawing based on state ---
    screen.fill(WHITE)
    if current_state == "main_menu":
        draw_main_menu(screen, menu_options, selected_menu_option)

    elif current_state == "quick_game_active" and current_match_info:
        if current_minigame_state and current_match_info.get('minigame_active', False):
            draw_player_match_minigame(screen, current_minigame_state, current_match_info)
        elif current_minigame_state and current_minigame_state.get('status') == 'finished': # Show minigame result before Enter
            draw_player_match_minigame(screen, current_minigame_state, current_match_info)
        else: # Before minigame starts or after match truly finished (Enter pressed)
            draw_quick_game(screen, current_match_info)


    elif current_state == "cup_team_selection":
        draw_cup_team_selection_screen(screen, TEAMS_DATA, selected_cup_team_index, cup_team_scroll_offset, TEAMS_PER_SELECTION_PAGE)

    elif current_state == "cup_active":
        if current_cup_data:
            draw_tournament_bracket(screen, current_cup_data)
            stage_name = CUP_STAGES[current_cup_data['current_stage_index']]
            display_message(screen, f"Copa: {stage_name} - Simulando Jogos...", SCREEN_WIDTH / 2, 20, size=30, color=BLACK)


    elif current_state == "cup_player_match":
        if current_cup_data: # Draw bracket in background
            draw_tournament_bracket(screen, current_cup_data)
        if current_minigame_state and active_player_cup_match:
            # Pass active_player_cup_match as the 'match_info' for the minigame drawer
            # It needs player_team and opponent_team, which might be team1 and team2 in cup matches
            # Ensure draw_player_match_minigame can handle this structure.
            # We might need to map team1/team2 to player_team/opponent_team for it.
            # For now, assuming draw_player_match_minigame was updated to handle team1/team2.
            # Or, create a temporary match_info for it:
            temp_minigame_match_info = {
                'player_team': current_cup_data['player_team'], # Player is always player_team
                'opponent_team': active_player_cup_match['team2'] if active_player_cup_match['team1']['id'] == current_cup_data['player_team']['id'] else active_player_cup_match['team1']
            }
            draw_player_match_minigame(screen, current_minigame_state, temp_minigame_match_info)
        elif active_player_cup_match : # Minigame not started yet, show prompt
             team1_name = active_player_cup_match['team1']['name']
             team2_name = active_player_cup_match['team2']['name']
             overlay_text = f"Seu Próximo Jogo: {team1_name} vs {team2_name}. Carregando..."
             display_message(screen, overlay_text, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, size=32, color=(0,0,150))


    elif current_state == "cup_finished":
        if current_cup_data:
            draw_tournament_bracket(screen, current_cup_data)
            display_message(screen, "Pressione Enter para voltar ao Menu.", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 15, size=28, color=BLACK)

    pygame.display.flip()

# Quit Pygame
pygame.mixer.quit()
pygame.font.quit()
pygame.quit()
