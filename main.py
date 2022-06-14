import pygame
import math
import copy
import random

# Initialise pygame
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('menlo', 30)

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)

bullet_image_gold = pygame.image.load("Bullet Gold.png")
bullet_image_black = pygame.image.load("Bullet Black.png")

# Handle any events
def eventHandler():
    global running
    global wPressed
    global aPressed
    global sPressed
    global dPressed
    global player_gun_equipped
    global guns
    global playerPos
    global playerRot
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Has pygame been quit?
            running = False
        if event.type == pygame.KEYDOWN:  # Has a key been pressed?
            if event.key == pygame.K_ESCAPE:
                running = False
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
        self.size = 25
        self.image = pygame.image.load("Pistol.png")
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.fire_rate = 2
        self.ammo = 20
        self.max_ammo = 20

# Class for AR(inherited from Gun class)
class AR(Gun):
    def __init__(self, position):
        self.position = position
        self.size = 75
        self.image = pygame.image.load("AR.png")
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.fire_rate = 1
        self.ammo = 10
        self.max_ammo = 10

# Class for enemy
class Enemy:
    def __init__(self, position):
        # initialise variables for enemy
        self.shoot_cooldown = 0
        self.position = position
        self.rotation = 0
        self.hitbox = pygame.Rect((position[0] - 10, position[1] - 10), (20, 20))
        self.bullets = []
        self.walk_amount = 0
        self.rot_amount = 0
        self.rot_dir = 1
        self.prevPos = []
        self.seePlayer = False
    def shoot(self): # Enemy shoot method
        global_bullets.append(Bullet(copy.deepcopy(self.position), self.rotation))
        self.bullets.append(global_bullets[-1])

    def draw(self):  # Draw enemy
        pygame.draw.circle(window, (200, 0, 0), (self.position[0], self.position[1]), 15)
        pygame.draw.circle(window, (0, 0, 0),
                           (14 * math.sin(self.rotation) + self.position[0], 14 * math.cos(self.rotation) + self.position[1]), 2)
    
    def canSeePlayer(self, obstacle): # Can the enemy see the player?
        self.seePlayer = True
        if self.position[0] - playerPos[0] != 0:
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


# Class for bullet
class Bullet:
    def __init__(self, position, rotation):
        # Init bullet variables
        self.position = position
        self.rotation = rotation
        self.hitbox = pygame.Rect(self.position, (2, 2))

    def draw(self):  # Draw bullet
        pygame.draw.circle(window, (0, 0, 0), (self.position[0], self.position[1]), 4)

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
        self.rect = pygame.Rect((vertex), (width, height))
        self.colour = (0, 0, 0)
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
playerPos = [800, 501]
playerPrevPos = [400, 100]
playerRot = 0
playerPosChange = [0, 0]
playerRotChange = 0
timeScale = 1
timeDecrease = False
shootReady = 1
player_hitbox = pygame.Rect((400, 100), (15, 15))
player_gun_equipped = None
crosshair = pygame.image.load("pixil-frame-0 (2).png")

obstacles = [Obstacle((500, 500), 100, 100)]
global_bullets = []
enemies = [Enemy([400, 500])]
guns = [AR([100, 100]), Pistol([0, 0])]

wPressed = False
aPressed = False
sPressed = False
dPressed = False
prevMouse = False

