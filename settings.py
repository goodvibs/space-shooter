from os import path

# Folder directory
SpaceShooterRedux_dir = path.join(path.dirname(__file__), "SpaceShooterRedux")
Backgrounds_dir = path.join(SpaceShooterRedux_dir, "Backgrounds")
PNG_dir = path.join(SpaceShooterRedux_dir, "PNG")
Lasers_dir = path.join(PNG_dir, "Lasers")
Meteors_dir = path.join(PNG_dir, "Meteors")
Bonus_dir = path.join(SpaceShooterRedux_dir, "Bonus")
Explosions_dir = path.join(PNG_dir, "Explosions")
Powerups_dir = path.join(PNG_dir, "Power-ups")
# Player_damage_dir = path.join(PNG_dir, "Damage")

TITLE = "Space Shooter"
WIDTH = 480
HEIGHT = 600
FPS = 60
SHIELD_BAR_LENGTH = 100
SHIELD_BAR_HEIGHT = 10
GUN_POWERUP_TIME = 5000

# Define useful colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)