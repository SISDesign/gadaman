"""
PIXEL QUEST: ASCII-TO-PYGAME ENGINE
Educational Platformer Framework — 3-Act Campaign
"""

import os
import sys
import pygame
from PIL import Image, ImageSequence

# Suppress ALSA warnings in headless/cloud environments
os.environ["SDL_AUDIODRIVER"] = "dummy"

# ==============================================================================
# SECTION 1: STUDENT CUSTOMIZATION ZONE (STORY & ASCII LEVEL DESIGN)
# ==============================================================================

STUDENT_ACTS = [
    # --------------------------------------------------------------------------
    # ACT I: COASTAL LANDFALL (Sphacteria Island, 425 BCE)
    # --------------------------------------------------------------------------
    {
        "act_num": 1,
        "title": "Act I: Coastal Landfall",
        "intro": [
            "Midnight along the rocky shoreline of Sphacteria.",
            "You are Kassandra, an Athenian runner dispatched by General Demosthenes.",
            "Spartan sentries (*) patrol the coastline with bronze shields and spears.",
            "MISSION: Sneak through brush (~) or strike sentries (press F to attack),",
            "secure the Shore Defense Map ($), and reach the gateway pass (E)!"
        ],
        "outro": [
            "SHORE DEFENSES SECURED!",
            "You retrieved the Spartan tactical map without raising an alarm.",
            "Ascend the steep mountain paths toward the fortress redoubt..."
        ],
        "map": """
#####################################################################################
#                                                                                  E#
#====                                              =======                      ====#
#                 $                                          *                      #
#              =======                                    =======                   #
#                                  *                                                #
#                                =====                                              #
#      ~~~         xxxxx                      ~~~          xxxxxxx                  #
#@   =======       =====                    =======        =======                  #
#####################################################################################
"""
    },

    # --------------------------------------------------------------------------
    # ACT II: THE TEMPLE REDOUBT (Mountain Stronghold)
    # --------------------------------------------------------------------------
    {
        "act_num": 2,
        "title": "Act II: Temple Redoubt",
        "intro": [
            "The Mountain Acropolis — A fortified Spartan bastion.",
            "Hoplite sentries maintain strict patrol vigilance across the ruined temple.",
            "MISSION: Scale the colonnades, strike or bypass sentries, recover the",
            "Spartan Scytale rod ($), and descend to the harbor (E)!"
        ],
        "outro": [
            "SCYTALE SECURED!",
            "You slipped past the guard line and secured the encoded wooden rod.",
            "Hurry to the harbor docks before the Spartan fleet cuts off your escape!"
        ],
        "map": """
###############################################################################################
#                                                                                            E#
#                                                                                         ====#
#        *                             *                            $                         #
#     =======                       =======                       =====                       #
#                ===                                *                                         #
#                                                 =====                                       #
#                        *                                                                    #
#                      =====                                          *                       #
#@   ~~~     xxxxxxxx           ~~~          xxxxxxxxxx             =====              ~~~    #
###############################################################################################
"""
    },

    # --------------------------------------------------------------------------
    # ACT III: THE HARBOR EXTRACTION (Bay of Pylos)
    # --------------------------------------------------------------------------
    {
        "act_num": 3,
        "title": "Act III: Harbor Extraction",
        "intro": [
            "Bay of Pylos — Dawn approaches over the Aegean Sea.",
            "The Spartan garrison is on high alert searching for the infiltrator.",
            "MISSION: Navigate the seawall, ignite the Signal Torch ($),",
            "and board the waiting Athenian trireme flagship (E)!"
        ],
        "outro": [
            "CAMPAIGN COMPLETE! ATHENS PREVAILS!",
            "You boarded the trireme under covering archer fire with the cipher intact.",
            "HISTORICAL RECORD: The Athenian triumph at Sphacteria in 425 BCE shocked the",
            "Greek world, proving intelligence and stealth could outmaneuver brute force."
        ],
        "map": """
##############################################################################################################
#                                                                                                           E#
#===                                                                                                      ===#
#             *                     *                         $                      *                       #
#           ======                ======                    =====                  ======                    #
#                                                                                                            #
#      *                   *                      *                      *                                   #
#    =====               =====                  =====                  =====                                 #
#                                                                                                            #
#@   ~~~     xxxxxxxxx    ~~~     xxxxxxxxxxx    ~~~     xxxxxxxxxxx    ~~~     xxxxxxxxxxxxxxxxx     ~~~    #
##############################################################################################################
"""
    }
]

