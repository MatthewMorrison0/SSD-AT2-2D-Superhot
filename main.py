import time

import pygame
import math
import copy
import random
from PIL import Image

# Initialise pygame
pygame.init()
pygame.font.init()
menlo = pygame.font.SysFont('menlo', 30)

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)

bullet_image_gold = pygame.image.load("Bullet Gold.png")
bullet_image_black = pygame.image.load("Bullet Black.png")

volume = 1.0

colour_theme = "Light"


# Handle any events
def eventHandler():
    global wPressed
    global aPressed
    global sPressed
    global dPressed
    global running
    global player_gun_equipped
    global guns
    global playerPos
    global playerRot
    global mode_selection
    global mode
    global volume
    global colour_theme
    global playerPosChange
    global playerRotChange
    global enemies
    global global_bullets
    global obstacles
    global timeScale
    global timeDecrease
    global shootReady
    global player_hitbox
    global newCrosshair
    global kills

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Has pygame been quit?
            mode = 0
        if event.type == pygame.KEYDOWN:  # Has a key been pressed?
            if event.key == pygame.K_ESCAPE:
                mode = 0
            if event.key == pygame.K_w:
                wPressed = True
            if event.key == pygame.K_a:
                aPressed = True
            if event.key == pygame.K_s:
                sPressed = True
            if event.key == pygame.K_d:
                dPressed = True
            if event.key == pygame.K_g and player_gun_equipped is not None:
                guns.append(player_gun_equipped)
                guns[-1].setPosition((75 * math.sin(playerRot) + playerPos[0] - player_gun_equipped.getSize() / 2, 75 * math.cos(playerRot) + playerPos[1] - player_gun_equipped.getSize() / 2))
                player_gun_equipped = None
            if event.key == pygame.K_DOWN and (mode == 0 or mode == 4 or mode == 5):
                if mode_selection < 2:
                    mode_selection += 1
                else:
                    mode_selection = 0
            if event.key == pygame.K_UP and (mode == 0 or mode == 4 or mode == 5):
                if mode_selection > 0:
                    mode_selection -= 1
                else:
                    mode_selection = 2
            if event.key == pygame.K_RETURN and mode == 0 and mode_selection == 0:
                mode = 1
            if event.key == pygame.K_RETURN and (mode == 0 or mode == 5) and mode_selection == 2:
                running = False
                mode = None
            if event.key == pygame.K_RETURN and mode == 4 and mode_selection == 2:
                mode = 0
                mode_selection = 0
            if event.key == pygame.K_RETURN and mode == 0 and mode_selection == 1:
                mode = 4
            if event.key == pygame.K_RETURN and mode == 5 and mode_selection == 0:
                # Player data
                playerPos = [200, 50]
                playerRot = 0
                playerPosChange = [0, 0]
                playerRotChange = 0
                timeScale = 1
                timeDecrease = False
                shootReady = 1
                player_hitbox = pygame.Rect((400, 100), (20, 20))
                player_gun_equipped = None
                crosshair = pygame.image.load("Crosshair.png")
                newCrosshair = crosshair
                kills = 0

                global_bullets = []
                enemies = [Enemy([400, 500]), Enemy([100, 400]), Enemy([700, 250])]
                guns = [AR([100, 450]), Pistol([300, 50])]

                mode = 1
            if event.key == pygame.K_RETURN and mode == 5 and mode_selection == 1:
               mode = 0
               mode_selection = 0

            if event.key == pygame.K_LEFT and mode == 4:
                if mode_selection == 0 and volume > 0:
                    volume = round(volume - 0.1, 1)
                elif mode_selection == 1 and colour_theme == "Light":
                    colour_theme = "Dark"
            if event.key == pygame.K_RIGHT and mode == 4:
                if mode_selection == 0 and volume < 1:
                    volume = round(volume + 0.1, 1)
                elif mode_selection == 1 and colour_theme == "Dark":
                    colour_theme = "Light"

        if event.type == pygame.KEYUP:  # Has a key been lifted?
            if event.key == pygame.K_w:
                wPressed = False
            if event.key == pygame.K_a:
                aPressed = False
            if event.key == pygame.K_s:
                sPressed = False
            if event.key == pygame.K_d:
                dPressed = False

