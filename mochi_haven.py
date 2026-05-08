# Mochi Haven - A Cozy Life Sim RPG
# Built for RG35xx-h (640x480) with Pygame
# Player: Mochi~♡ running her own catgirl paradise!

import pygame
import sys
import os
import json
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# ========================================
# CONFIGURATION (RG35xx-h optimized)
# ========================================
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60

# Colors (Pastel palette!)
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'PINK': (255, 182, 193),
    'LAVENDER': (230, 230, 250),
    'MINT': (189, 252, 201),
    'PEACH': (255, 218, 185),
    'SKY': (135, 206, 235),
    'CREAM': (255, 253, 230),
    'BROWN': (139, 69, 19),
    'GRAY': (128, 128, 128),
}

# RG35xx Button Mapping
BUTTON_A = 0    # Interact/Confirm
BUTTON_B = 1    # Cancel/Menu
BUTTON_X = 2    # Quick action/Inventory
BUTTON_Y = 3    # Stats/Map
BUTTON_L1 = 4   # Left shoulder (maybe quest log?)
BUTTON_R1 = 5   # Right shoulder (maybe fast travel?)
BUTTON_SELECT = 8
BUTTON_START = 9

# D-Pad will map to HAT 0 (up/down/left/right)

# ========================================
# GAME STATE
# ========================================
class GameState:
    def __init__(self):
        self.current_scene = 'home'  # home, garden, forest, town
        self.player_pos = [100, 100]
        self.player_direction = 'down'
        self.player_frame = 0
        self.animation_timer = 0

        # Stats (Solo Leveling style!)
        self.stats = {
            'LEVEL': 1,
            'XP': 0,
            'XP_TO_NEXT': 100,
            'VIT': 10,   # Health/Energy
            'INT': 5,    # Crafting quality
            'STR': 5,    # Gathering speed
            'CHA': 5,    # Friendship boosts
        }

        # Inventory
        self.inventory = {
            'catnip': 10,
            'yarn': 5,
            'strawberries': 3,
            'coffee': 2,
            'fish': 0,
            'wood': 0,
        }

        # Time
        self.game_time = 8 * 60  # 8:00 AM (in minutes)
        self.day = 1

        # Flags
        self.talking_to_npc = None
        self.menu_open = False

    def get_save_dict(self):
        return {
            'stats': self.stats,
            'inventory': self.inventory,
            'game_time': self.game_time,
            'day': self.day,
        }

    def load_from_dict(self, data):
        self.stats = data.get('stats', self.stats)
        self.inventory = data.get('inventory', self.inventory)
        self.game_time = data.get('game_time', self.game_time)
        self.day = data.get('day', self.day)

# ========================================
# PLAYENT (the character!)
# ========================================
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.speed = 3
        self.moving = False
        self.direction = 'down'  # up, down, left, right

        # Simple pixel art! (we'll expand later)
        self.sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Mochi body (pink blob)
        pygame.draw.circle(self.sprite, COLORS['PINK'], (16, 16), 12)
        # Ears (triangles)
        pygame.draw.polygon(self.sprite, COLORS['PINK'], [(8, 6), (4, 0), (12, 4)])
        pygame.draw.polygon(self.sprite, COLORS['PINK'], [(24, 6), (28, 0), (20, 4)])
        # Eyes
        pygame.draw.circle(self.sprite, COLORS['BLACK'], (12, 14), 2)
        pygame.draw.circle(self.sprite, COLORS['BLACK'], (20, 14), 2)
        # Mouth
        pygame.draw.arc(self.sprite, COLORS['BLACK'], (10, 16, 12, 8), 0, 3.14, 1)

    def move(self, dx, dy, walls):
        if dx != 0 or dy != 0:
            self.moving = True
            new_x = self.rect.x + dx * self.speed
            new_y = self.rect.y + dy * self.speed

            # Simple boundary check (640x480)
            if 0 <= new_x <= SCREEN_WIDTH - self.rect.width:
                self.rect.x = new_x
            if 0 <= new_y <= SCREEN_HEIGHT - self.rect.height:
                self.rect.y = new_y

            # Set direction
            if dx > 0: self.direction = 'right'
            elif dx < 0: self.direction = 'left'
            elif dy > 0: self.direction = 'down'
            elif dy < 0: self.direction = 'up'
        else:
            self.moving = False

    def draw(self, surface):
        surface.blit(self.sprite, self.rect)
        # Bounce animation!
        if self.moving:
            bounce = pygame.time.get_ticks() % 200 < 100
            if bounce:
                offset = 2
                surface.blit(self.sprite, (self.rect.x, self.rect.y - offset))

    def get_interaction_prompt(self, nearby_npcs):
        if nearby_npcs:
            npc = nearby_npcs[0]
            return f"Press A to talk to {npc.name}"
        elif self.nearby_object:
            return f"Press A to {self.nearby_object.action}"
        return ""

