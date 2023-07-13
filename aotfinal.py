from pygame import *
import random
import time as t

mixer.pre_init(44100, 16, 2, 4096)
init()

WIDTH, HEIGHT = 1200, 800
screen = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Titan Slayer: The Game")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 255, 0)
GREEN = (0, 0, 255)

ACC = 4
FRIC = -0.7
COUNT = 0

FPS = 30
clock = time.Clock()


def imageLoad(inverted, animList, animNames, animListInverted=None):
    for element in animNames:
        animList.append(image.load(element).convert_alpha())
        if inverted:
            animListInverted.append(transform.flip(image.load(element).convert_alpha(), True, False))


# movement
runRight, runLeft = [], []
runNames = ["assets/erenstanding.png", "assets/erenrun0.png", "assets/erenrun1.png",
            "assets/erenrun2.png", "assets/erenrun3.png", "assets/erenrun4.png", "assets/erenrun5.png"]
imageLoad(True, runRight, runNames, runLeft)

# attack animations
atkRight, atkLeft = [], []
atkNames = ["assets/attack0r.png", "assets/attack1r.png", "assets/attack2r.png",
            "assets/attack3r.png", "assets/attack4r.png", "assets/attack5r.png", "assets/attack0r.png"]
imageLoad(True, atkRight, atkNames, atkLeft)

deathAnim = []
deathNames = ["assets/enemydeath1.png", "assets/enemydeath2.png",
              "assets/enemydeath3.png", "assets/enemydeath4.png"]
imageLoad(False, deathAnim, deathNames)

healthAnim = []
healthNames = ["assets/hearts1.png", "assets/hearts2.png", "assets/hearts3.png",
               "assets/hearts4.png", "assets/hearts5.png"]
imageLoad(False, healthAnim, healthNames)

levelAnim = []
levelAnimNames = ["assets/levelcomplete1.png", "assets/levelcomplete2.png", "assets/levelcomplete3.png",
                  "assets/levelcomplete4.png", "assets/levelcomplete5.png", "assets/levelcomplete6.png",
                  "assets/levelcomplete7.png"]
imageLoad(False, levelAnim, levelAnimNames)

gameoverAnim = []
gameoverNames = ["assets/gameover1.png", "assets/gameover2.png", "assets/gameover3.png",
                 "assets/gameover4.png", "assets/gameover5.png", "assets/gameover6.png",
                 "assets/gameover7.png"]
imageLoad(False, gameoverAnim, gameoverNames)

# fonts
fontSmall = font.Font("assets/Minecraft.ttf", 20)
fontMed = font.Font("assets/Minecraft.ttf", 30)
fontBig = font.Font("assets/Minecraft.ttf", 50)

# menu imgs
titleText = fontBig.render("TITAN SLAYER: THE GAME", True, WHITE)
menubg = image.load("assets/menubg.png").convert()
# menu buttons
startimg = image.load("assets/start.png").convert()
startRect = startimg.get_rect()
startRect.topleft = (50, 150)
questimg = image.load("assets/sidequest.png").convert()
questRect = questimg.get_rect()
questRect.topleft = (50, 250)

# level images
level1bg = image.load("assets/levelbg1.png").convert()
level2bg = image.load("assets/levelbg2.png").convert()
level3bg = image.load("assets/levelbg3.png").convert()

# quest images
questbg = image.load("assets/questbg.png").convert()