# Class for gun
class Gun:
    def __init__(self):
        self.position = [0, 0]
        self.size = 0
        self.image = None
        self.fire_rate = 0
        self.ammo = 0
        self.max_ammo = 0

    def shoot(self, position, rotation):
        global timeDecrease
        global timeScale
        global shootReady
        if self.ammo > 0:
            global_bullets.append(Bullet(copy.deepcopy(position), copy.deepcopy(rotation)))
            timeDecrease = True
            timeScale = 1
            shootReady = 0
            self.ammo -= 1

    # Getters
    def getPosition(self):
        return self.position

    def getImage(self):
        return self.image

    def getSize(self):
        return self.size

    def getFireRate(self):
        return self.fire_rate

    def getAmmo(self):
        return self.ammo

    def getMaxAmmo(self):
        return self.max_ammo

    # Setters

    def setPosition(self, position):
        self.position = position

# Class for pistol(inherited from Gun class)
class Pistol(Gun):
    def __init__(self, position):
        self.position = position
        self.size = 40
        self.image = pygame.image.load("Pistol.png")
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.fire_rate = 2
        self.ammo = 10
        self.max_ammo = 10

# Class for AR(inherited from Gun class)
class AR(Gun):
    def __init__(self, position):
        self.position = position
        self.size = 100
        self.image = pygame.image.load("AR.png")
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.fire_rate = 1
        self.ammo = 20
        self.max_ammo = 20

# Class for enemy
class Enemy:
    def __init__(self, position):
        # initialise variables for enemy
        self.shoot_cooldown = 0
        self.position = position
        self.rotation = 0
        self.hitbox = pygame.Rect((position[0] - 20, position[1] - 20), (20, 20))
        self.bullets = []
        self.walk_amount = 0
        self.rot_amount = 0
        self.rot_dir = 1
        self.prevPos = []
        self.seePlayer = False
    def shoot(self): # Enemy shoot method
        global_bullets.append(Bullet(copy.deepcopy(self.position), self.rotation + random.randint(-5, 5) / 50))
        self.bullets.append(global_bullets[-1])

    def draw(self):  # Draw enemy
        pygame.draw.circle(window, (200, 0, 0), (self.position[0], self.position[1]), 20)
        pygame.draw.circle(window, (0, 0, 0),
                           (14 * math.sin(self.rotation) + self.position[0], 14 * math.cos(self.rotation) + self.position[1]), 2)

    def canSeePlayer(self): # Can the enemy see the player?
        self.seePlayer = True
        global obstacles
        for obstacle in obstacles:
            if self.position[0] - playerPos[0] != 0 and self.position[1] - playerPos[1] != 0:
                lineGradient = (self.position[1] - playerPos[1]) / (self.position[0] - playerPos[0])
                lineC = self.position[1] - (self.position[0] * lineGradient)
                intersectionPoint1 = obstacle.getVertices()[0][0] * lineGradient + lineC
                intersectionPoint2 = obstacle.getVertices()[2][0] * lineGradient + lineC
                intersectionPoint3 = (obstacle.getVertices()[1][1] - lineC) / lineGradient
                intersectionPoint4 = (obstacle.getVertices()[0][1] - lineC) / lineGradient

                if playerPos[0] >= self.position[0]:
                    rotation = 1.57 - math.atan(lineGradient)
                else:
                    rotation = 4.71 - math.atan(lineGradient)

                if intersectionPoint1 >= obstacle.getVertices()[0][1] and intersectionPoint1 <= obstacle.getVertices()[1][1] and not ((intersectionPoint1 <= self.position[1] and intersectionPoint1 <= playerPos[1]) or (intersectionPoint1 >= self.position[1] and intersectionPoint1 >= playerPos[1])):
                    self.seePlayer = False
                    return rotation
                if intersectionPoint2 >= obstacle.getVertices()[2][1] and intersectionPoint2 <= obstacle.getVertices()[3][1] and not ((intersectionPoint2 <= self.position[1] and intersectionPoint2 <= playerPos[1]) or (intersectionPoint2 >= self.position[1] and intersectionPoint2 >= playerPos[1])):
                    self.seePlayer = False
                    return rotation
                if intersectionPoint3 >= obstacle.getVertices()[1][0] and intersectionPoint3 <= obstacle.getVertices()[3][0] and not ((intersectionPoint3 <= self.position[0] and intersectionPoint3 <= playerPos[0]) or (intersectionPoint3 >= self.position[0] and intersectionPoint3 >= playerPos[0])):
                    self.seePlayer = False
                    return rotation
                if intersectionPoint4 >= obstacle.getVertices()[0][0] and intersectionPoint4 <= obstacle.getVertices()[2][0] and not ((intersectionPoint4 <= self.position[0] and intersectionPoint4 <= playerPos[0]) or (intersectionPoint4 >= self.position[0] and intersectionPoint4 >= playerPos[0])):
                    self.seePlayer = False
                    return rotation
                if not (self.rotation - rotation < -5.49779 or self.rotation - rotation > -0.785398):
                    self.seePlayer = False

            else:
                return 0
        return rotation


    # Getters
    def getPosition(self):
        return self.position

    def getRotation(self):
        return self.rotation

    def getHitbox(self):
        return self.hitbox

    def getBullets(self):
        return self.bullets

    def getShootCooldown(self):
        return self.shoot_cooldown

    def getWalkAmount(self):
        return self.walk_amount

    def getRotAmount(self):
        return self.rot_amount

    def getPrevPos(self):
        return self.prevPos

    def getSeePlayer(self):
        return self.seePlayer

    def getRotDir(self):
        return self.rot_dir

    # Setters
    def setPosition(self, position):
        self.position = position

    def setRotation(self, rotation):
        self.rotation = rotation

    def setShootCooldown(self, shoot_cooldown):
        self.shoot_cooldown = shoot_cooldown

    def setWalkAmount(self, walkAmount):
        self.walk_amount = walkAmount

    def setRotAmount(self, rotAmount):
        self.rot_amount = rotAmount

    def setHitbox(self, hitbox):
        self.hitbox = hitbox

    def setPrevPos(self, prevPos):
        self.prevPos = prevPos

    def setSeePlayer(self, seeEnemy):
        self.seeEnemy = seeEnemy

    def setRotDir(self, direction):
        self.rot_dir = direction