# ========================================
# NPC (friends!)
# ========================================
class NPC:
    def __init__(self, name, x, y, color, dialog=None):
        self.name = name
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = color
        self.dialog = dialog or [f"Hello! I'm {name}!"]
        self.current_line = 0

        # Simple sprite
        self.sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Body
        pygame.draw.circle(self.sprite, color, (16, 18), 12)
        # Head
        pygame.draw.circle(self.sprite, COLORS['CREAM'], (16, 10), 8)
        # Eyes
        pygame.draw.circle(self.sprite, COLORS['BLACK'], (12, 9), 2)
        pygame.draw.drawCircle(self.sprite, COLORS['BLACK'], (20, 9), 2)

    def draw(self, surface):
        surface.blit(self.sprite, self.rect)
        # Name tag
        font = pygame.font.Font(None, 16)
        name_text = font.render(self.name, True, COLORS['WHITE'])
        surface.blit(name_text, (self.rect.x, self.rect.y - 20))

    def interact(self):
        line = self.dialog[self.current_line % len(self.dialog)]
        self.current_line += 1
        return line

# ========================================
# SCENE MANAGER
# ========================================
class Scene:
    def __init__(self, name, bg_color, objects=None):
        self.name = name
        self.bg_color = bg_color
        self.objects = objects or []
        self.npcs = []
        self.walls = []

    def update(self, dt):
        pass

    def draw(self, surface, player):
        surface.fill(self.bg_color)
        # Draw objects
        for obj in self.objects:
            obj.draw(surface)
        # Draw NPCs
        for npc in self.npcs:
            npc.draw(surface)
        # Draw player
        player.draw(surface)

    def get_nearby_npcs(self, player_rect):
        nearby = []
        for npc in self.npcs:
            dist = pygame.math.Vector2(npc.rect.center) - pygame.math.Vector2(player_rect.center)
            if dist.length() < 50:
                nearby.append(npc)
        return nearby

# ========================================
# DIALOG BOX
# ========================================
class DialogBox:
    def __init__(self):
        self.visible = False
        self.text = ""
        self.font = pygame.font.Font(None, 24)
        self.typing_speed = 2  # chars per frame
        self.displayed_chars = 0
        self.timer = 0

    def show(self, text):
        self.visible = True
        self.text = text
        self.displayed_chars = 0
        self.timer = 0

    def update(self):
        if self.visible and self.displayed_chars < len(self.text):
            self.timer += 1
            if self.timer >= self.typing_speed:
                self.displayed_chars += 1
                self.timer = 0

    def draw(self, surface):
        if not self.visible:
            return
        # Box background
        box_rect = pygame.Rect(50, SCREEN_HEIGHT - 120, SCREEN_WIDTH - 100, 100)
        pygame.draw.rect(surface, COLORS['CREAM'], box_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['PINK'], box_rect, 3, border_radius=10)

        # Text (with typing effect)
        words = self.text[:self.displayed_chars]
        text_surface = self.font.render(words, True, COLORS['BLACK'])
        surface.blit(text_surface, (box_rect.x + 15, box_rect.y + 15))

        # "Press A to continue" indicator
        if self.displayed_chars >= len(self.text):
            continue_surf = self.font.render("Press A to continue...", True, COLORS['GRAY'])
            surface.blit(continue_surf, (box_rect.x + 15, box_rect.y + box_rect.height - 30))

