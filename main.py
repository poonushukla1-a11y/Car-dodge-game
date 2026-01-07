import pygame, random, os

pygame.init()
pygame.mixer.init()

# ================= SCREEN (PYGBAG FIX) =================
# DO NOT USE pygame.FULLSCREEN in pygbag
screen = pygame.display.set_mode((800, 600))
WIDTH, HEIGHT = screen.get_size()
clock = pygame.time.Clock()

pygame.display.set_caption("Car Game")

# ================= COLORS =================
WHITE = (255,255,255)
BLACK = (0,0,0)
RED   = (255,0,0)
GREEN = (0,255,0)
BLUE  = (0,0,255)
ORANGE= (255,165,0)
GRAY  = (120,120,120)

# ================= FONTS =================
font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 34)
car_font = pygame.font.SysFont("arial", 26)

# ================= TOUCH FIX =================
def get_pos(event):
    if event.type in (pygame.FINGERDOWN, pygame.FINGERUP):
        return int(event.x * WIDTH), int(event.y * HEIGHT)
    return event.pos

# ================= GAME STATE =================
state = "home"
running = True
paused = False

# ================= ADS / REVIVE =================
ads_available = True
revive_used = False
show_ad_message = ""
ad_message_timer = 0

# ================= SAFE SOUND LOAD =================
def safe_sound(file):
    try:
        return pygame.mixer.Sound(file)
    except:
        return None

snd_click = safe_sound("click.wav")
snd_coin  = safe_sound("coin.wav")
snd_crash = safe_sound("crash.wav")
snd_power = safe_sound("power.wav")

# ================= CAR =================
CAR_W, CAR_H = 50, 22
car = {
    "x": WIDTH // 2,
    "y": HEIGHT - 260,
    "speed": 7,
    "shape": "0/--°--\\0"
}

# ================= SKINS =================
skins = [
    ("Dhunnu","0/--°--\\0",0),
    ("Caraa_cara","0---∆---0",1),
    ("Chara","<---0---->",3),
    ("Jaara","<--67-->",5),
    ("Cara_Z","0--69--0",5),
    ("Naara","--------",8),
    ("Modi ji","&--&",10),
    ("Bittu","$----$",12),
    ("Yashha","--XD--",12),
    ("Somu","--:-)--",12),
    ("Technoblaze","+.+",49),
    ("Bambaa","///0\\",50)
]

owned_skins = {"Dhunnu"}
current_skin = "Dhunnu"
skin_index = 0

# ================= GAME DATA =================
stars = []
coins = []
specials = []

score = 0
high_score = 0
total_coins = 0

immortal = False
immortal_left = 0

STAR_SIZE = 30
COIN_SIZE = 20

# ================= LEADERBOARD =================
leaderboard = [
    ("Samriddhi",1000),
    ("Saumya",900),
    ("Yashu",800),
    ("Avichal",700),
    ("Manav",600),
    ("Pihu",500),
    ("Poonam",400),
    ("Saurabh",300),
    ("Ankit",200),
    ("Shuklaji",100)
]
player_name = "You"

# ================= SAVE / LOAD =================
def load_int(file):
    try:
        return int(open(file).read())
    except:
        return 0

high_score = load_int("high_score.txt")
total_coins = load_int("coins.txt")

def save_data():
    open("high_score.txt","w").write(str(high_score))
    open("coins.txt","w").write(str(total_coins))

# ================= TIMERS (CRASH FIX) =================
star_timer = 0
coin_timer = 0
special_timer = 0