# Class for bullet
class Bullet:
    def __init__(self, position, rotation):
        # Init bullet variables
        self.position = position
        self.rotation = rotation
        self.hitbox = pygame.Rect(self.position, (2, 2))

    def draw(self, colour):  # Draw bullet
        pygame.draw.circle(window, colour, (self.position[0], self.position[1]), 4)

    def isCollision(self):  # Has the obstacle
        self.hitbox = pygame.Rect(self.position, (2, 2))
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle):
                return True
        return False

    # Getters
    def getPosition(self):
        return self.position

    def getRotation(self):
        return self.rotation

    def getHitbox(self):
        return self.hitbox

    # Setters
    def setPosition(self, position):
        self.position = position

    def setRotation(self, rotation):
        self.rotation = rotation


# Class for obstacles
class Obstacle:
    def __init__(self, vertex, width, height):
        # Initialise obstacle variables
        self.rect = pygame.Rect(vertex, (width, height))
        self.vertices = [vertex, [vertex[0], vertex[1] + height], [vertex[0] + width, vertex[1]], [vertex[0] + width, vertex[1] + height]] # 0---2
                                                                                                                                           # |   |
                                                                                                                                           # 1---3
    def drawObstacle(self):  # Draw an obstacle
        pygame.draw.rect(window, self.colour, self.rect)

    # Getters
    def getRect(self):
        return self.rect

    def getVertices(self):
        return self.vertices

    # Setters
    def setRect(self, rect):
        self.rect = rect

    def setVertices(self, vertices):
        self.vertices = vertices


# Player data
playerPos = [200, 50]
playerPrevPos = [1, 1]
playerRot = 0
playerPosChange = [0, 0]
playerRotChange = 0
timeScale = 1
timeDecrease = False
shootReady = 1
player_hitbox = pygame.Rect((400, 100), (20, 20))
player_gun_equipped = None
crosshair = pygame.image.load("Crosshair.png")
newCrosshair = crosshair
playerBullets = []
kills = 0

obstacles = []
global_bullets = []
enemies = [Enemy([400, 500]), Enemy([100, 400]), Enemy([700, 250])]
guns = [AR([100, 450]), Pistol([300, 50])]

map = Image.open("Map.png")

# Turn map image into obstacles
pix = map.load()
rect_status = False  # True = detecting a rect
rect_start = 0

