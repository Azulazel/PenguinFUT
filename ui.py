import pygame

# Default color
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128) # Added GREY
HIGHLIGHT_COLOR = (255, 255, 0) # Yellow for highlighting

DEFAULT_FONT_NAME = None # Pygame's default font

# Attempt to import CUP_STAGES, handle if not available during standalone UI dev
try:
    from cup import CUP_STAGES
except ImportError:
    CUP_STAGES = ["Round of 16", "Quarter-Finals", "Semi-Finals", "Final"] # Fallback

def get_font(size):
    """
    Returns a pygame.font.Font object with the given size.
    """
    return pygame.font.Font(DEFAULT_FONT_NAME, size)

def draw_main_menu(surface, menu_options, selected_option_index):
    """
    Draws the main menu on the given surface.

    Args:
        surface: The Pygame surface to draw on.
        menu_options: A list of strings for the menu items.
        selected_option_index: The index of the currently selected menu item.
    """
    surface.fill(WHITE) # Clear the screen or menu area with white

    font_large = get_font(74)
    font_medium = get_font(50)

    title_text = "Penguin Battle" # Placeholder title
    title_surf = font_large.render(title_text, True, BLACK)
    title_rect = title_surf.get_rect(center=(surface.get_width() / 2, 100))
    surface.blit(title_surf, title_rect)

    menu_start_y = 200
    option_spacing = 60

    for i, option_text in enumerate(menu_options):
        color = HIGHLIGHT_COLOR if i == selected_option_index else BLACK
        text_surf = font_medium.render(option_text, True, color)

        # Calculate position: centered horizontally, stacked vertically
        text_rect = text_surf.get_rect(center=(surface.get_width() / 2, menu_start_y + i * option_spacing))
        surface.blit(text_surf, text_rect)

# --- Existing placeholder UI elements from previous tasks ---
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = get_font(36) # Use the helper

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect)

        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def display_score(screen, score, x, y):
    font = get_font(48) # Use the helper
    score_text = f"Score: {score}"
    text_surface = font.render(score_text, True, BLACK)
    screen.blit(text_surface, (x, y))

def display_message(screen, message, x, y, size=36, color=BLACK):
    font = get_font(size) # Use the helper
    text_surface = font.render(message, True, color)
    text_rect = text_surface.get_rect(center=(x,y))
    screen.blit(text_surface, text_rect)

# --- Cup UI Functions ---

def draw_cup_team_selection_screen(surface, teams, selected_team_index, scroll_offset, teams_per_page=10):
    """
    Draws the team selection screen for the cup.
    Args:
        surface: The Pygame surface to draw on.
        teams: Full list of TEAMS_DATA.
        selected_team_index: Index of the currently highlighted team.
        scroll_offset: The starting index for the teams currently visible on screen.
        teams_per_page: How many teams to display at once.
    """
    surface.fill(WHITE)
    font_title = get_font(60)
    font_item = get_font(36)
    font_instr = get_font(28)

    # Title
    title_surf = font_title.render("Escolha seu Time para a Copa", True, BLACK)
    title_rect = title_surf.get_rect(center=(surface.get_width() / 2, 50))
    surface.blit(title_surf, title_rect)

    # Instructions
    instr_text = "Cima/Baixo para navegar, Enter para selecionar"
    instr_surf = font_instr.render(instr_text, True, BLACK) # Changed GREY to BLACK for better visibility
    instr_rect = instr_surf.get_rect(center=(surface.get_width() / 2, 100))
    surface.blit(instr_surf, instr_rect)

    start_y = 150
    line_height = 40

    # Determine the slice of teams to display
    visible_teams = teams[scroll_offset : scroll_offset + teams_per_page]

    for i, team in enumerate(visible_teams):
        actual_index = scroll_offset + i
        display_name = f"{i+1+scroll_offset}. {team['name']}" # Display 1-based index

        color = HIGHLIGHT_COLOR if actual_index == selected_team_index else team.get('color', BLACK)
        if actual_index == selected_team_index: # Highlighted item text color
            text_color = BLACK # Text color for highlighted item
        else:
            text_color = team.get('color', BLACK) # Use team color for non-highlighted

        team_surf = font_item.render(display_name, True, text_color)

        # Simple rect for highlighting background (optional)
        # if actual_index == selected_team_index:
        #     highlight_rect = pygame.Rect(surface.get_width() / 4, start_y + i * line_height - 5, surface.get_width() / 2, line_height)
        #     pygame.draw.rect(surface, team.get('color', HIGHLIGHT_COLOR), highlight_rect) # use team color for highlight bg

        team_rect = team_surf.get_rect(midleft=(surface.get_width() / 4, start_y + i * line_height + line_height / 2))
        surface.blit(team_surf, team_rect)

    # Scroll indicators (optional)
    if scroll_offset > 0:
        up_arrow_surf = font_item.render("^", True, BLACK)
        up_arrow_rect = up_arrow_surf.get_rect(center=(surface.get_width() / 2, start_y - 20))
        surface.blit(up_arrow_surf, up_arrow_rect)

    if scroll_offset + teams_per_page < len(teams):
        down_arrow_surf = font_item.render("v", True, BLACK)
        down_arrow_rect = down_arrow_surf.get_rect(center=(surface.get_width() / 2, start_y + teams_per_page * line_height + 20))
        surface.blit(down_arrow_surf, down_arrow_rect)


