# team.py

# Define team colors (RGB tuples)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_PURPLE = (128, 0, 128)
COLOR_ORANGE = (255, 165, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_PINK = (255, 192, 203)
COLOR_BROWN = (165, 42, 42)
COLOR_GREY = (128, 128, 128)
COLOR_GOLD = (255, 215, 0)
COLOR_SILVER = (192, 192, 192)
COLOR_BRONZE = (205, 127, 50)
COLOR_NAVY = (0, 0, 128)
COLOR_TEAL = (0, 128, 128)
COLOR_MAROON = (128, 0, 0)
COLOR_OLIVE = (128, 128, 0)
COLOR_LIME = (0, 128, 0) # Darker green
COLOR_INDIGO = (75, 0, 130)
COLOR_VIOLET = (238, 130, 238)


TEAMS_DATA = [
    {"id": 1, "name": "Red Robins", "skin_id": 1, "color": COLOR_RED},
    {"id": 2, "name": "Blue Blizzards", "skin_id": 2, "color": COLOR_BLUE},
    {"id": 3, "name": "Green Ghosts", "skin_id": 3, "color": COLOR_GREEN},
    {"id": 4, "name": "Yellow Yaks", "skin_id": 4, "color": COLOR_YELLOW},
    {"id": 5, "name": "Purple Penguins", "skin_id": 5, "color": COLOR_PURPLE},
    {"id": 6, "name": "Orange Otters", "skin_id": 6, "color": COLOR_ORANGE},
    {"id": 7, "name": "Cyan Cyclones", "skin_id": 7, "color": COLOR_CYAN},
    {"id": 8, "name": "Pink Panthers", "skin_id": 8, "color": COLOR_PINK},
    {"id": 9, "name": "Brown Bears", "skin_id": 9, "color": COLOR_BROWN},
    {"id": 10, "name": "Grey Geese", "skin_id": 10, "color": COLOR_GREY},
    {"id": 11, "name": "Golden Griffins", "skin_id": 11, "color": COLOR_GOLD},
    {"id": 12, "name": "Silver Sharks", "skin_id": 12, "color": COLOR_SILVER},
    {"id": 13, "name": "Bronze Badgers", "skin_id": 13, "color": COLOR_BRONZE},
    {"id": 14, "name": "Navy Narwhals", "skin_id": 14, "color": COLOR_NAVY},
    {"id": 15, "name": "Teal Turtles", "skin_id": 15, "color": COLOR_TEAL},
    {"id": 16, "name": "Maroon Monkeys", "skin_id": 16, "color": COLOR_MAROON},
    {"id": 17, "name": "Olive Owls", "skin_id": 17, "color": COLOR_OLIVE},
    {"id": 18, "name": "Lime Lions", "skin_id": 18, "color": COLOR_LIME},
    {"id": 19, "name": "Indigo Iguanas", "skin_id": 19, "color": COLOR_INDIGO},
    {"id": 20, "name": "Violet Vultures", "skin_id": 20, "color": COLOR_VIOLET},
]

# Store teams in a dictionary for easy lookup by ID
TEAMS_BY_ID = {team["id"]: team for team in TEAMS_DATA}

def get_team_by_id(team_id):
    """
    Returns the team data for a given team_id.
    Args:
        team_id (int): The ID of the team to retrieve.
    Returns:
        dict: The team data dictionary, or None if not found.
    """
    return TEAMS_BY_ID.get(team_id)

def get_all_teams():
    """
    Returns the full list of team data.
    Returns:
        list: A list of dictionaries, where each dictionary is a team's data.
    """
    return TEAMS_DATA

def get_random_teams(count, exclude_teams_ids=None):
    """
    Selects a specified number of unique random teams, excluding any provided IDs.

    Args:
        count (int): The number of random teams to select.
        exclude_teams_ids (list[int], optional): A list of team IDs to exclude. Defaults to None.

    Returns:
        list[dict]: A list of unique random team objects.
                    Returns an empty list if requirements can't be met (e.g., count too high).
    """
    if exclude_teams_ids is None:
        exclude_teams_ids = []

    available_teams = [team for team in TEAMS_DATA if team["id"] not in exclude_teams_ids]

    if count > len(available_teams):
        print(f"Warning: Requested {count} teams, but only {len(available_teams)} unique teams are available after exclusion.")
        return random.sample(available_teams, len(available_teams)) # Return all available if count is too high

    if count < 0:
        return []

    return random.sample(available_teams, count)

# Example placeholder functions from previous task, can be removed or refactored later
# teams = {
#     "team1": {
    """
    Returns the full list of team data.
    Returns:
        list: A list of dictionaries, where each dictionary is a team's data.
    """
    return TEAMS_DATA

# Example placeholder functions from previous task, can be removed or refactored later
# teams = {
#     "team1": {
#         "name": "Team Alpha",
#         "players": [], # List of Penguin objects
#         "score": 0
#     },
#     "team2": {
#         "name": "Team Beta",
#         "players": [], # List of Penguin objects
#         "score": 0
#     }
# }

# def add_player_to_team(player, team_name):
#     if team_name in teams:
#         teams[team_name]["players"].append(player)
#     else:
#         print(f"Error: Team {team_name} not found.")

# def update_score(team_name, points):
#     if team_name in teams:
#         teams[team_name]["score"] += points
#     else:
#         print(f"Error: Team {team_name} not found.")