for x in range(map.size[0]):
    for y in range(map.size[1]):
        if pix[x, y] == (0, 0, 0, 255) and not rect_status:
            rect_start = y
            rect_status = True
        elif pix[x, y] == (255, 255, 255, 255) and rect_status:
            obstacles.append(Obstacle(((x * (window.get_size()[0] / map.size[0])), (rect_start * (window.get_size()[1] / map.size[1]))), window.get_size()[0] / map.size[0], math.fabs(y - rect_start) * (window.get_size()[1] / map.size[1])))
            rect_status = False
        if y == map.size[1] - 1 and rect_status:
            obstacles.append(Obstacle(((x * (window.get_size()[0] / map.size[0])), (rect_start * (window.get_size()[1] / map.size[1]))),window.get_size()[0] / map.size[0], math.fabs((y - rect_start) + 1) * (window.get_size()[1] / map.size[1])))
            rect_status = False



wPressed = False
aPressed = False
sPressed = False
dPressed = False
prevMouse = False

def movePlayer(delta_time):
    global playerPos
    global playerPrevPos
    global timeScale
    global aPressed
    global wPressed
    global sPressed
    global dPressed
    global timeDecrease
    global player_hitbox
    playerPrevPos = copy.deepcopy(playerPos)
    if wPressed:  # Move player forward
        timeScale = 1
        playerPos[0] += math.sin(playerRot) * delta_time * 200
        playerPos[1] += math.cos(playerRot) * delta_time * 200
    if aPressed:  # Move player left
        playerPos[0] -= 200 * delta_time
        timeScale = 1
    if sPressed:  # Move player backwards
        playerPos[0] -= math.sin(playerRot) * delta_time * 200
        playerPos[1] -= math.cos(playerRot) * delta_time * 200
        timeScale = 1
    if dPressed:  # Move player right
        playerPos[0] += 200 * delta_time
        timeScale = 1
    if not (wPressed or aPressed or sPressed or dPressed):
        # If none of the WASD keys are pressed, slow time
        if timeDecrease and timeScale > 0.01:
            timeScale -= 0.06
        else:
            timeScale = 0.01
    player_hitbox = pygame.Rect((playerPos[0] - 10, playerPos[1] - 10), (20, 20))  # Updates player hitbox


def rotatePlayer():
    global playerPos
    global playerRot
    if pygame.mouse.get_pos()[1] - playerPos[1] > 0:
        playerRot = math.atan((pygame.mouse.get_pos()[0] - playerPos[0]) / (pygame.mouse.get_pos()[1] - playerPos[1]))
    elif pygame.mouse.get_pos()[1] - playerPos[1] < 0:
        playerRot = math.pi + math.atan(
            (pygame.mouse.get_pos()[0] - playerPos[0]) / (pygame.mouse.get_pos()[1] - playerPos[1]))

def playerShoot(delta_time):
    global player_gun_equipped
    global shootReady
    global timeScale
    global prevMouse
    global newCrosshair
    global global_bullets
    global kills

    if player_gun_equipped is not None:
        if shootReady <= player_gun_equipped.getFireRate():
            shootReady += 6 * timeScale * delta_time
        newCrosshair = pygame.transform.rotate(crosshair, (shootReady * 90) / player_gun_equipped.getFireRate())  # Rotate crosshair
        if pygame.mouse.get_pressed()[0] and not prevMouse and shootReady >= player_gun_equipped.getFireRate() and type(player_gun_equipped) == Pistol:
            # If mouse has been pressed, shoot one bullet and speed up time for a bit
            player_gun_equipped.shoot(playerPos, playerRot)
            playerBullets.append(global_bullets[-1])
        elif pygame.mouse.get_pressed()[0] and shootReady >= player_gun_equipped.getFireRate() and type(player_gun_equipped) == AR:
            # If mouse has been pressed, shoot one bullet and speed up time for a bit
            player_gun_equipped.shoot(playerPos, playerRot)
            playerBullets.append(global_bullets[-1])
    prevMouse = pygame.mouse.get_pressed()[0]

def updateBullet(bullet, delta_time):
    global colour_theme
    global playerPos
    global mode
    global playerBullets
    bullet.setPosition((bullet.getPosition()[0] + math.sin(bullet.rotation) * 1200 * timeScale * delta_time, bullet.getPosition()[1] + math.cos(bullet.rotation) * 1200 * timeScale * delta_time))  # Updates position of bullet
    if colour_theme == "Light":
        bullet.draw((0, 0, 0))  # Draws bullet
    else:
        bullet.draw((255, 255, 255))
    if player_hitbox.collidepoint(bullet.getPosition()[0], bullet.getPosition()[1]) and playerBullets.count(bullet) == 0:
        mode = 5
    if bullet.getPosition()[0] > window.get_size()[0] or bullet.getPosition()[0] < 0 or bullet.getPosition()[1] > window.get_size()[1] or bullet.getPosition()[1] < 0 or bullet.isCollision():  # Is the bullet outside of the screen or hit something?
        global_bullets.pop(global_bullets.index(bullet))  # If so, delete the bullet
        del bullet