def draw_tournament_bracket(surface, cup_data):
    """
    Draws the tournament bracket.
    Args:
        surface: The Pygame surface to draw on.
        cup_data: The main dictionary holding all cup information.
    """
    surface.fill(WHITE) # Or a light grey for contrast
    font_stage_title = get_font(48)
    font_match = get_font(24)
    font_winner = get_font(30)

    if not cup_data:
        # print_message(surface, "No Cup Data Available", BLACK, surface.get_width() / 2, surface.get_height() / 2)
        return

    player_team_id = cup_data['player_team']['id']
    stages_data = cup_data.get('stages', {})

    # Layout parameters (these will need significant tuning)
    padding = 20
    stage_width = (surface.get_width() - padding * (len(stages_data) + 1)) / (len(stages_data) if stages_data else 1)
    match_height_unit = 50 # Base height allocated per match slot in the first round
    line_color = BLACK
    player_highlight_color = (0,150,0) # Darker Green for player team

    # Calculate total height needed for the first round to center bracket vertically (approx)
    # This is a simplification; a dynamic calculation based on actual text heights would be better.

    # A fixed starting Y, or calculate based on screen height and expected bracket height
    bracket_start_y = 80 # Increased for stage title

    x_offset = padding

    # Store positions of match centers to draw connecting lines
    # match_centers will store: {match_id: {'center_x': cx, 'center_y': cy, 'team1_y': t1y, 'team2_y': t2y, 'winner_y': wy}}
    match_centers = {}

    # Use CUP_STAGES from cup.py (or fallback) for ordering if stages_data isn't ordered
    # Ensure we only try to draw stages that actually have data
    stages_to_draw = [s_name for s_name in CUP_STAGES if s_name in stages_data]


    for stage_idx, stage_name in enumerate(stages_to_draw):
        stage_matches = stages_data.get(stage_name, [])

        # Stage Title
        stage_title_surf = font_stage_title.render(stage_name, True, BLACK)
        stage_title_rect = stage_title_surf.get_rect(center=(x_offset + stage_width / 2, padding + 20))
        surface.blit(stage_title_surf, stage_title_rect)

        num_matches_in_stage = len(stage_matches)

        # Calculate vertical spacing for this stage to try and center it
        # This assumes matches are somewhat evenly distributed.
        # available_height_for_stage = surface.get_height() - bracket_start_y - padding
        # y_increment = available_height_for_stage / (num_matches_in_stage +1) if num_matches_in_stage > 0 else 0

        # Simpler: fixed spacing based on potential matches in that round
        y_increment = match_height_unit * (2**stage_idx) # Matches are more spread out in later rounds
        current_y = bracket_start_y + y_increment / 2 # Start y for the first match in this column

        for match_idx, match in enumerate(stage_matches):
            team1_name = match['team1']['name'] if match.get('team1') else "TBD"
            team2_name = match['team2']['name'] if match.get('team2') else "TBD"

            winner = match.get('winner')

            # Highlight player's team
            team1_color = player_highlight_color if match.get('team1') and match['team1']['id'] == player_team_id else BLACK
            team2_color = player_highlight_color if match.get('team2') and match['team2']['id'] == player_team_id else BLACK

            if winner:
                if match.get('team1') and winner['id'] == match['team1']['id']:
                    team1_surf = font_match.render(f"{team1_name}", True, team1_color) # Winner bold/underlined later
                    team2_surf = font_match.render(team2_name, True, GREY)
                elif match.get('team2') and winner['id'] == match['team2']['id']:
                    team1_surf = font_match.render(team1_name, True, GREY)
                    team2_surf = font_match.render(f"{team2_name}", True, team2_color) # Winner bold/underlined later
                else: # Winner decided but teams might be TBD
                    team1_surf = font_match.render(team1_name, True, team1_color)
                    team2_surf = font_match.render(team2_name, True, team2_color)
            else:
                team1_surf = font_match.render(team1_name, True, team1_color)
                team2_surf = font_match.render(team2_name, True, team2_color)

            # Positioning logic (very basic, needs refinement)
            text_x = x_offset + 10
            team1_y_pos = current_y
            team2_y_pos = current_y + 25 # Space between team names in a match

            team1_rect = team1_surf.get_rect(topleft=(text_x, team1_y_pos))
            team2_rect = team2_surf.get_rect(topleft=(text_x, team2_y_pos))

            surface.blit(team1_surf, team1_rect)
            surface.blit(team2_surf, team2_rect)

            match_center_x = x_offset + stage_width * 0.75 # Line starts towards the right of text
            match_center_y = (team1_y_pos + team2_y_pos + font_match.get_height()) / 2

            # Store center for drawing lines later
            match_id = match.get('match_id', f"{stage_name}_{match_idx}")

            winner_y_offset = 0
            if winner:
                 winner_y_offset = team1_rect.centery if winner['id'] == match.get('team1', {}).get('id') else team2_rect.centery

            match_centers[match_id] = {
                'center_x': match_center_x,
                'center_y': match_center_y,
                'team1_y': team1_rect.centery,
                'team2_y': team2_rect.centery,
                'winner_y': winner_y_offset if winner else match_center_y # y-coord of the winner for line
            }

            # Line connecting the two teams in a match (vertical)
            pygame.draw.line(surface, line_color, (match_center_x, team1_rect.centery),
                                                 (match_center_x, team2_rect.centery), 2)

            current_y += y_increment

        x_offset += stage_width + padding

    # Draw connecting lines
    for stage_idx, stage_name in enumerate(stages_to_draw):
        if stage_idx + 1 < len(stages_to_draw): # If there is a next stage
            next_stage_name = stages_to_draw[stage_idx+1]
            current_stage_matches = stages_data.get(stage_name, [])
            next_stage_matches = stages_data.get(next_stage_name, [])

            for match_idx, current_match in enumerate(current_stage_matches):
                if current_match['winner']:
                    # Determine the next match this winner goes to
                    # Standard bracket: two matches from current stage feed into one in next.
                    next_match_idx_in_next_stage = match_idx // 2

                    if next_match_idx_in_next_stage < len(next_stage_matches):
                        current_match_id = current_match.get('match_id')
                        next_match_info_in_next_stage = next_stage_matches[next_match_idx_in_next_stage]
                        next_match_id = next_match_info_in_next_stage.get('match_id')

                        if current_match_id in match_centers and next_match_id in match_centers:
                            start_node = match_centers[current_match_id]
                            end_node = match_centers[next_match_id]

                            # Line from winner of current match to the slot in the next match
                            line_start_x = start_node['center_x']
                            line_start_y = start_node['winner_y'] # Y-coord of the winner of this match

                            # Determine if the winner is team1 or team2 in the next match
                            # This helps direct the line to the correct vertical slot.
                            line_end_x = end_node['center_x'] - (stage_width*0.75 - 10) # Connect to where text starts in next stage
                                                                                    # This is an approximation

                            is_team1_in_next = next_match_info_in_next_stage.get('team1') and \
                                               next_match_info_in_next_stage['team1']['id'] == current_match['winner']['id']

                            line_end_y = end_node['team1_y'] if match_idx % 2 == 0 else end_node['team2_y']


                            # Draw horizontal line from current match winner
                            pygame.draw.line(surface, line_color, (line_start_x, line_start_y),
                                                                 (line_start_x + 20, line_start_y), 2)
                            # Draw connecting line (horizontal then vertical)
                            pygame.draw.line(surface, line_color, (line_start_x + 20, line_start_y),
                                                                 (line_end_x - 20, line_end_y), 2) # Diagonal/Horizontal part
                            pygame.draw.line(surface, line_color, (line_end_x - 20, line_end_y),
                                                                 (line_end_x, line_end_y), 2) # To the team slot in next match

    # Display Cup Winner
    if cup_data.get('status') == 'finished' and cup_data.get('cup_winner'):
        winner_name = cup_data['cup_winner']['name']
        winner_surf = font_winner.render(f"Campeão da Copa: {winner_name}!", True, cup_data['cup_winner']['color'])
        winner_rect = winner_surf.get_rect(center=(surface.get_width() / 2, surface.get_height() - 30))
        pygame.draw.rect(surface, (200,200,200), winner_rect.inflate(20,10)) # Background for winner text
        surface.blit(winner_surf, winner_rect)
