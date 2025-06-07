import pygame

class Penguin:
    def __init__(self, skin_id, x=0, y=0):
        """
        Initializes a Penguin instance.
        Args:
            skin_id (int): The ID of the skin for the penguin (1-20).
            x (int): The initial x-coordinate of the penguin.
            y (int): The initial y-coordinate of the penguin.
        """
        self.skin_id = skin_id
        self.x = x
        self.y = y
        self.skin_image = None  # Will hold the loaded skin image
        self.load_skin(self.skin_id)

    def load_skin(self, skin_id):
        """
        Loads the penguin's skin image based on skin_id.
        For now, it prints the path to the skin.
        """
        self.skin_id = skin_id
        skin_path = f"assets/skins/skin_{self.skin_id}.png"
        print(f"Loading skin: {skin_path}")
        # In the future, this will use pygame.image.load()
        # For now, we'll just store the path for demonstration
        # self.skin_image = pygame.image.load(skin_path).convert_alpha()
        # For placeholder, we can assign a dummy surface if needed for drawing logic
        # self.skin_image = pygame.Surface((50,50)) # Example placeholder surface
        # self.skin_image.fill((255,0,0)) # Fill with red for visibility

    def draw(self, surface):
        """
        Draws the penguin on the given surface.
        For now, it prints a message.
        """
        print(f"Drawing penguin with skin {self.skin_id} at ({self.x}, {self.y})")
        # In the future, this will blit self.skin_image to the surface
        # if self.skin_image:
        #     surface.blit(self.skin_image, (self.x, self.y))
        # else: # Fallback if image not loaded
        #     pygame.draw.rect(surface, (0,0,255), (self.x, self.y, 50, 50)) # Draw a blue square

    def move(self, dx, dy):
        """
        Moves the penguin by dx and dy.
        """
        self.x += dx
        self.y += dy