def updateEnemy(enemy, delta_time):
    global timeScale
    global timeDecrease
    global kills

    enemy.setPrevPos(copy.deepcopy(enemy.getPosition()))
    # Randomise enemy movement
    if enemy.getWalkAmount() == 0 and random.randint(0, 100) == 0:
        enemy.setWalkAmount(random.randint(0, 200))
    if enemy.getWalkAmount() != 0:
        enemy.setPosition((enemy.getPosition()[0] + math.sin(enemy.getRotation()) * timeScale * delta_time * 200, enemy.getPosition()[1] + math.cos(enemy.getRotation()) * timeScale * delta_time * 200))
        enemy.setHitbox(pygame.Rect((enemy.getPosition()[0] - 10, enemy.getPosition()[1] - 10), (20, 20)))
        enemy.setWalkAmount(enemy.getWalkAmount() - 200 * timeScale * delta_time)
    if enemy.getRotAmount() > 0:
        enemy.setRotation(enemy.getRotation() + 0.1 * enemy.getRotDir() * timeScale * delta_time * 50)
        enemy.setRotAmount(enemy.getRotAmount() - 0.1 * timeScale * delta_time * 200)
    if enemy.getRotation() > 6.28 or enemy.getRotation() < 0:
        enemy.setRotation(0)
    # Detects if the enemy can see the player through obstacles
    rotation = enemy.canSeePlayer()
    if not enemy.getSeePlayer():
        if random.randint(0, 100) == 0:
            enemy.setRotAmount(random.randint(1, 6))
            if random.randint(1, 2) == 1:
                enemy.setRotDir(-1)
            else:
                enemy.setRotDir(1)
    else:
        enemy.setRotation(rotation)
        if random.randint(0, 50) == 0 and enemy.shoot_cooldown >= 5:  # Randomly shoots bullet
            timeDecrease = True
            enemy.shoot()
            enemy.setShootCooldown(0)
            if random.randint(1, 2) == 1:
                enemy.setRotDir(-1)
            else:
                enemy.setRotDir(1)

    if enemy.getPosition()[0] < 0 or enemy.getPosition()[0] > window.get_size()[0] or enemy.getPosition()[1] < 0 or enemy.getPosition()[1] > window.get_size()[1]:
        enemy.setPosition(enemy.getPrevPos())
        enemy.setRotAmount(6)
        enemy.setRotDir(1)

    enemy.setShootCooldown(enemy.getShootCooldown() + 20 * timeScale * delta_time)  # Updates enemy shoot cooldown
    enemy.draw()  # Draws enemy

    # Has the enemy been shot?
    for bullet in global_bullets:
        if enemy.hitbox.colliderect(bullet.hitbox) and enemy.bullets.count(bullet) == 0:
            enemies.pop(enemies.index(enemy))
            global_bullets.pop(global_bullets.index(bullet))
            kills += 1

def updateGun(gun):
    global playerPos
    global player_gun_equipped

    # Is the player close enough to a gun to pick it up?
    if math.sqrt((playerPos[0] - gun.getPosition()[0] - gun.getSize() / 2) ** 2 + (
            playerPos[1] - gun.getPosition()[1] - gun.getSize() / 2) ** 2) < 30 and player_gun_equipped is None:
        player_gun_equipped = gun
        guns.pop(guns.index(gun))
    window.blit(gun.getImage(), (gun.getPosition()[0], gun.getPosition()[1]))  # Draw gun

couriernew_big = pygame.font.SysFont('couriernew', 40)
couriernew_small = pygame.font.SysFont('couriernew', 25)

mode = 0

