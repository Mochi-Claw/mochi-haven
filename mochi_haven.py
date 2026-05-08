# Mochi Haven - A Cozy Life Sim RPG
# Built for RG35xx-h (640x480) with Pygame
# Player: Mochi~♡ running her own catgirl paradise!

import pygame
import sys
import os
import json
import random
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
# GAME STATE (extended)
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
            'VIT': 10,   # Max Health/Energy
            'INT': 5,    # Crafting quality
            'STR': 5,    # Gathering speed
            'CHA': 5,    # Friendship boosts
        }
        # Current health (starts at max VIT)
        self.health = self.stats['VIT']

        # Inventory
        self.inventory = {
            'catnip': 10,
            'yarn': 5,
            'strawberries': 3,
            'coffee': 2,
            'fish': 0,
            'wood': 0,
            'ore': 0,
            'string': 0,
            'water': 0,
            'catnip_tea': 0,
            'yarn_ball': 0,
            'fishing_rod': 0,
            'amulet': 0,
        }

        # Time
        self.game_time = 8 * 60  # 8:00 AM (in minutes)
        self.day = 1

        # Flags
        self.talking_to_npc = None
        self.menu_open = False

        # Quest Log (Phase 2)
        self.quests = []
        self.active_quest_indices = []  # indices into self.quests
        self.completed_quests = []

        # Active temporary buffs (list of (stat, value, expiry_ms))
        self.active_buffs = []

        # Crafting & Gathering state
        self.gathering = False
        self.gather_progress = 0
        self.gather_target = None  # ResourceNode object
        self.gather_duration = 2000  # ms
        self.crafting_menu_open = False
        self.selected_recipe = 0

        # UI overlays
        self.stats_overlay_open = False
        self.quest_log_open = False

        # Initialize starting quests
        self.initialize_quests()

    def initialize_quests(self):
        # Starting quests: Gather 5 Wood, Catch 3 Fish, Talk to Tiri
        self.quests = [
            {
                'id': 'gather_wood_5',
                'title': 'Gather 5 Wood',
                'description': 'Collect 5 pieces of wood from the forest.',
                'objective_type': 'gather',
                'target_item': 'wood',
                'target_count': 5,
                'current_count': 0,
                'reward_xp': 50,
                'reward_item': None,
                'active': True,
            },
            {
                'id': 'catch_fish_3',
                'title': 'Catch 3 Fish',
                'description': 'Catch 3 fish from the garden pond or forest river.',
                'objective_type': 'gather',
                'target_item': 'fish',
                'target_count': 3,
                'current_count': 0,
                'reward_xp': 75,
                'reward_item': None,
                'active': True,
            },
            {
                'id': 'talk_tiri',
                'title': 'Talk to Tiri',
                'description': 'Have a conversation with Tiri.',
                'objective_type': 'talk',
                'target_npc': 'Tiri',
                'target_count': 1,
                'current_count': 0,
                'reward_xp': 25,
                'reward_item': None,
                'active': True,
            },
        ]
        self.active_quest_indices = [0, 1, 2]

    def calculate_xp_to_next(self):
        level = self.stats['LEVEL']
        return int(100 * (level ** 1.5))

    def gain_xp(self, amount):
        """Add XP and process any level-ups. Returns number of levels gained."""
        self.stats['XP'] += amount
        levels = 0
        while self.stats['XP'] >= self.stats['XP_TO_NEXT']:
            # Level up once
            increased_stat = self.level_up()
            levels += 1
        return levels

    def level_up(self):
        """Perform a single level up, auto-assign to smallest stat. Returns the stat increased."""
        self.stats['LEVEL'] += 1
        self.stats['XP'] -= self.stats['XP_TO_NEXT']
        self.stats['XP_TO_NEXT'] = self.calculate_xp_to_next()
        # Auto-assign smallest stat
        min_stat = min(['VIT', 'INT', 'STR', 'CHA'], key=lambda s: self.stats[s])
        self.stats[min_stat] += 1
        return min_stat

    def dialog_show(self, text):
        # No-op; dialogs handled by main game
        pass

    def update_quest_progress(self, objective_type, target, amount=1):
        for i, quest_idx in enumerate(self.active_quest_indices[:]):
            quest = self.quests[quest_idx]
            if quest['objective_type'] == objective_type:
                if objective_type == 'gather' and quest.get('target_item') == target:
                    quest['current_count'] += amount
                elif objective_type == 'talk' and quest.get('target_npc') == target:
                    quest['current_count'] += amount
                # Check completion
                if quest['current_count'] >= quest['target_count']:
                    self.complete_quest(quest_idx)

    def complete_quest(self, quest_idx):
        quest = self.quests[quest_idx]
        # Grant rewards
        self.gain_xp(quest['reward_xp'])
        if quest['reward_item']:
            self.inventory[quest['reward_item']] = self.inventory.get(quest['reward_item'], 0) + 1
        # Remove from active
        if quest_idx in self.active_quest_indices:
            self.active_quest_indices.remove(quest_idx)
        self.completed_quests.append(quest)
        # Add a new random quest
        self.add_random_quest()
        self.dialog_show(f"Quest Complete! {quest['title']} — +{quest['reward_xp']} XP!")

    def update_quest_progress(self, objective_type, target, amount=1):
        newly_completed = []
        for i, quest_idx in enumerate(self.active_quest_indices[:]):
            quest = self.quests[quest_idx]
            if quest['objective_type'] == objective_type:
                if objective_type == 'gather' and quest.get('target_item') == target:
                    quest['current_count'] += amount
                elif objective_type == 'talk' and quest.get('target_npc') == target:
                    quest['current_count'] += amount
                # Check completion
                if quest['current_count'] >= quest['target_count']:
                    newly_completed.append(quest_idx)
        return newly_completed

    def complete_quest(self, quest_idx):
        quest = self.quests[quest_idx]
        levels = self.gain_xp(quest['reward_xp'])
        rewards = {
            'xp': quest['reward_xp'],
            'levels': levels,
            'item': quest['reward_item'],
        }
        # Grant item
        if quest['reward_item']:
            self.inventory[quest['reward_item']] = self.inventory.get(quest['reward_item'], 0) + 1
        # Remove from active
        if quest_idx in self.active_quest_indices:
            self.active_quest_indices.remove(quest_idx)
        self.completed_quests.append(quest)
        # Add a new random quest
        self.add_random_quest()
        return rewards

    def add_random_quest(self):
        # Simple pool of possible quests
        pool = [
            {
                'id': 'gather_strawberries_5',
                'title': 'Gather 5 Strawberries',
                'description': 'Collect 5 strawberries from the garden.',
                'objective_type': 'gather',
                'target_item': 'strawberries',
                'target_count': 5,
                'current_count': 0,
                'reward_xp': 40,
                'reward_item': None,
            },
            {
                'id': 'gather_catnip_10',
                'title': 'Gather 10 Catnip',
                'description': 'Harvest 10 catnip from the garden.',
                'objective_type': 'gather',
                'target_item': 'catnip',
                'target_count': 10,
                'current_count': 0,
                'reward_xp': 30,
                'reward_item': None,
            },
            {
                'id': 'talk_watson',
                'title': 'Talk to Watson',
                'description': 'Chat with Watson in the house.',
                'objective_type': 'talk',
                'target_npc': 'Watson',
                'target_count': 1,
                'current_count': 0,
                'reward_xp': 25,
                'reward_item': None,
            },
        ]
        new_quest = random.choice(pool)
        new_quest['active'] = True
        new_quest_idx = len(self.quests)
        self.quests.append(new_quest)
        self.active_quest_indices.append(new_quest_idx)

    def get_save_dict(self):
        return {
            'stats': self.stats,
            'health': self.health,
            'inventory': self.inventory,
            'game_time': self.game_time,
            'day': self.day,
            'quests': self.quests,
            'active_quest_indices': self.active_quest_indices,
            'completed_quests': self.completed_quests,
        }

    def load_from_dict(self, data):
        self.stats = data.get('stats', self.stats)
        self.health = data.get('health', self.stats['VIT'])
        self.inventory = data.get('inventory', self.inventory)
        self.game_time = data.get('game_time', self.game_time)
        self.day = data.get('day', self.day)
        self.quests = data.get('quests', self.quests)
        self.active_quest_indices = data.get('active_quest_indices', self.active_quest_indices)
        self.completed_quests = data.get('completed_quests', self.completed_quests)
        # Ensure XP_TO_NEXT is recalculated on load
        self.stats['XP_TO_NEXT'] = self.calculate_xp_to_next()