# ================= MOVEMENT FLAGS =================
move_left = False
move_right = False
# ================= BUTTONS =================
start_btn = pygame.Rect(WIDTH//2-120, HEIGHT//2-150, 240, 60)
skins_btn = pygame.Rect(WIDTH//2-120, HEIGHT//2-70, 240, 60)
leader_btn= pygame.Rect(WIDTH//2-120, HEIGHT//2+10, 240, 60)
info_btn  = pygame.Rect(WIDTH//2-120, HEIGHT//2+90, 240, 60)

back_btn = pygame.Rect(30, 30, 120, 50)

play_again_btn = pygame.Rect(WIDTH//2-120, HEIGHT//2+60, 240, 60)
home_btn = pygame.Rect(WIDTH//2-120, HEIGHT//2+140, 240, 60)

revive_btn = pygame.Rect(WIDTH//2-120, HEIGHT//2-20, 240, 60)

pause_btn = pygame.Rect(WIDTH-70, 20, 50, 40)

left_btn = {"center": (110, HEIGHT-140), "radius": 55}
right_btn= {"center": (WIDTH-110, HEIGHT-140), "radius": 55}

left_skin_btn = pygame.Rect(60, HEIGHT//2-40, 80, 80)
right_skin_btn= pygame.Rect(WIDTH-140, HEIGHT//2-40, 80, 80)

resume_btn = pygame.Rect(WIDTH//2-120, HEIGHT//2+40, 240, 60)

# ================= HELPERS =================
def fall_speed():
    if score >= 500: return 9
    if score >= 100: return 7
    return 5

def reset_game():
    global score, stars, coins, specials, immortal, immortal_left, revive_used
    score = 0
    stars.clear()
    coins.clear()
    specials.clear()
    immortal = False
    immortal_left = 0
    revive_used = False
    car["x"] = WIDTH // 2

# ================= BACKGROUNDS =================
def draw_menu_bg():
    screen.fill((30, 30, 60))
    for _ in range(30):
        pygame.draw.circle(
            screen,
            (50,50,90),
            (random.randint(0, WIDTH), random.randint(0, HEIGHT)),
            random.randint(1,3)
        )

def draw_game_bg():
    screen.fill((135,206,235))
    pygame.draw.circle(screen, (255,255,180), (WIDTH-120,120), 60)

# ================= HOME =================
def draw_home():
    draw_menu_bg()

    pygame.draw.rect(screen, GREEN, start_btn)
    pygame.draw.rect(screen, BLUE, skins_btn)
    pygame.draw.rect(screen, ORANGE, leader_btn)
    pygame.draw.rect(screen, GRAY, info_btn)

    screen.blit(font.render("START",1,WHITE),(start_btn.x+80,start_btn.y+18))
    screen.blit(font.render("SKINS",1,WHITE),(skins_btn.x+85,skins_btn.y+18))
    screen.blit(font.render("LEADERBOARD",1,WHITE),(leader_btn.x+40,leader_btn.y+18))
    screen.blit(font.render("INFO",1,WHITE),(info_btn.x+95,info_btn.y+18))

    screen.blit(font.render(f"High Score: {high_score}",1,WHITE),(20,20))
    screen.blit(font.render(f"Coins: {total_coins}",1,ORANGE),(WIDTH-220,20))

# ================= CONTROLS =================
def draw_controls():
    pygame.draw.circle(screen, RED, left_btn["center"], left_btn["radius"])
    pygame.draw.circle(screen, RED, right_btn["center"], right_btn["radius"])

    screen.blit(font.render("L",1,WHITE),
                (left_btn["center"][0]-10,left_btn["center"][1]-15))
    screen.blit(font.render("R",1,WHITE),
                (right_btn["center"][0]-10,right_btn["center"][1]-15))

# ================= SKINS =================
def draw_skins():
    draw_menu_bg()

    name, shape, cost = skins[skin_index]

    pygame.draw.rect(screen, RED, back_btn)
    screen.blit(font.render("BACK",1,WHITE),(back_btn.x+25,back_btn.y+15))

    pygame.draw.rect(screen, BLUE, left_skin_btn)
    pygame.draw.rect(screen, BLUE, right_skin_btn)

    screen.blit(font.render("◀",1,WHITE),(left_skin_btn.x+30,left_skin_btn.y+25))
    screen.blit(font.render("▶",1,WHITE),(right_skin_btn.x+30,right_skin_btn.y+25))

    screen.blit(car_font.render(shape,1,WHITE),(WIDTH//2-60,160))
    screen.blit(font.render(name,1,WHITE),(WIDTH//2-70,210))

    price = "FREE" if cost == 0 else f"{cost} coins"
    screen.blit(font.render(price,1,ORANGE),(WIDTH//2-60,240))

    action_btn = pygame.Rect(WIDTH//2-100,300,200,60)

    if name == current_skin:
        pygame.draw.rect(screen, GRAY, action_btn)
        txt = "SELECTED"
    elif name in owned_skins:
        pygame.draw.rect(screen, GREEN, action_btn)
        txt = "SELECT"
    else:
        pygame.draw.rect(screen, BLUE, action_btn)
        txt = "BUY"

    screen.blit(font.render(txt,1,WHITE),(action_btn.x+60,action_btn.y+18))
    screen.blit(font.render(f"Coins: {total_coins}",1,ORANGE),(WIDTH-220,20))

    return action_btn

# ================= LEADERBOARD =================
def draw_leaderboard():
    draw_menu_bg()

    pygame.draw.rect(screen, RED, back_btn)
    screen.blit(font.render("BACK",1,WHITE),(back_btn.x+25,back_btn.y+15))

    screen.blit(big_font.render("LEADERBOARD",1,WHITE),(WIDTH//2-130,60))

    temp = leaderboard.copy()
    if high_score > temp[-1][1]:
        temp.append((player_name, high_score))
        temp.sort(key=lambda x: x[1], reverse=True)
        temp = temp[:10]

    y = 140
    for i,(name,sc) in enumerate(temp):
        color = GREEN if name == player_name else WHITE
        screen.blit(font.render(f"{i+1}. {name} - {sc}",1,color),
                    (WIDTH//2-160,y))
        y += 35

# ================= INFO =================
def draw_info():
    draw_menu_bg()

    lines = [
        "INFO",
        "",
        "SS = gives immortality",
        "RS = adds 20 to score",
        "O  = coin",
        "",
        "For business contact:",
        "kingshukla0100@gmail.com"
    ]

    y = 120
    for line in lines:
        screen.blit(font.render(line,1,WHITE),(WIDTH//2-180,y))
        y += 40

    pygame.draw.rect(screen, RED, back_btn)
    screen.blit(font.render("BACK",1,WHITE),(back_btn.x+25,back_btn.y+15))

# ================= PAUSE =================
def draw_pause():
    screen.fill((80,80,80))
    screen.blit(big_font.render("PAUSED",1,WHITE),(WIDTH//2-80,140))

    pygame.draw.rect(screen, GREEN, resume_btn)
    screen.blit(font.render("RESUME",1,WHITE),
                (resume_btn.x+80,resume_btn.y+18))

# ================= END =================
def draw_end():
    screen.fill(BLACK)

    screen.blit(big_font.render("GAME OVER",1,RED),(WIDTH//2-130,110))
    screen.blit(font.render(f"Score: {score}",1,WHITE),(WIDTH//2-60,160))

    if not revive_used:
        pygame.draw.rect(screen, GREEN, revive_btn)
        screen.blit(font.render("REVIVE (WATCH AD)",1,WHITE),
                    (revive_btn.x+25,revive_btn.y+18))

    pygame.draw.rect(screen, BLUE, play_again_btn)
    pygame.draw.rect(screen, ORANGE, home_btn)

    screen.blit(font.render("PLAY AGAIN",1,WHITE),
                (play_again_btn.x+50,play_again_btn.y+18))
    screen.blit(font.render("HOME",1,WHITE),
                (home_btn.x+90,home_btn.y+18))

    if show_ad_message:
        screen.blit(font.render(show_ad_message,1,RED),
                    (WIDTH//2-150, HEIGHT//2+120))
                    # ================= GAME FLAGS =================
move_left = False
move_right = False
paused = False

revive_used = False
show_ad_message = ""

star_timer = 0
coin_timer = 0
special_timer = 0

# ================= MAIN LOOP =================
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # -------- INPUT DOWN --------
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pos = get_pos(event)
            if snd_click:
                snd_click.play()

            # ---------- HOME ----------
            if state == "home":
                if start_btn.collidepoint(pos):
                    car["shape"] = dict((n,s) for n,s,_ in skins)[current_skin]
                    reset_game()
                    state = "play"
                elif skins_btn.collidepoint(pos):
                    state = "skins"
                elif leader_btn.collidepoint(pos):
                    state = "leaderboard"
                elif info_btn.collidepoint(pos):
                    state = "info"

            # ---------- SKINS ----------
            elif state == "skins":
                if back_btn.collidepoint(pos):
                    state = "home"
                elif left_skin_btn.collidepoint(pos):
                    skin_index = (skin_index - 1) % len(skins)
                elif right_skin_btn.collidepoint(pos):
                    skin_index = (skin_index + 1) % len(skins)
                else:
                    btn = draw_skins()
                    name, shape, cost = skins[skin_index]
                    if btn.collidepoint(pos):
                        if name in owned_skins:
                            current_skin = name
                        elif total_coins >= cost:
                            total_coins -= cost
                            owned_skins.add(name)
                            current_skin = name
                            save_data()

            # ---------- LEADERBOARD ----------
            elif state == "leaderboard":
                if back_btn.collidepoint(pos):
                    state = "home"

            # ---------- INFO ----------
            elif state == "info":
                if back_btn.collidepoint(pos):
                    state = "home"

            # ---------- PLAY ----------
            elif state == "play":
                if pause_btn.collidepoint(pos):
                    paused = True
                    state = "pause"
                elif (pos[0]-left_btn["center"][0])**2 + (pos[1]-left_btn["center"][1])**2 <= left_btn["radius"]**2:
                    move_left = True
                elif (pos[0]-right_btn["center"][0])**2 + (pos[1]-right_btn["center"][1])**2 <= right_btn["radius"]**2:
                    move_right = True

            # ---------- PAUSE ----------
            elif state == "pause":
                if resume_btn.collidepoint(pos):
                    paused = False
                    state = "play"

            # ---------- END ----------
            elif state == "end":
                if not revive_used and revive_btn.collidepoint(pos):
                    if random.choice([True, False]):
                        revive_used = True
                        immortal = True
                        immortal_left = 20
                        state = "play"
                    else:
                        show_ad_message = "Ads not available"

                elif play_again_btn.collidepoint(pos):
                    reset_game()
                    state = "play"

                elif home_btn.collidepoint(pos):
                    state = "home"

        # -------- INPUT UP --------
        if event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
            move_left = False
            move_right = False

    # ================= GAME LOGIC =================
    if state == "play" and not paused:

        if move_left and car["x"] > 0:
            car["x"] -= car["speed"]
        if move_right and car["x"] < WIDTH - CAR_W:
            car["x"] += car["speed"]

        star_timer += 1
        coin_timer += 1
        special_timer += 1

        if star_timer > 30:
            stars.append({"x": random.randint(0, WIDTH-STAR_SIZE), "y": 0})
            star_timer = 0

        if coin_timer > 90:
            coins.append({"x": random.randint(0, WIDTH-COIN_SIZE), "y": 0})
            coin_timer = 0

        if score >= 50 and special_timer > 300:
            specials.append({
                "x": random.randint(0, WIDTH-30),
                "y": 0,
                "type": random.choice(["SS","RS"])
            })
            special_timer = 0

        car_rect = pygame.Rect(car["x"], car["y"], CAR_W, CAR_H)

        for s in stars[:]:
            s["y"] += fall_speed()
            star_rect = pygame.Rect(s["x"], s["y"], STAR_SIZE, STAR_SIZE)

            if star_rect.colliderect(car_rect):
                if not immortal:
                    if snd_crash:
                        snd_crash.play()
                    if score > high_score:
                        high_score = score
                        save_data()
                    state = "end"
                stars.remove(s)

            elif s["y"] > HEIGHT:
                stars.remove(s)
                score += 1

        for c in coins[:]:
            c["y"] += fall_speed()
            coin_rect = pygame.Rect(c["x"], c["y"], COIN_SIZE, COIN_SIZE)

            if coin_rect.colliderect(car_rect):
                score += 5
                total_coins += 1
                if snd_coin:
                    snd_coin.play()
                save_data()
                coins.remove(c)
            elif c["y"] > HEIGHT:
                coins.remove(c)

        for sp in specials[:]:
            sp["y"] += fall_speed()
            sp_rect = pygame.Rect(sp["x"], sp["y"], 30, 30)

            if sp_rect.colliderect(car_rect):
                if snd_power:
                    snd_power.play()
                if sp["type"] == "SS":
                    immortal = True
                    immortal_left = 25
                else:
                    score += 20
                specials.remove(sp)
            elif sp["y"] > HEIGHT:
                specials.remove(sp)

        if immortal:
            immortal_left -= 1
            if immortal_left <= 0:
                immortal = False

    # ================= DRAW =================
    if state == "home":
        draw_home()
    elif state == "skins":
        draw_skins()
    elif state == "leaderboard":
        draw_leaderboard()
    elif state == "info":
        draw_info()
    elif state == "play":
        draw_game_bg()

        for s in stars:
            screen.blit(font.render("★",1,RED),(s["x"],s["y"]))
        for c in coins:
            screen.blit(font.render("O",1,ORANGE),(c["x"],c["y"]))
        for sp in specials:
            color = GREEN if sp["type"]=="SS" else BLUE
            screen.blit(font.render(sp["type"],1,color),(sp["x"],sp["y"]))

        screen.blit(car_font.render(car["shape"],1,WHITE),(car["x"],car["y"]))
        draw_controls()

        pygame.draw.rect(screen, GRAY, pause_btn)
        screen.blit(font.render("||",1,WHITE),(pause_btn.x+18,pause_btn.y+12))

        screen.blit(font.render(f"Score: {score}",1,WHITE),(20,20))
        screen.blit(font.render(f"Coins: {total_coins}",1,ORANGE),(20,50))

    elif state == "pause":
        draw_pause()
    elif state == "end":
        draw_end()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()