# ==============================================================================
# SECTION 2: ENGINE & DISPLAY CONSTANTS
# ==============================================================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
TILE_SIZE = 32
FPS = 60
MAX_LIVES = 5

COLOR_PLATFORM = (95, 85, 75)
COLOR_HAZARD = (180, 50, 40)
COLOR_BUSH = (65, 115, 60)
COLOR_HERO = (240, 215, 140)
COLOR_SCOUT = (195, 45, 45)
COLOR_RELIC = (235, 185, 55)
COLOR_PORTAL = (40, 160, 220)
COLOR_TEXT = (245, 240, 230)
COLOR_HEART = (220, 40, 50)
COLOR_HEART_EMPTY = (70, 70, 75)


# ==============================================================================
# SECTION 3: GIF LOADER & BOTTOM-BASELINE ANCHORING
# ==============================================================================
class AnimatedGif:
    def __init__(self, filepath, target_size, frame_delay=6, align_to_bottom=False):
        self.frames = []
        self.current_frame = 0
        self.counter = 0
        self.frame_delay = frame_delay
        tw, th = target_size

        if os.path.exists(filepath):
            try:
                pil_img = Image.open(filepath)
                for frame in ImageSequence.Iterator(pil_img):
                    rgba = frame.convert("RGBA")
                    
                    if align_to_bottom:
                        bbox = rgba.getbbox()
                        if bbox:
                            # 1. Scale the full original canvas to (tw, th) first so proportions stay 1:1
                            scaled_full = rgba.resize((tw, th), Image.Resampling.NEAREST)
                            
                            # 2. Find where the colored pixels land in the scaled version
                            scaled_bbox = scaled_full.getbbox()
                            if scaled_bbox:
                                cropped = scaled_full.crop(scaled_bbox)
                                cw, ch = cropped.size
                                
                                # 3. Place on canvas flush against the floor without changing width
                                canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
                                offset_x = (tw - cw) // 2
                                offset_y = th - ch  # Push directly to bottom
                                canvas.paste(cropped, (offset_x, offset_y), cropped)
                                rgba = canvas
                            else:
                                rgba = scaled_full
                        else:
                            rgba = rgba.resize((tw, th), Image.Resampling.NEAREST)
                    else:
                        rgba = rgba.resize((tw, th), Image.Resampling.NEAREST)

                    raw_data = rgba.tobytes()
                    surface = pygame.image.frombytes(raw_data, (tw, th), "RGBA")
                    self.frames.append(surface)
            except Exception as e:
                print(f"Notice loading {filepath}: {e}")

    def get_frame(self, flip_x=False):
        if not self.frames:
            return None
        self.counter += 1
        if self.counter >= self.frame_delay:
            self.counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        frame = self.frames[self.current_frame]
        return pygame.transform.flip(frame, flip_x, False) if flip_x else frame