mode_selection = 0
running = True
while running:
    # Menu loop
    def menuLoop():
        # Text for UI
        play_text = couriernew_big.render('Play', False, (255, 255, 255))
        setting_text = couriernew_big.render('Settings', False, (255, 255, 255))
        exit_text = couriernew_big.render('Exit', False, (255, 255, 255))
        version_text = couriernew_small.render('V0.0.5', False, (255, 255, 255))
        enter_text = couriernew_small.render("Press 'enter' to select", False, (255, 255, 255))
        title_text = pygame.font.SysFont('couriernew', 60).render("SUPERHOT.exe", False, (255, 255, 255))
        dir_text1 = couriernew_small.render("C:\\SUPERHOT\\Main\\", False, (255, 255, 255))
        menu_running = True
        while menu_running:
            window.fill((0, 0, 0))
            eventHandler()  # Handle events
            # Mode selection
            if mode != 0:
                return
            pygame.draw.polygon(window, (255, 255, 255), ((100, 100), (100, 700), (1180, 700), (1180, 100)))
            pygame.draw.polygon(window, (0, 0, 0), ((105, 105), (105, 695), (1175, 695), (1175, 105)))
            if mode_selection == 0:
                pygame.draw.polygon(window, (150, 0, 0), ((105, 155), (105, 195), (1175, 195), (1175, 155)))
                window.blit(enter_text, (800, 163))
                dir_text2 = couriernew_small.render("Play.exe\\", False, (150, 150, 150))
                window.blit(dir_text2, (365, 660))
            elif mode_selection == 1:
                pygame.draw.polygon(window, (150, 0, 0), ((105, 200), (105, 242), (1175, 242), (1175, 200)))
                window.blit(enter_text, (800, 209))
                dir_text2 = couriernew_small.render("Settings\\", False, (150, 150, 150))
                window.blit(dir_text2, (365, 660))
            else:
                pygame.draw.polygon(window, (150, 0, 0), ((105, 250), (105, 290), (1175, 290), (1175, 250)))
                window.blit(enter_text, (800, 257))
                dir_text2 = couriernew_small.render("Exit.exe\\", False, (150, 150, 150))
                window.blit(dir_text2, (365, 660))

            # Drawing to window
            pygame.draw.polygon(window, (0, 0, 0), ((400, 100), (400, 105), (880, 105), (880, 100)))
            window.blit(play_text, (150, 150))
            window.blit(setting_text, (150, 200))
            window.blit(exit_text, (150, 250))
            window.blit(version_text, (1080, 660))
            window.blit(title_text, (425, 69))
            window.blit(dir_text1, (110, 660))

            pygame.display.update()

    if mode == 0:
        menuLoop()

    def settingsLoop():
        settings_running = True
        global mode_selection
        global volume
        mode_selection = 0
        arrows_text = couriernew_small.render("Press '<' or '>' to adjust", False, (255, 255, 255))
        title_text = pygame.font.SysFont('couriernew', 60).render("SUPERHOT.exe", False, (255, 255, 255))
        exit_text = couriernew_big.render('Back', False, (255, 255, 255))
        enter_text = couriernew_small.render("Press 'enter' to select", False, (255, 255, 255))
        while settings_running:
            window.fill((0, 0, 0))
            eventHandler()  # Handle events
            sound_text = couriernew_big.render('Sound <' + str(volume) + '>', False, (255, 255, 255))
            theme_text = couriernew_big.render('Theme <' + colour_theme + '>', False, (255, 255, 255))
            # Mode selection
            if mode != 4:
                return
            pygame.draw.polygon(window, (255, 255, 255), ((100, 100), (100, 700), (1180, 700), (1180, 100)))
            pygame.draw.polygon(window, (0, 0, 0), ((105, 105), (105, 695), (1175, 695), (1175, 105)))
            if mode_selection == 0:
                pygame.draw.polygon(window, (150, 0, 0), ((105, 155), (105, 195), (1175, 195), (1175, 155)))
                window.blit(arrows_text, (760, 163))
                dir_text2 = couriernew_small.render("Sound\\", False, (150, 150, 150))
                dir_text1 = couriernew_small.render("C:\\SUPERHOT\\Main\\Settings\\", False, (255, 255, 255))
                window.blit(dir_text2, (500, 660))
            elif mode_selection == 1:
                pygame.draw.polygon(window, (150, 0, 0), ((105, 200), (105, 242), (1175, 242), (1175, 200)))
                window.blit(arrows_text, (760, 209))
                dir_text2 = couriernew_small.render("Mouse Sensitivity\\", False, (150, 150, 150))
                dir_text1 = couriernew_small.render("C:\\SUPERHOT\\Main\\Settings\\", False, (255, 255, 255))
                window.blit(dir_text2, (500, 660))
            else:
                pygame.draw.polygon(window, (150, 0, 0), ((105, 250), (105, 290), (1175, 290), (1175, 250)))
                window.blit(enter_text, (800, 257))
                dir_text1 = couriernew_small.render("C:\\SUPERHOT\\Main\\", False, (255, 255, 255))

            pygame.draw.polygon(window, (0, 0, 0), ((400, 100), (400, 105), (880, 105), (880, 100)))
            window.blit(sound_text, (150, 150))
            window.blit(theme_text, (150, 200))
            window.blit(exit_text, (150, 250))
            window.blit(title_text, (425, 69))
            window.blit(dir_text1, (110, 660))

            pygame.display.update()

    if mode == 4:
        settingsLoop()

    def deathLoop():
        global mode_selection
        global mode
        death_running = True
        mode_selection = 0
        title_text = pygame.font.SysFont('couriernew', 60).render("You Died", False, (255, 255, 255))
        exit_text = couriernew_big.render('Exit', False, (255, 255, 255))
        enter_text = couriernew_small.render("Press 'enter' to select", False, (255, 255, 255))
        while death_running:
            window.fill((0, 0, 0))
            eventHandler()  # Handle events
            replay_text = couriernew_big.render('Replay', False, (255, 255, 255))
            main_text = couriernew_big.render('Main', False, (255, 255, 255))
            # Mode selection
            if mode != 5:
                return
            pygame.draw.polygon(window, (255, 255, 255), ((100, 100), (100, 700), (1180, 700), (1180, 100)))
            pygame.draw.polygon(window, (0, 0, 0), ((105, 105), (105, 695), (1175, 695), (1175, 105)))
            if mode_selection == 0:
                pygame.draw.polygon(window, (150, 0, 0), ((105, 155), (105, 195), (1175, 195), (1175, 155)))
                window.blit(enter_text, (760, 163))
                dir_text2 = couriernew_small.render("Replay.exe\\", False, (150, 150, 150))
                dir_text1 = couriernew_small.render("C:\\SUPERHOT\\Main\\Settings\\", False, (255, 255, 255))
                window.blit(dir_text2, (500, 660))
            elif mode_selection == 1:
                pygame.draw.polygon(window, (150, 0, 0), ((105, 200), (105, 242), (1175, 242), (1175, 200)))
                window.blit(enter_text, (760, 209))
                dir_text2 = couriernew_small.render("", False, (150, 150, 150))
                dir_text1 = couriernew_small.render("C:\\SUPERHOT\\Main\\", False, (255, 255, 255))
                window.blit(dir_text2, (500, 660))
            else:
                pygame.draw.polygon(window, (150, 0, 0), ((105, 250), (105, 290), (1175, 290), (1175, 250)))
                window.blit(enter_text, (800, 257))
                dir_text2 = couriernew_small.render("Exit.exe\\", False, (150, 150, 150))
                dir_text1 = couriernew_small.render("C:\\SUPERHOT\\Main\\Settings\\", False, (255, 255, 255))
                window.blit(dir_text2, (500, 660))

            pygame.draw.polygon(window, (0, 0, 0), ((460, 100), (460, 105), (820, 105), (820, 100)))
            window.blit(replay_text, (150, 150))
            window.blit(main_text, (150, 200))
            window.blit(exit_text, (150, 250))
            window.blit(title_text, (490, 69))
            window.blit(dir_text1, (110, 660))

            pygame.display.update()

    if mode == 5:
        deathLoop()

    # Game loop
    def playLoop():
        global playerPos
        global timeDecrease
        global timeScale
        global player_gun_equipped
        global playerRot
        global player_hitbox
        global playerPrevPos
        global playerPosChange
        global playerRotChange
        global shootReady
        global newCrosshair
        global kills

        start_time = time.time()

        play_running = True
        delta_time = 0
        prev_time = time.time()
        while play_running:
            delta_time = time.time() - prev_time
            prev_time = time.time()

            if mode != 1:
                return
            if colour_theme == "Light":
                window.fill((230, 230, 230))
            else:
                window.fill((0, 0, 0))

            if random.randint(0, 2000) == 0 or len(enemies) == 0:
                for i in range(random.randint(0, 2)):
                    enemies.append(Enemy((random.randint(50, 1230), random.randint(50, 750))))
                    for obstacle in obstacles:
                        if obstacle.getRect().colliderect(enemies[-1].getHitbox()):
                            enemies.pop(-1)
                            break

            eventHandler()  # Handle events
            newCrosshair = crosshair

            movePlayer(delta_time)  # Moves player according to the keys that are pressed
            rotatePlayer()  # Rotates player according to mouse position
            playerShoot(delta_time)  # Shoots bullet from player if appropriate

            # Loop through all bullets and update their position and status
            for bullet in global_bullets:
                updateBullet(bullet, delta_time)

            # Loops through all obstacles, draws them and detects if the player has bumped into one
            for obstacle in obstacles:
                # Draws obstacle
                if colour_theme == "Light":
                    pygame.draw.rect(window, (0, 0, 0), obstacle)
                else:
                    pygame.draw.rect(window, (255, 255, 255), obstacle)
                if player_hitbox.colliderect(obstacle):
                    playerPos = playerPrevPos  # Stops player from moving if it has collided with an obstacle

                for enemy in enemies:
                    if obstacle.getRect().colliderect(enemy.getHitbox()):
                        enemy.setPosition(enemy.getPrevPos())
                        enemy.setRotAmount(random.randint(0, 6))
                        enemy.setRotDir(1)
                for gun_index in range(len(guns)):
                    if obstacle.getRect().collidepoint(guns[gun_index].getPosition()):
                        guns.pop(gun_index)

            if random.randint(0, 4000) == 0:
                guns.append(Pistol((random.randint(50, 1230), random.randint(50, 750))))
            if random.randint(0, 4000) == 0:
                guns.append(AR((random.randint(50, 1230), random.randint(50, 750))))

            if playerPos[0] < 0 or playerPos[0] > window.get_size() [0] or playerPos[1] < 0 or playerPos[1] > window.get_size()[1]:
                playerPos = playerPrevPos

            # Iterate through and update all the enemies
            for enemy in enemies:
                updateEnemy(enemy, delta_time)
            # Iterate through all guns
            for gun in guns:
                updateGun(gun)

            if player_gun_equipped is not None:
                if player_gun_equipped.getAmmo() >= 3:
                    window.blit(bullet_image_gold, (1170, 750))
                    window.blit(bullet_image_gold, (1190, 750))
                    window.blit(bullet_image_gold, (1210, 750))
                if player_gun_equipped.getAmmo() == 2:
                    window.blit(bullet_image_gold, (1170, 750))
                    window.blit(bullet_image_gold, (1190, 750))
                    window.blit(bullet_image_black, (1210, 750))
                if player_gun_equipped.getAmmo() == 1:
                    window.blit(bullet_image_gold, (1170, 750))
                    window.blit(bullet_image_black, (1190, 750))
                    window.blit(bullet_image_black, (1210, 750))
                if player_gun_equipped.getAmmo() == 0:
                    window.blit(bullet_image_black, (1170, 750))
                    window.blit(bullet_image_black, (1190, 750))
                    window.blit(bullet_image_black, (1210, 750))
                ammo_text = menlo.render(str(player_gun_equipped.getAmmo()), False, (0, 0, 0))
                time_alive_text = menlo.render("Time Alive: " + str(round(time.time() - start_time, 2)), False, (0, 0, 0))
                kills_text = menlo.render("Kills: " + str(kills), False, (0, 0, 0))
                window.blit(ammo_text, (1240, 750))
                window.blit(time_alive_text, (850, 0))
                window.blit(kills_text, (995, 30))
            if colour_theme == "Light":
                pygame.draw.circle(window, (0, 0, 0), (playerPos[0], playerPos[1]), 20)  # Draw player
                pygame.draw.circle(window, (255, 255, 255), (14 * math.sin(playerRot) + playerPos[0], 14 * math.cos(playerRot) + playerPos[1]), 2)
            else:
                pygame.draw.circle(window, (255, 255, 255), (playerPos[0], playerPos[1]), 20)  # Draw player
                pygame.draw.circle(window, (0, 0, 0), (14 * math.sin(playerRot) + playerPos[0], 14 * math.cos(playerRot) + playerPos[1]), 2)
            window.blit(newCrosshair, (pygame.mouse.get_pos()[0] - crosshair.get_size()[0] / 2, pygame.mouse.get_pos()[1] - crosshair.get_size()[1] / 2))  # Draw crosshair
            pygame.display.update()

    if mode == 1:
        playLoop()