running = True
while running:
    window.fill((230, 230, 230))
    eventHandler()  # Handle events

    newCrosshair = crosshair

    # Move player
    playerPrevPos = copy.deepcopy(playerPos)
    if wPressed:  # Move player forward
        timeScale = 1
        playerPos[0] += math.sin(playerRot)
        playerPos[1] += math.cos(playerRot)
    if aPressed:  # Move player left
        playerPos[0] -= 1
        timeScale = 1
    if sPressed:  # Move player backwards
        playerPos[0] -= math.sin(playerRot)
        playerPos[1] -= math.cos(playerRot)
        timeScale = 1
    if dPressed:  # Move player right
        playerPos[0] += 1
        timeScale = 1
    if not (wPressed or aPressed or sPressed or dPressed):
        # If none of the WASD keys are pressed, slow time
        if timeDecrease and timeScale > 0.01:
            timeScale -= 0.06
        else:
            timeScale = 0.01

    # Rotate player
    if pygame.mouse.get_pos()[1] - playerPos[1] > 0:
        playerRot = math.atan((pygame.mouse.get_pos()[0] - playerPos[0]) / (pygame.mouse.get_pos()[1] - playerPos[1]))
    elif pygame.mouse.get_pos()[1] - playerPos[1] < 0:
        playerRot = math.pi + math.atan((pygame.mouse.get_pos()[0] - playerPos[0]) / (pygame.mouse.get_pos()[1] - playerPos[1]))

    player_hitbox = pygame.Rect((playerPos[0] - 10, playerPos[1] - 10), (20, 20))  # Updates player hitbox
    if player_gun_equipped is not None:
        if shootReady <= player_gun_equipped.getFireRate():
            shootReady += 0.03 * timeScale
        newCrosshair = pygame.transform.rotate(crosshair, (shootReady * 90) / player_gun_equipped.getFireRate())  # Rotate crosshair
        if pygame.mouse.get_pressed()[0] and not prevMouse and shootReady >= player_gun_equipped.getFireRate() and type(player_gun_equipped) == Pistol:
            # If mouse has been pressed, shoot one bullet and speed up time for a bit
            player_gun_equipped.shoot(playerPos, playerRot)
        elif pygame.mouse.get_pressed()[0] and shootReady >= player_gun_equipped.getFireRate() and type(player_gun_equipped) == AR:
            # If mouse has been pressed, shoot one bullet and speed up time for a bit
            player_gun_equipped.shoot(playerPos, playerRot)
    prevMouse = pygame.mouse.get_pressed()[0]

    for bullet in global_bullets:
        bullet.setPosition((bullet.getPosition()[0] + math.sin(bullet.rotation) * 10 * timeScale, bullet.getPosition()[1] + math.cos(bullet.rotation) * 10 * timeScale))  # Updates position of bullet
        bullet.draw()  # Draws bullet
        if bullet.getPosition()[0] > window.get_size()[0] or bullet.getPosition()[0] < 0 or bullet.getPosition()[1] > \
                window.get_size()[1] or bullet.getPosition()[1] < 0 or bullet.isCollision():  # Is the bullet outside of the screen or hit something?
            global_bullets.pop(global_bullets.index(bullet))  # If so, delete the bullet
            del bullet

    for obstacle in obstacles:
        pygame.draw.rect(window, (0, 0, 0), obstacle)  # Draws obstacle
        if player_hitbox.colliderect(obstacle):
            playerPos = playerPrevPos  # Stops player from moving if it has collided with an obstacle

    for enemy in enemies:
        enemy.setPrevPos(copy.deepcopy(enemy.getPosition()))
        # Randomise enemy movement
        if enemy.getWalkAmount() == 0 and random.randint(0, 100) == 0:
            enemy.setWalkAmount(random.randint(0, 200))
        if enemy.getWalkAmount() != 0:
            enemy.setPosition((enemy.getPosition()[0] + math.sin(enemy.getRotation()) * timeScale, enemy.getPosition()[1] + math.cos(enemy.getRotation()) * timeScale))
            enemy.setHitbox(pygame.Rect((enemy.getPosition()[0] - 10, enemy.getPosition()[1] - 10), (20, 20)))
            enemy.setWalkAmount(enemy.getWalkAmount() - 1 * timeScale)
        if enemy.getRotAmount() > 0:
            enemy.setRotation((enemy.getRotation() + 0.01) * timeScale)
            enemy.setRotAmount((enemy.getRotAmount() - 0.1) * timeScale)
        if enemy.getRotation() > 6.28 or enemy.getRotation() < 0:
            enemy.setRotation(0)
        # Detects if the enemy can see the player through obstacles
        for obstacle in obstacles:
            if obstacle.getRect().colliderect(enemy.getHitbox()) or window.get_size()[0] < enemy.getPosition()[0] or enemy.getPosition()[0] < 0 or window.get_size()[1] < enemy.getPosition()[1] or enemy.getPosition()[1] < 0:
                enemy.setPosition(enemy.getPrevPos())
                enemy.setRotAmount(random.randint(0, 3))
            rotation = enemy.canSeePlayer(obstacle)
            if not enemy.getSeePlayer():
                if random.randint(0, 100) == 0:
                    enemy.setRotAmount(random.randint(0, 3))
            else:
                enemy.setRotAmount(0)
                enemy.setRotation(rotation)
                if random.randint(0, 50) == 0 and enemy.shoot_cooldown >= 1:  # Randomly shoots bullet
                    timeDecrease = True
                    enemy.shoot()
                    enemy.setShootCooldown(0)
        enemy.setShootCooldown(enemy.getShootCooldown() + 0.1 * timeScale)  # Updates enemy shoot cooldown
        enemy.draw()  # Draws enemy

        # Has the enemy been shot?
        for bullet in global_bullets:
            if enemy.hitbox.colliderect(bullet.hitbox) and enemy.bullets.count(bullet) == 0:
                enemies.pop(enemies.index(enemy))
                global_bullets.pop(global_bullets.index(bullet))
    # Iterate through all guns
    for gun in guns:
        # Is the player close enough to a gun to pick it up?
        if math.sqrt((playerPos[0] - gun.getPosition()[0] - gun.getSize() / 2) ** 2 + (playerPos[1] - gun.getPosition()[1] - gun.getSize() / 2) ** 2) < 30 and player_gun_equipped is None:
            player_gun_equipped = gun
            guns.pop(guns.index(gun))
        window.blit(gun.getImage(), (gun.getPosition()[0], gun.getPosition()[1]))  # Draw gun
    if player_gun_equipped is not None:
        if player_gun_equipped.getAmmo() >= 3:
            window.blit(bullet_image_gold, (10, 750))
            window.blit(bullet_image_gold, (30, 750))
            window.blit(bullet_image_gold, (50, 750))
        if player_gun_equipped.getAmmo() == 2:
            window.blit(bullet_image_gold, (10, 750))
            window.blit(bullet_image_gold, (30, 750))
            window.blit(bullet_image_black, (50, 750))
        if player_gun_equipped.getAmmo() == 1:
            window.blit(bullet_image_gold, (10, 750))
            window.blit(bullet_image_black, (30, 750))
            window.blit(bullet_image_black, (50, 750))
        if player_gun_equipped.getAmmo() == 0:
            window.blit(bullet_image_black, (10, 750))
            window.blit(bullet_image_black, (30, 750))
            window.blit(bullet_image_black, (50, 750))
        ammo_text = font.render(str(player_gun_equipped.getAmmo()), False, (0, 0, 0))
        window.blit(ammo_text, (90, 750))
    pygame.draw.circle(window, (0, 0, 0), (playerPos[0], playerPos[1]), 15)  # Draw player
    pygame.draw.circle(window, (255, 255, 255), (14 * math.sin(playerRot) + playerPos[0], 14 * math.cos(playerRot) + playerPos[1]), 2)
    window.blit(newCrosshair, (pygame.mouse.get_pos()[0] - crosshair.get_size()[0] / 2, pygame.mouse.get_pos()[1] - crosshair.get_size()[1] / 2))  # Draw crosshair
    pygame.display.update()