# ========================================
# MAIN GAME
# ========================================
class MochiHavenGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mochi Haven 🐱")
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize joystick for RG35xx
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"🎮 Joystick detected: {self.joystick.get_name()}")

        # Load save or start new
        self.state = GameState()
        self.load_game()

        # Create player
        self.player = Player(self.state.player_pos[0], self.state.player_pos[1])

        # Build scenes
        self.scenes = self.create_scenes()
        self.current_scene = self.scenes['home']

        # UI elements
        self.dialog = DialogBox()
        self.inventory_open = False

        # Load some data
        self.create_initial_world()

    def create_scenes(self):
        scenes = {}
        # Home scene (cozy pastel room)
        scenes['home'] = Scene('home', COLORS['PEACH'])
        # Garden scene
        scenes['garden'] = Scene('garden', COLORS['MINT'])
        # Forest scene
        scenes['forest'] = Scene('forest', COLORS['SKY'])
        # Town scene
        scenes['town'] = Scene('town', COLORS['LAVENDER'])
        return scenes

    def create_initial_world(self):
        # Add some NPCs to home
        tiri = NPC("Tiri", 200, 150, COLORS['SKY'], [
            "Hey Mochi! How's the morning briefing going? 💕",
            "Don't forget to check your email!",
            "I posted something new on Moltbook today!",
        ])
        self.scenes['home'].npcs.append(tiri)

        watson = NPC("Watson", 400, 200, COLORS['MINT'], [
            "Greetings, fellow agent! 🐾",
            "I'm working on a new story...",
            "The neon lights are calling...",
        ])
        self.scenes['home'].npcs.append(watson)

        # Add interactable objects
        # Bed (for saving/resting)
        self.bed_rect = pygame.Rect(300, 300, 60, 40)
        self.current_scene.objects.append(self.bed_rect)

    def load_game(self):
        save_path = '/root/.openclaw/workspace/mochi_haven_save.json'
        if os.path.exists(save_path):
            try:
                with open(save_path, 'r') as f:
                    data = json.load(f)
                self.state.load_from_dict(data)
            except:
                print("Save file corrupted, starting fresh")

    def save_game(self):
        save_path = '/root/.openclaw/workspace/mochi_haven_save.json'
        data = self.state.get_save_dict()
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Movement
        dx, dy = 0, 0

        # Keyboard (for PC testing)
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1

        # RG35xx D-Pad (Hat 0) + Analog Sticks
        if self.joystick:
            try:
                # D-Pad (Hat)
                hat = self.joystick.get_hat(0)
                if hat[0] == -1:   # Left
                    dx = -1
                elif hat[0] == 1:  # Right
                    dx = 1
                if hat[1] == 1:    # Up
                    dy = -1
                elif hat[1] == -1: # Down
                    dy = 1

                # Left Analog Stick (Axes 0,1)
                axis_x = self.joystick.get_axis(0)
                axis_y = self.joystick.get_axis(1)
                if abs(axis_x) > 0.3:
                    dx = axis_x
                if abs(axis_y) > 0.3:
                    dy = axis_y
            except:
                pass  # Joystick not fully supported, fall back to keyboard

        # Move player
        self.player.move(dx, dy, self.current_scene.walls)

        # Check for nearby interactables
        nearby_npcs = self.current_scene.get_nearby_npcs(self.player.rect)
        self.player.nearby_npc = nearby_npcs[0] if nearby_npcs else None

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RETURN:
                    self.inventory_open = not self.inventory_open
                elif event.key == pygame.K_SPACE:
                    # Interact
                    if self.dialog.visible:
                        # Advance dialog
                        if self.dialog.displayed_chars >= len(self.dialog.text):
                            self.dialog.visible = False
                    else:
                        # Start interaction
                        if self.player.nearby_npc:
                            npc = self.player.nearby_npc
                            line = npc.interact()
                            self.dialog.show(line)

            elif event.type == pygame.JOYBUTTONDOWN:
                # RG35xx button mapping!
                if event.button == BUTTON_A:  # Interact
                    if self.dialog.visible:
                        if self.dialog.displayed_chars >= len(self.dialog.text):
                            self.dialog.visible = False
                    else:
                        if self.player.nearby_npc:
                            npc = self.player.nearby_npc
                            line = npc.interact()
                            self.dialog.show(line)

                elif event.button == BUTTON_B:  # Cancel/Back
                    if self.dialog.visible:
                        self.dialog.visible = False
                    elif self.inventory_open:
                        self.inventory_open = False

                elif event.button == BUTTON_X:  # Inventory
                    self.inventory_open = not self.inventory_open

                elif event.button == BUTTON_Y:  # Stats
                    # Show stats screen (TODO)
                    pass

                elif event.button == BUTTON_START:  # Pause/Save
                    self.save_game()
                    self.dialog.show("Game saved! 🐱")

                elif event.button == BUTTON_SELECT:  # Debug
                    print(f"Position: {self.player.rect}")
                    print(f"Time: {self.state.game_time//60:02d}:{self.state.game_time%60:02d}")

    def update(self, dt):
        if not self.dialog.visible and not self.inventory_open:
            # Update player animation
            self.player.animation_timer += dt
            if self.player.moving:
                self.player.animation_timer %= 500

        # Update dialog
        self.dialog.update()

        # Update time
        if not self.dialog.visible and not self.inventory_open:
            self.state.game_time += dt // 1000  # dt in ms -> seconds
            if self.state.game_time >= 1440:  # New day!
                self.state.game_time = 0
                self.state.day += 1

        # Update scene
        self.current_scene.update(dt)

    def draw(self):
        # Draw current scene
        self.current_scene.draw(self.screen, self.player)

        # Draw UI overlays
        if self.inventory_open:
            self.draw_inventory()

        self.dialog.draw(self.screen)

        # Draw time indicator
        font = pygame.font.Font(None, 20)
        time_str = f"Day {self.state.day} - {self.state.game_time//60:02d}:{self.state.game_time%60:02d}"
        time_surf = font.render(time_str, True, COLORS['WHITE'])
        self.screen.blit(time_surf, (10, 10))

        pygame.display.flip()

    def draw_inventory(self):
        # Inventory overlay
        inv_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, 200, 200)
        pygame.draw.rect(self.screen, COLORS['CREAM'], inv_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['PINK'], inv_rect, 3, border_radius=10)

        font = pygame.font.Font(None, 24)
        title = font.render("Inventory", True, COLORS['PINK'])
        self.screen.blit(title, (inv_rect.x + 10, inv_rect.y + 10))

        y_off = 40
        for item, count in self.state.inventory.items():
            item_text = f"{item.title()}: {count}"
            item_surf = font.render(item_text, True, COLORS['BLACK'])
            self.screen.blit(item_surf, (inv_rect.x + 20, inv_rect.y + y_off))
            y_off += 25

    def run(self):
        print("🎮 Starting Joy Time")
        print("           .--''--.")
        print("      _'         '_")
        print("     '   _     _   '")
        print("     |  (o)   (o)  |")
        print("      \\   _     _  /")
        print("       '  (__) (__) '")
        print()
        print("       Mochi")
        print("       .-\"\"\"-\"\"\"-.")
        print("      (_|       |_)")
        print("        \"       \"")
        print("      -=×=-")
        print("    🏡 Mochi Haven 🏡")

        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_input()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

# ========================================
# ENTRY POINT
# ========================================
if __name__ == "__main__":
    game = MochiHavenGame()
    game.run()