# ========================================
# PLAYENT (the character!)
# ========================================
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.speed = 3
        self.moving = False
        self.direction = 'down'  # up, down, left, right
        self.animation_timer = 0
        self.nearby_npc = None
        self.nearby_object = None

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
        pygame.draw.circle(self.sprite, COLORS['BLACK'], (20, 9), 2)

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
# INTERACTABLE OBJECTS (beds, chests, etc.)
# ========================================
class Interactable:
    def __init__(self, x, y, width, height, color, action="Interact", interact_msg="You interacted with something!"):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.action = action
        self.interact_msg = interact_msg

    def draw(self, surface):
        # Draw a simple colored rectangle with border
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLORS['WHITE'], self.rect, 2, border_radius=8)

    def interact(self):
        return self.interact_msg

# ========================================
# RESOURCE NODES (for gathering)
# ========================================
class ResourceNode:
    def __init__(self, x, y, resource_type, yield_amount=1, respawn_time=60000):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.resource_type = resource_type
        self.yield_amount = yield_amount
        self.respawn_time = respawn_time  # ms
        self.depleted = False
        self.deplete_timer = 0
        self.visible = True

        # Color based on resource type
        colors = {
            'catnip': COLORS['MINT'],
            'yarn': COLORS['PINK'],
            'strawberries': COLORS['PEACH'],
            'wood': COLORS['BROWN'],
            'ore': (169, 169, 169),  # Dark gray
            'fish': (100, 150, 255),
            'water': COLORS['SKY'],
        }
        self.color = colors.get(resource_type, COLORS['WHITE'])

    def start_gathering(self):
        if not self.depleted:
            self.depleted = True
            self.deplete_timer = pygame.time.get_ticks()
            return True
        return False

    def update(self):
        if self.depleted:
            if pygame.time.get_ticks() - self.deplete_timer >= self.respawn_time:
                self.depleted = False

    def draw(self, surface):
        if not self.visible:
            return
        # Draw as a small plant/rock/etc.
        if self.depleted:
            color = (self.color[0]//2, self.color[1]//2, self.color[2]//2)
        else:
            color = self.color
        pygame.draw.circle(surface, color, self.rect.center, 12)
        pygame.draw.circle(surface, COLORS['WHITE'], self.rect.center, 12, 2)
        # Label (small)
        font = pygame.font.Font(None, 14)
        label = font.render(self.resource_type[:3].upper(), True, COLORS['WHITE'])
        surface.blit(label, (self.rect.x+4, self.rect.y-10))

# ========================================
# CRAFTING SYSTEM
# ========================================
CRAFTING_RECIPES = [
    {
        'name': 'Catnip Tea',
        'output': 'catnip_tea',
        'count': 1,
        'ingredients': {'catnip': 2, 'water': 1},
        'description': 'Restores 20 VIT energy.',
        'effect': {'heal': 20},
    },
    {
        'name': 'Yarn Ball',
        'output': 'yarn_ball',
        'count': 1,
        'ingredients': {'yarn': 3},
        'description': '+2 CHA temporary for 5 minutes.',
        'effect': {'buff': ('CHA', 2, 300_000)},  # 5 min in ms
    },
    {
        'name': 'Fishing Rod',
        'output': 'fishing_rod',
        'count': 1,
        'ingredients': {'wood': 2, 'string': 1},
        'description': 'Unlocks fishing minigame.',
        'effect': {'unlock': 'fishing'},
    },
    {
        'name': 'Amulet',
        'output': 'amulet',
        'count': 1,
        'ingredients': {'ore': 1, 'yarn': 1, 'strawberries': 1},
        'description': '+1 INT permanently.',
        'effect': {'permanent_stat': ('INT', 1)},
    },
]

# ========================================
# SCENE MANAGER (extended)
# ========================================
class Scene:
    def __init__(self, name, bg_color, objects=None):
        self.name = name
        self.bg_color = bg_color
        self.objects = objects or []
        self.npcs = []
        self.walls = []
        self.resource_nodes = []  # Phase 2: gathering nodes

    def update(self, dt):
        # Update resource nodes (respawn)
        for node in self.resource_nodes:
            node.update()

    def draw(self, surface, player):
        surface.fill(self.bg_color)
        # Draw objects
        for obj in self.objects:
            obj.draw(surface)
        # Draw resource nodes
        for node in self.resource_nodes:
            node.draw(surface)
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

    def get_nearby_objects(self, player_rect):
        nearby = []
        for obj in self.objects:
            if player_rect.colliderect(obj.rect):
                nearby.append(obj)
        return nearby

    def get_nearby_resource_nodes(self, player_rect):
        nearby = []
        for node in self.resource_nodes:
            if player_rect.colliderect(node.rect.inflate(20, 20)):  # Slightly larger hitbox
                nearby.append(node)
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

        # Transient state
        self.pending_messages = []
        self.last_hat = (0, 0)
        # Note: gathering state lives in self.state (gathering, gather_progress, gather_target, gather_duration, crafting_menu_open, selected_recipe, stats_overlay_open, quest_log_open)
        # These are reset on load (fine)


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
        bed = Interactable(300, 300, 60, 40, COLORS['PEACH'], "Sleep", "You slept peacefully! 💤")
        self.scenes['home'].objects.append(bed)
        # Store reference for bed interaction
        self.bed = bed

    def load_game(self):
        # Use platform-appropriate save directory
        if sys.platform == 'win32':
            save_dir = os.path.join(os.path.expanduser('~'), '.mochi_haven')
        else:
            save_dir = '/root/.openclaw/workspace'  # Linux default
        
        save_path = os.path.join(save_dir, 'savegame.json')
        
        if os.path.exists(save_path):
            try:
                with open(save_path, 'r') as f:
                    data = json.load(f)
                self.state.load_from_dict(data)
            except Exception as e:
                print(f"Save file corrupted, starting fresh: {e}")

    def save_game(self):
        # Use platform-appropriate save directory
        if sys.platform == 'win32':
            save_dir = os.path.join(os.path.expanduser('~'), '.mochi_haven')
        else:
            save_dir = '/root/.openclaw/workspace'
        
        # Ensure directory exists
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, 'savegame.json')
        
        data = self.state.get_save_dict()
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Game saved to {save_path}")

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        # Keyboard movement (PC testing)
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1

        # RG35xx D-Pad (Hat) + Analog sticks
        current_hat = (0, 0)
        if self.joystick:
            try:
                hat = self.joystick.get_hat(0)
                current_hat = hat
                if hat[0] == -1:
                    dx = -1
                elif hat[0] == 1:
                    dx = 1
                if hat[1] == 1:
                    dy = -1
                elif hat[1] == -1:
                    dy = 1
                axis_x = self.joystick.get_axis(0)
                axis_y = self.joystick.get_axis(1)
                if abs(axis_x) > 0.3:
                    dx = axis_x
                if abs(axis_y) > 0.3:
                    dy = axis_y
            except:
                pass

        # ========================================
        # Event handling
        # ========================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RETURN:
                    if self.state.crafting_menu_open:
                        # Craft selected recipe
                        recipe = CRAFTING_RECIPES[self.state.selected_recipe]
                        can_craft = all(self.state.inventory.get(ing, 0) >= qty for ing, qty in recipe['ingredients'].items())
                        if can_craft:
                            for ing, qty in recipe['ingredients'].items():
                                self.state.inventory[ing] -= qty
                            self.state.inventory[recipe['output']] = self.state.inventory.get(recipe['output'], 0) + recipe['count']
                            effect = recipe.get('effect', {})
                            if 'heal' in effect:
                                heal = effect['heal']
                                self.state.health = min(self.state.stats['VIT'], self.state.health + heal)
                                self.dialog.show(f"{recipe['name']} crafted! Restored {heal} VIT.")
                            elif 'buff' in effect:
                                stat, val, duration = effect['buff']
                                self.state.stats[stat] += val
                                expiry = pygame.time.get_ticks() + duration
                                self.state.active_buffs.append((stat, val, expiry))
                                self.dialog.show(f"{recipe['name']} crafted! +{val} {stat} for {duration/60000:.0f} min.")
                            elif 'unlock' in effect:
                                self.dialog.show(f"{recipe['name']} crafted! {effect['unlock'].title()} unlocked!")
                            elif 'permanent_stat' in effect:
                                stat, val = effect['permanent_stat']
                                self.state.stats[stat] += val
                                self.dialog.show(f"{recipe['name']} crafted! Permanently +{val} {stat}!")
                            else:
                                self.dialog.show(f"Crafted {recipe['name']}!")
                        else:
                            self.dialog.show("Not enough materials for that recipe.")
                    else:
                        self.inventory_open = not self.inventory_open
                elif event.key == pygame.K_x:
                    if not (self.state.crafting_menu_open or self.state.quest_log_open or self.state.stats_overlay_open):
                        nearby_nodes = self.current_scene.get_nearby_resource_nodes(self.player.rect)
                        if nearby_nodes:
                            node = nearby_nodes[0]
                            if not self.state.gathering:
                                if node.start_gathering():
                                    self.state.gathering = True
                                    self.state.gather_target = node
                                    self.state.gather_progress = 0
                        else:
                            self.inventory_open = not self.inventory_open
                elif event.key == pygame.K_y:
                    if not self.dialog.visible:
                        self.state.crafting_menu_open = not self.state.crafting_menu_open
                        if self.state.crafting_menu_open:
                            self.state.quest_log_open = False
                            self.state.stats_overlay_open = False
                            self.inventory_open = False
                            self.state.selected_recipe = 0
                elif event.key == pygame.K_UP and self.state.crafting_menu_open:
                    self.state.selected_recipe = (self.state.selected_recipe - 1) % len(CRAFTING_RECIPES)
                elif event.key == pygame.K_DOWN and self.state.crafting_menu_open:
                    self.state.selected_recipe = (self.state.selected_recipe + 1) % len(CRAFTING_RECIPES)
                elif event.key == pygame.K_SPACE:
                    if self.dialog.visible:
                        if self.dialog.displayed_chars >= len(self.dialog.text):
                            if self.pending_messages:
                                self.dialog.show(self.pending_messages.pop(0))
                            else:
                                self.dialog.visible = False
                    else:
                        if self.player.nearby_npc:
                            npc = self.player.nearby_npc
                            line = npc.interact()
                            completed = self.state.update_quest_progress('talk', npc.name, 1)
                            for idx in completed:
                                quest = self.state.quests[idx]
                                rewards = self.state.complete_quest(idx)
                                msg = f"Quest Complete: {quest['title']}! +{rewards['xp']} XP"
                                if rewards.get('levels', 0) > 0:
                                    msg += f" (Now Level {self.state.stats['LEVEL']})"
                                if rewards.get('item'):
                                    msg += f" + {rewards['item']}"
                                self.pending_messages.append(msg)
                            self.dialog.show(line)
                        elif self.player.nearby_object:
                            obj = self.player.nearby_object
                            line = obj.interact()
                            self.dialog.show(line)
                            if obj.action == "Sleep":
                                self.save_game()
                                self.dialog.show("Game saved! Sweet dreams... 💤")

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == BUTTON_A:
                    if self.dialog.visible:
                        if self.dialog.displayed_chars >= len(self.dialog.text):
                            if self.pending_messages:
                                self.dialog.show(self.pending_messages.pop(0))
                            else:
                                self.dialog.visible = False
                    elif self.state.crafting_menu_open:
                        # Craft selected recipe
                        recipe = CRAFTING_RECIPES[self.state.selected_recipe]
                        can_craft = all(self.state.inventory.get(ing, 0) >= qty for ing, qty in recipe['ingredients'].items())
                        if can_craft:
                            for ing, qty in recipe['ingredients'].items():
                                self.state.inventory[ing] -= qty
                            self.state.inventory[recipe['output']] = self.state.inventory.get(recipe['output'], 0) + recipe['count']
                            effect = recipe.get('effect', {})
                            if 'heal' in effect:
                                heal = effect['heal']
                                self.state.health = min(self.state.stats['VIT'], self.state.health + heal)
                                self.dialog.show(f"{recipe['name']} crafted! Restored {heal} VIT.")
                            elif 'buff' in effect:
                                stat, val, duration = effect['buff']
                                self.state.stats[stat] += val
                                expiry = pygame.time.get_ticks() + duration
                                self.state.active_buffs.append((stat, val, expiry))
                                self.dialog.show(f"{recipe['name']} crafted! +{val} {stat} for {duration/60000:.0f} min.")
                            elif 'unlock' in effect:
                                self.dialog.show(f"{recipe['name']} crafted! {effect['unlock'].title()} unlocked!")
                            elif 'permanent_stat' in effect:
                                stat, val = effect['permanent_stat']
                                self.state.stats[stat] += val
                                self.dialog.show(f"{recipe['name']} crafted! Permanently +{val} {stat}!")
                            else:
                                self.dialog.show(f"Crafted {recipe['name']}!")
                        else:
                            self.dialog.show("Not enough materials for that recipe.")
                    else:
                        # Normal interaction with NPC/object
                        if self.player.nearby_npc:
                            npc = self.player.nearby_npc
                            line = npc.interact()
                            completed = self.state.update_quest_progress('talk', npc.name, 1)
                            for idx in completed:
                                quest = self.state.quests[idx]
                                rewards = self.state.complete_quest(idx)
                                msg = f"Quest Complete: {quest['title']}! +{rewards['xp']} XP"
                                if rewards.get('levels', 0) > 0:
                                    msg += f" (Now Level {self.state.stats['LEVEL']})"
                                if rewards.get('item'):
                                    msg += f" + {rewards['item']}"
                                self.pending_messages.append(msg)
                            self.dialog.show(line)
                        elif self.player.nearby_object:
                            obj = self.player.nearby_object
                            line = obj.interact()
                            self.dialog.show(line)
                            if obj.action == "Sleep":
                                self.save_game()
                                self.dialog.show("Game saved! Sweet dreams... 💤")

                elif event.button == BUTTON_B:
                    if self.dialog.visible:
                        self.dialog.visible = False
                    elif self.inventory_open:
                        self.inventory_open = False
                    elif self.state.crafting_menu_open:
                        self.state.crafting_menu_open = False
                    elif self.state.quest_log_open:
                        self.state.quest_log_open = False
                    elif self.state.stats_overlay_open:
                        self.state.stats_overlay_open = False

                elif event.button == BUTTON_X:
                    if self.dialog.visible:
                        pass
                    else:
                        if self.state.crafting_menu_open or self.state.quest_log_open or self.state.stats_overlay_open:
                            pass
                        else:
                            nearby_nodes = self.current_scene.get_nearby_resource_nodes(self.player.rect)
                            if nearby_nodes:
                                node = nearby_nodes[0]
                                if not self.state.gathering:
                                    if node.start_gathering():
                                        self.state.gathering = True
                                        self.state.gather_target = node
                                        self.state.gather_progress = 0
                            else:
                                self.inventory_open = not self.inventory_open

                elif event.button == BUTTON_Y:
                    if not self.dialog.visible:
                        self.state.crafting_menu_open = not self.state.crafting_menu_open
                        if self.state.crafting_menu_open:
                            self.state.quest_log_open = False
                            self.state.stats_overlay_open = False
                            self.inventory_open = False
                            self.state.selected_recipe = 0

                elif event.button == BUTTON_L1:
                    if not self.dialog.visible:
                        self.state.quest_log_open = not self.state.quest_log_open
                        if self.state.quest_log_open:
                            self.state.crafting_menu_open = False
                            self.state.stats_overlay_open = False
                            self.inventory_open = False

                elif event.button == BUTTON_SELECT:
                    if not self.dialog.visible:
                        self.state.stats_overlay_open = not self.state.stats_overlay_open
                        if self.state.stats_overlay_open:
                            self.state.crafting_menu_open = False
                            self.state.quest_log_open = False
                            self.inventory_open = False

                elif event.button == BUTTON_START:
                    self.save_game()
                    self.dialog.show("Game saved! 🐱")

        # ========================================
        # Menu navigation (crafting via hat)
        # ========================================
        if self.state.crafting_menu_open:
            if current_hat[1] == 1 and self.last_hat[1] != 1:
                self.state.selected_recipe = (self.state.selected_recipe - 1) % len(CRAFTING_RECIPES)
            if current_hat[1] == -1 and self.last_hat[1] != -1:
                self.state.selected_recipe = (self.state.selected_recipe + 1) % len(CRAFTING_RECIPES)
            self.last_hat = current_hat
            return

        # Skip normal gameplay if any overlay open (inventory, quest, stats)
        if self.inventory_open or self.state.quest_log_open or self.state.stats_overlay_open:
            self.last_hat = current_hat
            return

        # ========================================
        # Normal gameplay: move player
        # ========================================
        self.player.move(dx, dy, self.current_scene.walls)

        # Update nearby interactables
        nearby_npcs = self.current_scene.get_nearby_npcs(self.player.rect)
        nearby_objects = self.current_scene.get_nearby_objects(self.player.rect)
        nearby_nodes = self.current_scene.get_nearby_resource_nodes(self.player.rect)

        if nearby_npcs:
            self.player.nearby_npc = nearby_npcs[0]
        else:
            self.player.nearby_npc = None
        if nearby_objects:
            self.player.nearby_object = nearby_objects[0]
        else:
            self.player.nearby_object = None

        self.last_hat = current_hat


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