# ==============================================================================
# SECTION 4: ROBUST PLAYER PHYSICS (NO JITTER & RESPONSIVE JUMPING)
# ==============================================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        base = "assets/hero.gif"
        attack_file = "assets/heroattack.gif" if os.path.exists("assets/heroattack.gif") else "assets/attack.gif"
        if not os.path.exists(attack_file):
            attack_file = base

        # align_to_bottom=True ensures every single frame sits on the ground
        self.anims = {
            "idle": AnimatedGif(base, (24, 32), frame_delay=8, align_to_bottom=True),
            "walk": AnimatedGif("assets/herowalking.gif" if os.path.exists("assets/herowalking.gif") else "assets/walk.gif" if os.path.exists("assets/walk.gif") else base, (24, 32), frame_delay=5, align_to_bottom=True),
            "jump": AnimatedGif("assets/herojumping.gif" if os.path.exists("assets/herojumping.gif") else "assets/jump.gif" if os.path.exists("assets/jump.gif") else base, (24, 32), frame_delay=6, align_to_bottom=True),
            "crouch": AnimatedGif("assets/herocrouch.gif" if os.path.exists("assets/herocrouch.gif") else base, (24, 32), frame_delay=9999, align_to_bottom=True),
            "attack": AnimatedGif(attack_file, (32, 32), frame_delay=4, align_to_bottom=True),
        }
        self.rect = pygame.Rect(x, y, 24, 32)
        self.x_pos = float(x)
        self.y_pos = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 4.0
        self.crouch_speed = 2.0
        self.jump_force = -11.0
        self.gravity = 0.55
        self.max_fall_speed = 12.0
        
        # Jump buffer & coyote time to ensure jumps always register in noVNC
        self.coyote_timer = 0
        self.jump_buffer = 0
        
        self.is_hidden = False
        self.facing = 1
        self.has_relic = False
        self.state = "idle"

        self.invulnerable_timer = 0
        self.attack_timer = 0
        self.attack_cooldown = 0

    def trigger_damage(self):
        self.invulnerable_timer = 60

    def trigger_attack(self):
        if self.attack_cooldown <= 0:
            self.attack_timer = 18
            self.attack_cooldown = 24
            if "attack" in self.anims and self.anims["attack"].frames:
                self.anims["attack"].current_frame = 0

    def get_attack_hitbox(self):
        if self.attack_timer > 0:
            if self.facing == 1:
                return pygame.Rect(self.rect.right, self.rect.y + 4, 22, 24)
            else:
                return pygame.Rect(self.rect.left - 22, self.rect.y + 4, 22, 24)
        return None

    def request_jump(self):
        self.jump_buffer = 8  # Keep jump request alive for 8 frames

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vx = 0.0
        move_speed = self.crouch_speed if self.is_hidden else self.speed

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -move_speed
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = move_speed
            self.facing = 1

        # Continuous polling support for jump keys
        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
            self.request_jump()

    def update(self, platforms, bushes):
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        # Check bush cover
        self.is_hidden = any(self.rect.colliderect(b.rect.inflate(16, 8)) for b in bushes)

        # 1. Execute Jump if buffered and within coyote time
        if self.jump_buffer > 0 and self.coyote_timer > 0:
            self.vy = self.jump_force
            self.coyote_timer = 0
            self.jump_buffer = 0

        # 2. Horizontal Movement & Collision
        self.x_pos += self.vx
        self.rect.x = round(self.x_pos)
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx > 0:
                    self.rect.right = p.rect.left
                elif self.vx < 0:
                    self.rect.left = p.rect.right
                self.x_pos = float(self.rect.x)

        # 3. Vertical Gravity & Movement
        self.vy = min(self.vy + self.gravity, self.max_fall_speed)
        self.y_pos += self.vy
        self.rect.y = round(self.y_pos)

        # 4. Vertical Collision Resolution
        on_ground_now = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vy > 0:  # Landing on platform
                    self.rect.bottom = p.rect.top
                    self.y_pos = float(self.rect.y)
                    self.vy = 0.0
                    on_ground_now = True
                elif self.vy < 0:  # Hitting ceiling
                    self.rect.top = p.rect.bottom
                    self.y_pos = float(self.rect.y)
                    self.vy = 0.0

        if on_ground_now:
            self.coyote_timer = 6  # 6 frames of jump forgiveness
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1

        # 5. Animation State Priority
        if self.attack_timer > 0:
            self.state = "attack"
        elif self.coyote_timer == 0:
            self.state = "jump"
        elif self.is_hidden:
            self.state = "crouch"
        elif abs(self.vx) > 0:
            self.state = "walk"
        else:
            self.state = "idle"

    def draw(self, surface, offset_x):
        if self.invulnerable_timer > 0 and (self.invulnerable_timer // 6) % 2 == 1:
            return

        active = self.anims.get(self.state, self.anims["idle"])

        if self.state == "crouch" and active.frames:
            frame = active.frames[0]
            if self.facing == -1:
                frame = pygame.transform.flip(frame, True, False)
        else:
            frame = active.get_frame(flip_x=(self.facing == -1))

        if frame:
            surface.blit(frame, (self.rect.x - offset_x, self.rect.y))
        else:
            pygame.draw.rect(surface, COLOR_HERO, (self.rect.x - offset_x, self.rect.y, self.rect.w, self.rect.h))

        if self.state == "attack" and not self.anims["attack"].frames:
            slash_x = self.rect.right - offset_x if self.facing == 1 else self.rect.left - offset_x - 14
            pygame.draw.rect(surface, (255, 230, 80), (slash_x, self.rect.y + 8, 14, 16))


class Sentry(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_distance=64):
        super().__init__()
        base = "assets/scout.gif" if os.path.exists("assets/scout.gif") else "assets/bad guy.gif"
        self.anim = AnimatedGif(base, (24, 32), frame_delay=8, align_to_bottom=True)
        self.rect = pygame.Rect(x, y, 24, 32)
        self.origin_x = x
        self.patrol_distance = patrol_distance
        self.speed = 1.4
        self.facing = 1
        self.view_distance = 140

    def update(self):
        self.rect.x += int(self.speed * self.facing)
        if abs(self.rect.x - self.origin_x) > self.patrol_distance:
            self.facing *= -1

    def draw(self, surface, offset_x):
        frame = self.anim.get_frame(flip_x=(self.facing == -1))
        draw_rect = (self.rect.x - offset_x, self.rect.y, self.rect.w, self.rect.h)
        if frame:
            surface.blit(frame, draw_rect[:2])
        else:
            pygame.draw.rect(surface, COLOR_SCOUT, draw_rect)


class StaticProp(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, gif_path, fallback_color):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.anim = AnimatedGif(gif_path, (w, h), frame_delay=12)
        self.color = fallback_color

    def draw(self, surface, offset_x):
        frame = self.anim.get_frame()
        draw_rect = (self.rect.x - offset_x, self.rect.y, self.rect.w, self.rect.h)
        if frame:
            surface.blit(frame, draw_rect[:2])
        else:
            pygame.draw.rect(surface, self.color, draw_rect)


# ==============================================================================
# SECTION 5: DIALOGUE BOX WITH WORD-WRAPPING
# ==============================================================================
class DialogueBox:
    def __init__(self, font):
        self.font = font
        self.active = False
        self.pages = []
        self.page_index = 0

    def start(self, pages):
        if pages:
            self.pages = pages
            self.page_index = 0
            self.active = True

    def advance(self):
        self.page_index += 1
        if self.page_index >= len(self.pages):
            self.active = False

    def wrap_text(self, text, max_width):
        words = text.split(" ")
        lines = []
        current = ""
        for w in words:
            test = f"{current} {w}".strip()
            if self.font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines

    def draw(self, surface):
        if not self.active:
            return
        box = pygame.Rect(40, SCREEN_HEIGHT - 130, SCREEN_WIDTH - 80, 100)
        pygame.draw.rect(surface, (24, 22, 26), box, border_radius=8)
        pygame.draw.rect(surface, (215, 175, 80), box, 2, border_radius=8)

        max_w = box.width - 40
        wrapped_lines = self.wrap_text(self.pages[self.page_index], max_w)

        line_h = self.font.get_linesize() + 4
        for i, line_str in enumerate(wrapped_lines):
            rendered = self.font.render(line_str, True, COLOR_TEXT)
            surface.blit(rendered, (box.x + 20, box.y + 16 + (i * line_h)))

        prompt = self.font.render("[SPACE] to continue...", True, (160, 155, 140))
        surface.blit(prompt, (box.right - 180, box.bottom - 24))


# ==============================================================================
# SECTION 6: ASCII PARSER
# ==============================================================================
def build_level_from_ascii(ascii_map):
    raw_lines = [line for line in ascii_map.strip('\n').split('\n')]
    map_height = len(raw_lines) * TILE_SIZE
    map_width = max(len(line) for line in raw_lines) * TILE_SIZE

    platforms = []
    bushes = []
    hazards = []
    sentries = []
    player = None
    relic = None
    portal = None

    for row_idx, row in enumerate(raw_lines):
        for col_idx, char in enumerate(row):
            px = col_idx * TILE_SIZE
            py = row_idx * TILE_SIZE

            if char in ('#', '='):
                platforms.append(StaticProp(px, py, TILE_SIZE, TILE_SIZE, "assets/tile.gif", COLOR_PLATFORM))
            elif char == '~':
                bushes.append(StaticProp(px - 8, py - 4, 48, 36, "assets/bush.gif", COLOR_BUSH))
            elif char == 'x':
                hazards.append(StaticProp(px, py + 12, TILE_SIZE, 20, "assets/hazard.gif", COLOR_HAZARD))
            elif char == '*':
                sentries.append(Sentry(px, py))
            elif char == '$':
                relic = StaticProp(px, py, 24, 24, "assets/relic.gif", COLOR_RELIC)
            elif char == 'E':
                portal = StaticProp(px, py - 16, 32, 48, "assets/portal.gif", COLOR_PORTAL)
            elif char == '@':
                player = Player(px, py)

    if not player:
        player = Player(50, 50)

    return map_width, map_height, platforms, bushes, hazards, sentries, relic, portal, player


# ==============================================================================
# SECTION 7: HEART LIFE COUNTER RENDERER
# ==============================================================================
def draw_hearts(surface, current_lives, max_lives=5):
    start_x = SCREEN_WIDTH - 130
    y = 16
    heart_spacing = 22

    for i in range(max_lives):
        hx = start_x + (i * heart_spacing)
        color = COLOR_HEART if i < current_lives else COLOR_HEART_EMPTY
        pygame.draw.circle(surface, color, (hx + 4, y + 4), 4)
        pygame.draw.circle(surface, color, (hx + 12, y + 4), 4)
        triangle_points = [(hx, y + 5), (hx + 16, y + 5), (hx + 8, y + 14)]
        pygame.draw.polygon(surface, color, triangle_points)


# ==============================================================================
# SECTION 8: MAIN GAME LOOP & HORIZONTAL CAMERA ENGINE
# ==============================================================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pixel Quest: Student ASCII Map Platformer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)
    big_font = pygame.font.SysFont("monospace", 22, bold=True)

    bg_anim = AnimatedGif("assets/background.gif", (SCREEN_WIDTH, SCREEN_HEIGHT), frame_delay=30)
    dialogue = DialogueBox(font)

    current_act = 0
    lives = MAX_LIVES
    game_state = "INTRO"

    def load_act(index):
        data = STUDENT_ACTS[index]
        w, h, plats, bshs, hazs, snts, rlc, prtl, hero = build_level_from_ascii(data["map"])
        dialogue.start(data["intro"])
        return w, h, plats, bshs, hazs, snts, rlc, prtl, hero

    map_w, map_h, platforms, bushes, hazards, sentries, relic, portal, hero = load_act(current_act)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "PLAY" and not dialogue.active:
                    hero.trigger_attack()

            if event.type == pygame.KEYDOWN:
                if game_state == "VICTORY":
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        running = False

                elif game_state == "GAME_OVER":
                    if event.key in (pygame.K_r, pygame.K_SPACE):
                        lives = MAX_LIVES
                        map_w, map_h, platforms, bushes, hazards, sentries, relic, portal, hero = load_act(current_act)
                        game_state = "PLAY"
                    elif event.key == pygame.K_ESCAPE:
                        running = False

                elif dialogue.active:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                        dialogue.advance()
                        if not dialogue.active:
                            if game_state == "INTRO":
                                game_state = "PLAY"
                            elif game_state == "OUTRO":
                                current_act += 1
                                if current_act < len(STUDENT_ACTS):
                                    map_w, map_h, platforms, bushes, hazards, sentries, relic, portal, hero = load_act(current_act)
                                    game_state = "INTRO"
                                else:
                                    game_state = "VICTORY"

                elif game_state == "PLAY":
                    if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                        hero.request_jump()
                    elif event.key in (pygame.K_f, pygame.K_j):
                        hero.trigger_attack()

        # ----------------------------------------------------------------------
        # GAMEPLAY LOGIC & ATTACK RESOLUTION
        # ----------------------------------------------------------------------
        if game_state == "PLAY" and not dialogue.active:
            hero.handle_input()
            hero.update(platforms, bushes)

            # Attack Hitbox check (Hero striking sentries)
            attack_box = hero.get_attack_hitbox()
            if attack_box:
                defeated = [s for s in sentries if attack_box.colliderect(s.rect)]
                for d in defeated:
                    sentries.remove(d)

            # Check damage against hero
            if hero.invulnerable_timer == 0:
                take_damage = False

                for sentry in sentries:
                    if not hero.is_hidden and abs(sentry.rect.centery - hero.rect.centery) < 24:
                        dx = hero.rect.centerx - sentry.rect.centerx
                        if (sentry.facing == 1 and 0 < dx < sentry.view_distance) or (sentry.facing == -1 and -sentry.view_distance < dx < 0):
                            take_damage = True
                            break

                if not take_damage:
                    for haz in hazards:
                        if hero.rect.colliderect(haz.rect):
                            take_damage = True
                            break

                if take_damage:
                    lives -= 1
                    if lives <= 0:
                        game_state = "GAME_OVER"
                    else:
                        hero.trigger_damage()

            for sentry in sentries:
                sentry.update()

            # Cipher pickup
            if relic and hero.rect.colliderect(relic.rect):
                hero.has_relic = True
                relic = None

            # Portal reach
            if portal and hero.has_relic and hero.rect.colliderect(portal.rect):
                game_state = "OUTRO"
                dialogue.start(STUDENT_ACTS[current_act]["outro"])

        # Horizontal Camera Math
        target_camera_x = hero.rect.centerx - (SCREEN_WIDTH // 2)
        camera_offset_x = max(0, min(target_camera_x, max(0, map_w - SCREEN_WIDTH)))

        # ----------------------------------------------------------------------
        # RENDERING PASS
        # ----------------------------------------------------------------------
        bg_frame = bg_anim.get_frame()
        if bg_frame:
            screen.blit(bg_frame, (0, 0))
        else:
            screen.fill((20, 24, 32))

        for p in platforms:
            p.draw(screen, camera_offset_x)
        for b in bushes:
            b.draw(screen, camera_offset_x)
        for h in hazards:
            h.draw(screen, camera_offset_x)
        if relic:
            relic.draw(screen, camera_offset_x)
        if portal:
            portal.draw(screen, camera_offset_x)
        for s in sentries:
            s.draw(screen, camera_offset_x)

        hero.draw(screen, camera_offset_x)

        # In-game HUD
        if game_state in ("PLAY", "INTRO", "OUTRO"):
            act_info = STUDENT_ACTS[current_act]
            hud_status = "HIDDEN" if hero.is_hidden else "VISIBLE"
            hud_relic = "SECURED" if hero.has_relic else "SEARCHING"
            hud_text = font.render(f"{act_info['title']} | {hud_status} | CIPHER: {hud_relic} | [F] ATTACK", True, COLOR_TEXT)
            screen.blit(hud_text, (20, 16))
            draw_hearts(screen, lives, MAX_LIVES)

        dialogue.draw(screen)

        # Game Over Splash
        if game_state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((20, 10, 12, 230))
            screen.blit(overlay, (0, 0))
            loss_txt = big_font.render("MISSION FAILED: HEARTS DEPLETED", True, (235, 60, 60))
            sub_txt = font.render("Press [R] or [SPACE] to Retry Act  |  [ESC] to Quit", True, (215, 205, 195))
            screen.blit(loss_txt, (SCREEN_WIDTH // 2 - loss_txt.get_width() // 2, 210))
            screen.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 250))

        # Victory Splash
        if game_state == "VICTORY":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((15, 18, 26, 220))
            screen.blit(overlay, (0, 0))
            vic_txt = big_font.render("CAMPAIGN COMPLETE! ATHENS PREVAILS!", True, (245, 215, 100))
            sub_txt = font.render("All 3 Acts cleared with honor. Press ESC or SPACE to exit.", True, (210, 205, 195))
            screen.blit(vic_txt, (SCREEN_WIDTH // 2 - vic_txt.get_width() // 2, 210))
            screen.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 250))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