class Player(sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.atkDmg = 10
        self.recharge = False
        self.boost = 2
        self.boostCooldown = 10
        self.lastDir = None
        self.startup = 0.6
        self.image = image.load("assets/erenstanding.png")
        self.rect = self.image.get_rect()
        self.running = False
        self.moveFrame = 0  # frame of character currently
        self.deathFrame = 0
        self.health = 100
        self.mana = 0
        self.manaReset = 20
        self.deathFrameWait = 0

        # position and direction of character
        self.posx = 600
        self.posy = 520
        self.speed = 0
        self.moveCap = 0
        self.direction = 'RIGHT'  # direction facing

        # attack variables
        self.attacking = False
        self.cooldown = False
        self.atkFrame = 0
        self.attackMove = 0

        # jump
        self.jumping = False
        self.falling = False
        self.jumpSpeed = 2

    def move(self):
        global scrollAmount
        movementKeys = key.get_pressed()

        if self.speed < 1 and (movementKeys[K_a] or movementKeys[K_d]):
            self.speed += 6

        if (movementKeys[K_a] and self.lastDir == 1) or (movementKeys[K_d] and self.lastDir == 0):
            self.speed = 0.1

        if movementKeys[K_w]:
            self.jumping = True
        if movementKeys[K_LSHIFT]:
            self.attacking = True
        if movementKeys[K_a]:
            self.lastDir = 0
            self.posx -= self.speed
            self.direction = "LEFT"
        elif movementKeys[K_d]:
            self.lastDir = 1
            self.posx += self.speed
            self.direction = "RIGHT"
        else:
            self.speed = 0
        # character goes around screen
        if self.posx > WIDTH + 32 and scrollAmount > -1340:
            self.posx = -32
            if questStart and scrollAmount >= -670:
                scrollAmount -= 670
        elif self.posx > WIDTH + 32 and scrollAmount == -1340:
            self.posx = WIDTH + 32
        if self.posx < -32 and scrollAmount != 0:
            self.posx = WIDTH + 32
            if questStart and scrollAmount <= -670:
                scrollAmount += 670
        elif self.posx < -32 and scrollAmount == 0:
            self.posx = -32

        self.rect = self.image.get_rect()
        self.rect.topleft = (self.posx, self.posy)  # update rect with the player image

    def jump(self, jumpLimit):
        jumpKeys = key.get_pressed()
        if self.jumping:
            self.posy -= 8 * self.jumpSpeed
            self.jumpSpeed -= 0.08
        if self.posy > jumpLimit:
            self.jumping = False
            self.jumpSpeed = 2
        if jumpKeys[K_s]:
            self.posy += 6

    def update(self):
        # return to base frame (first frame of running animation) when at end of sequence
        if self.moveFrame > 6:
            self.moveFrame = 1
        # move char to next frame # and self.running == True:
        if self.jumping == False and self.speed != 0 and self.direction == "RIGHT":
            self.image = runRight[self.moveFrame]
        elif self.jumping == False and self.direction == "LEFT":
            self.image = runLeft[self.moveFrame]
        self.moveCap += 1
        if self.moveCap > 5:
            self.moveFrame += 1
            self.moveCap = 0
        # return user to standing
        if self.speed == 0 and self.moveFrame != 0:
            self.moveFrame = 0
            if self.direction == "RIGHT":
                self.image = runRight[self.moveFrame]
            elif self.direction == "LEFT":
                self.image = runLeft[self.moveFrame]

    def attack(self):
        if self.atkFrame > 6:
            self.atkFrame = 0
            self.attacking = False
        if self.direction == "RIGHT":
            self.image = atkRight[self.atkFrame]
            self.rect = Rect(self.posx, self.posy, 120, 130)
        elif self.direction == "LEFT":
            self.image = atkLeft[self.atkFrame]
        if self.attackMove > 5:
            self.atkFrame += 1
            self.attackMove = 0
        else:
            self.attackMove += 1

    def player_hit(self):
        if not self.cooldown:
            self.cooldown = True
            time.set_timer(hitCooldown, 1000)

            self.health = self.health - enemy.dmg

    def deathAnim(self):
        if self.deathFrame < 4:
            screen.blit(deathAnim[self.deathFrame], (self.posx, self.posy+80))
            if self.deathFrameWait > 20:
                self.deathFrame += 1
                self.deathFrameWait = 0
            self.deathFrameWait += 1

    def reset(self):
        self.recharge = False
        self.boost = 2
        self.boostCooldown = 10
        self.lastDir = None
        self.startup = 0.6
        self.image = image.load("assets/erenstanding.png")
        self.rect = self.image.get_rect()
        self.running = False
        self.moveFrame = 0  # frame of character currently
        self.deathFrame = 0
        self.health = 100
        self.mana = 0
        self.manaReset = 20
        self.deathFrameWait = 0

        # position and direction of character
        self.posx = 600
        self.posy = 520
        self.speed = 0
        self.moveCap = 0
        self.direction = 'RIGHT'  # direction facing

        # attack variables
        self.attacking = False
        self.cooldown = False
        self.atkFrame = 0
        self.attackMove = 0

        # jump
        self.jumping = False
        self.falling = False
        self.jumpSpeed = 2


# noinspection PyAttributeOutsideInit
class Enemy(sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.currRock = False
        self.hitLimit = True
        self.dmg = 10
        self.health = 50
        self.hits = None
        self.dying = False
        self.deathFrame = 0
        self.posx = 0
        self.posy = 0
        self.chooseTitan = random.randint(1, 3)
        self.direction = random.randint(0, 1)  # 0 for right, 1 for left
        self.speed = random.randint(70, 90) / 30
        self.mana = random.randint(2, 5)
        self.deathFrameWait = 0
        self.manaAppend = True

        if self.chooseTitan == 1:
            self.image = image.load("assets/titan1.png")

        if self.chooseTitan == 2:
            self.image = image.load("assets/titan2.png")

        if self.chooseTitan == 3:
            self.image = image.load("assets/titan3.png")

        self.enemyRect = self.image.get_rect()

        if self.direction == 0:
            self.posx = -100
            self.posy = 555
        if self.direction == 1:
            self.posx = 1190
            self.posy = 555

    def move(self):
        if self.posx >= (WIDTH - 20):
            self.direction = 1
        elif self.posx <= 0:
            self.direction = 0

        if self.direction == 0:
            self.posx += self.speed
        if self.direction == 1:
            self.posx -= self.speed
        self.enemyRect.topleft = (self.posx, self.posy)

    def update(self):
        self.enemyHit = player.rect.colliderect(self.enemyRect)  # sprite.spritecollide(self, playerGroup, False)
        # if enemy gets hit as well as the player is attacking
        if self.enemyHit and player.attacking == True and self.manaAppend and self.hitLimit:
            self.health -= player.atkDmg
            self.hitLimit = False
            if self.health == 0:
                self.manaAppend = False
                player.mana += self.mana
                self.dying = True

        # checking for player dmg
        elif self.enemyHit and player.attacking == False and self.dying == False:
            player.player_hit()

        if not self.dying:
            draw.rect(screen, BLACK, (self.posx-30, self.posy-50, 100, 20))
            draw.rect(screen, WHITE, (self.posx-29, self.posy-48, enemy.health*2-4, 16))
            screen.blit(self.image, (self.posx, self.posy))

    def deathAnim(self):
        if self.dying == True and self.deathFrame < 4:
            screen.blit(deathAnim[self.deathFrame], (self.posx, self.posy + 50))
            if self.deathFrameWait > 20:
                self.deathFrame += 1
                self.deathFrameWait = 0
            self.deathFrameWait += 1

    def throwRocks(self):
        if not self.currRock:
            self.currRock = True
            rockRect = (self.posx, self.posy, 30, 30)
            draw.rect(screen, BLACK, rockRect)


def healthbar():
    draw.rect(screen, BLACK, (10, 40, 500, 30))
    draw.rect(screen, RED, (12, 42, player.health*5-4, 26))
    screen.blit(healthText, (210, 20))


# menu screen - start of game
def mainScreen():
    screen.blit(menubg, (0, -150))
    screen.blit(titleText, (50, 50))
    screen.blit(startimg, (50, 150))
    screen.blit(questimg, (50, 250))


def level(bg):
    if currLevel == 3:
        screen.blit(bg, (0, -100))
    else:
        screen.blit(bg, (0, 0))
    manaText = fontMed.render("Mana Points: " + str(player.mana), True, WHITE)
    enemyCountText = fontMed.render("Enemies Remaining: " + str(enemyCount), True, WHITE)
    screen.blit(manaText, (850, 20))
    screen.blit(enemyCountText, (850, 50))
    # add tracker and hud


levelCompleteFrame = 0
levelCompleteTimer = 0


def levelComplete():
    global levelCompleteFrame, levelCompleteTimer, currLevel
    if levelCompleteTimer < 50:
        levelCompleteTimer += 1
    else:
        if levelCompleteFrame < 7:
            t.sleep(0.1)
            screen.blit(levelAnim[levelCompleteFrame], (-100, 0))
            levelCompleteFrame += 1
        else:
            screen.blit(levelAnim[6], (-100, 0))


def cutscene(dialogue):  # give cutscene lists that contain dialogue
    pass


tempFrame1 = 0


def gameOver():
    global tempFrame1
    if tempFrame1 < 7:
        t.sleep(0.1)
        screen.blit(gameoverAnim[tempFrame1], (-100, 0))
        tempFrame1 += 1
    else:
        screen.blit(gameoverAnim[6], (-100, 0))


boostText = fontSmall.render("BOOST", True, WHITE)
healthText = fontSmall.render("HEALTH", True, WHITE)


def boost():
    boostAmount = 15
    boostKey = key.get_pressed()
    if boostKey[K_e] and player.boostCooldown > 0:
        if player.direction == "LEFT":
            player.posx -= boostAmount
        else:
            player.posx += boostAmount
        player.boostCooldown -= 1
    draw.rect(screen, BLACK, (600, 40, 200, 30), 0)
    draw.rect(screen, WHITE, (600, 40, player.boostCooldown * 20, 30))
    draw.rect(screen, BLACK, (600, 40, 200, 30), 2)
    screen.blit(boostText, (665, 20))


def quest():
    global scrollAmount
    screen.blit(questbg, (scrollAmount, 0))


running = True
gameStart, questStart = False, False
player = Player()
playerGroup = sprite.Group()
playerGroup.add(player)
hitCooldown = USEREVENT + 1
enemyGroup = sprite.Group()
enemyTotal = 1
enemyCount = enemyTotal
levelCountdown = 0
enemySpawnTimer = 0
enemyLimit = 3
currLevel = 1
isGameover = False
resetMana = 10
groundPixel = 519
scrollAmount = 0

time.set_timer(USEREVENT, 1000)

while running:
    mx, my = mouse.get_pos()
    mb = mouse.get_pressed()
    for evt in event.get():
        if evt.type == QUIT:
            running = False
        if evt.type == MOUSEBUTTONUP:
            if startRect.collidepoint(mx, my) and (gameStart == False and questStart == False):
                gameStart = True
                questStart = False
            if questRect.collidepoint(mx, my) and (gameStart == False and questStart == False):
                player.posy = 650
                groundPixel = 650
                questStart = True
                gameStart = False
            if enemyCount == 0:
                player.reset()
                levelCompleteFrame = 0
                levelCompleteTimer = 0
                currLevel += 1
                enemyCount = 1  # 5 * currLevel
        if evt.type == KEYDOWN:
            if evt.key == K_q and player.mana >= resetMana and player.health < 5:
                player.health += 1
                player.mana -= resetMana
        if evt.type == hitCooldown:
            player.cooldown = False
            enemy.hitLimit = True
        if evt.type == USEREVENT and gameStart:
            if player.boostCooldown < 10:
                player.boostCooldown += 1

    mainScreen()
    player.move()
    player.update()
    if player.jumping:
        player.jump(groundPixel)
    if player.attacking:
        player.attack()

    if gameStart:
        questStart = False
        if currLevel == 1:
            level(level1bg)
        elif currLevel == 2:
            level(level2bg)
        elif currLevel == 3:
            level(level3bg)
        else:
            gameStart = False
            currLevel = 1
        healthbar()
        boost()
        for entity in enemyGroup:
            entity.update()
            entity.move()
            entity.throwRocks()
            if entity.dying:
                entity.deathAnim()
                if entity.deathFrame > 3:
                    enemyCount -= 1
                    entity.kill()
        if enemyCount != 0 and (len(enemyGroup) < 2 and enemyCount > len(enemyGroup)) and enemySpawnTimer > 50:
            enemySpawnTimer = 0
            enemy = Enemy()
            enemyGroup.add(enemy)
        enemySpawnTimer += 1
        if player.health == 0:
            player.kill()
            player.deathAnim()
            if levelCountdown > 100:
                levelCountdown = 0
                isGameover = True
            levelCountdown += 1
        else:
            screen.blit(player.image, player.rect)
        if enemyCount == 0:
            levelComplete()

    if questStart:
        gameStart = False
        quest()
        screen.blit(player.image, player.rect)

    if isGameover:
        gameOver()

    display.flip()
    clock.tick(60)

quit()
