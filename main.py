import pygame
import math
import copy
import random

# Initialise pygame
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 30)

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)


# Handle any events
def eventHandler():
    global running
    global wPressed
    global aPressed
    global sPressed
    global dPressed
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
        if event.type == pygame.KEYUP:  # Has a key been lifted?
            if event.key == pygame.K_w:
                wPressed = False
            if event.key == pygame.K_a:
                aPressed = False
            if event.key == pygame.K_s:
                sPressed = False
            if event.key == pygame.K_d:
                dPressed = False

# Class for enemy
class Enemy:
    def __init__(self, position):
        self.shoot_cooldown = 0
        self.position = position
        self.rotation = 180
        self.hitbox = pygame.Rect((position[0] - 10, position[1] - 10), (20, 20))
        self.bullets = []
        self.walk_amount = 0
        self.rot_amount = 0
        self.prevPos = []
        self.seeEnemy = False
    def shoot(self):
        global_bullets.append(Bullet(copy.deepcopy(self.position), self.rotation))
        self.bullets.append(global_bullets[-1])

    def draw(self):
        pygame.draw.circle(window, (200, 0, 0), (self.position[0], self.position[1]), 15)
        pygame.draw.circle(window, (0, 0, 0),
                           (14 * math.sin(self.rotation) + self.position[0], 14 * math.cos(self.rotation) + self.position[1]), 2)

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

    def getSeeEnemy(self):
        return self.seeEnemy

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

    def setSeeEnemy(self, seeEnemy):
        self.seeEnemy = seeEnemy

# Class for bullet
class Bullet:
    def __init__(self, position, rotation):
        self.position = position
        self.rotation = rotation
        self.hitbox = pygame.Rect(self.position, (2, 2))

    def draw(self):
        pygame.draw.circle(window, (0, 0, 0), (self.position[0], self.position[1]), 4)

    def isCollision(self):
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
crosshair = pygame.image.load("pixil-frame-0 (2).png")

obstacles = [Obstacle((500, 500), 100, 100)]
global_bullets = []
enemies = [Enemy([400, 500])]

wPressed = False
aPressed = False
sPressed = False
dPressed = False
prevMouse = False

running = True
while running:
    window.fill((230, 230, 230))
    eventHandler()  # Handle events

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
        playerRot = math.pi + math.atan(
            (pygame.mouse.get_pos()[0] - playerPos[0]) / (pygame.mouse.get_pos()[1] - playerPos[1]))

    player_hitbox = pygame.Rect((playerPos[0] - 10, playerPos[1] - 10), (20, 20))  # Updates player hitbox

    if pygame.mouse.get_pressed()[0] and not prevMouse and shootReady >= 1:
        # If mouse has been pressed, shoot one bullet and speed up time for a bit
        global_bullets.append(Bullet(copy.deepcopy(playerPos), copy.deepcopy(playerRot)))
        timeDecrease = True
        timeScale = 1
        shootReady = 0
    prevMouse = pygame.mouse.get_pressed()[0]

    for bullet in global_bullets:
        bullet.setPosition((bullet.getPosition()[0] + math.sin(bullet.rotation) * 10 * timeScale, bullet.getPosition()[1] + math.cos(bullet.rotation) * 10 * timeScale))  # Updates position of bullet
        bullet.draw()  # Draws bullet
        if bullet.getPosition()[0] > window.get_size()[0] or bullet.getPosition()[0] < 0 or bullet.getPosition()[1] > \
                window.get_size()[1] or bullet.getPosition()[1] < 0 or bullet.isCollision():  # Is the bullet outside of the screen or hit something?
            global_bullets.pop(global_bullets.index(bullet))  # If so, delete the bullet
            del bullet
    if shootReady < 1:
        shootReady += 0.03 * timeScale

    for obstacle in obstacles:
        pygame.draw.rect(window, (0, 0, 0), obstacle)  # Draws obstacle
        if player_hitbox.colliderect(obstacle):
            playerPos = playerPrevPos  # Stops player from moving if it has collided with an obstacle

    for enemy in enemies:
        enemy.setPrevPos(copy.deepcopy(enemy.getPosition()))
        if enemy.getWalkAmount() == 0 and random.randint(0, 100) == 0:
            enemy.setWalkAmount(random.randint(0, 200))
        if enemy.getWalkAmount() != 0:
            #enemy.setPosition((enemy.getPosition()[0] + math.sin(enemy.getRotation()) * timeScale, enemy.getPosition()[1] + math.cos(enemy.getRotation()) * timeScale))
            enemy.setHitbox(pygame.Rect((enemy.getPosition()[0] - 10, enemy.getPosition()[1] - 10), (20, 20)))
            enemy.setWalkAmount(enemy.getWalkAmount() - 1 * timeScale)
        for obstacle in obstacles:
            if obstacle.getRect().colliderect(enemy.getHitbox()) or window.get_size()[0] < enemy.getPosition()[0] or enemy.getPosition()[0] < 0 or window.get_size()[1] < enemy.getPosition()[1] or enemy.getPosition()[1] < 0:
                enemy.setPosition(enemy.getPrevPos())
            pygame.draw.line(window, (0, 0, 0), enemy.getPosition(), playerPos)
            enemy.setSeeEnemy(True)
            if enemy.getPosition()[0] - playerPos[0] != 0:
                lineGradient = (enemy.getPosition()[1] - playerPos[1]) / (enemy.getPosition()[0] - playerPos[0])
                lineC = enemy.getPosition()[1] - (enemy.getPosition()[0] * lineGradient)
                intersectionPoint1 = obstacle.getVertices()[0][0] * lineGradient + lineC
                intersectionPoint2 = obstacle.getVertices()[2][0] * lineGradient + lineC
                intersectionPoint3 = (obstacle.getVertices()[1][1] - lineC) / lineGradient
                intersectionPoint4 = (obstacle.getVertices()[0][1] - lineC) / lineGradient
                if playerPos[0] >= enemy.getPosition()[0]:
                    rotation = 1.57 - math.atan(lineGradient)
                else:
                    rotation = 4.71 - math.atan(lineGradient)
                if intersectionPoint1 >= obstacle.getVertices()[0][1] and intersectionPoint1 <= obstacle.getVertices()[1][1] and not ((intersectionPoint1 <= enemy.getPosition()[1] and intersectionPoint1 <= playerPos[1]) or (intersectionPoint1 >= enemy.getPosition()[1] and intersectionPoint1 >= playerPos[1])):
                    pygame.draw.circle(window, (255, 0, 0), (obstacle.getVertices()[0][0], intersectionPoint1), 5)
                    enemy.setSeeEnemy(False)
                if intersectionPoint2 >= obstacle.getVertices()[2][1] and intersectionPoint2 <= obstacle.getVertices()[3][1] and not ((intersectionPoint2 <= enemy.getPosition()[1] and intersectionPoint2 <= playerPos[1]) or (intersectionPoint2 >= enemy.getPosition()[1] and intersectionPoint2 >= playerPos[1])):
                    pygame.draw.circle(window, (255, 0, 0), (obstacle.getVertices()[2][0], intersectionPoint2), 5)
                    enemy.setSeeEnemy(False)
                if intersectionPoint3 >= obstacle.getVertices()[1][0] and intersectionPoint3 <= obstacle.getVertices()[3][0] and not ((intersectionPoint3 <= enemy.getPosition()[0] and intersectionPoint3 <= playerPos[0]) or (intersectionPoint3 >= enemy.getPosition()[0] and intersectionPoint3 >= playerPos[0])):
                    pygame.draw.circle(window, (255, 0, 0), (intersectionPoint3, obstacle.getVertices()[1][1]), 5)
                    enemy.setSeeEnemy(False)
                if intersectionPoint4 >= obstacle.getVertices()[0][0] and intersectionPoint4 <= obstacle.getVertices()[2][0] and not ((intersectionPoint4 <= enemy.getPosition()[0] and intersectionPoint4 <= playerPos[0]) or (intersectionPoint4 >= enemy.getPosition()[0] and intersectionPoint4 >= playerPos[0])):
                    pygame.draw.circle(window, (255, 0, 0), (intersectionPoint4, obstacle.getVertices()[0][1]), 5)
                    enemy.setSeeEnemy(False)
                if not (enemy.getRotation() - rotation < -5.49779 or enemy.getRotation() - rotation > -0.785398):
                    enemy.setSeeEnemy(False)
                if not enemy.getSeeEnemy():
                    enemy.setRotation(0)
                elif enemy.getPosition()[0] - playerPos[0] >= 0:
                    enemy.setRotation(4.71 - math.atan(lineGradient))
                else:
                    enemy.setRotation(1.57 - math.atan(lineGradient))
        enemy.setShootCooldown(enemy.getShootCooldown() + 0.1 * timeScale)  # Updates enemy shoot cooldown
        enemy.draw()  # Draws enemy

        if random.randint(0, 100) == 0 and enemy.shoot_cooldown >= 1:  # Randomly shoots bullet
            timeDecrease = True
            enemy.shoot()
            enemy.setShootCooldown(0)
        # Has the enemy been shot?
        for bullet in global_bullets:
            if enemy.hitbox.colliderect(bullet.hitbox) and enemy.bullets.count(bullet) == 0:
                enemies.pop(enemies.index(enemy))
                global_bullets.pop(global_bullets.index(bullet))

    newCrosshair = pygame.transform.rotate(crosshair, shootReady * 90)  # Rotate crosshair
    pygame.draw.circle(window, (0, 0, 0), (playerPos[0], playerPos[1]), 15)  # Draw player
    pygame.draw.circle(window, (255, 255, 255),
                       (14 * math.sin(playerRot) + playerPos[0], 14 * math.cos(playerRot) + playerPos[1]), 2)
    window.blit(newCrosshair, (pygame.mouse.get_pos()[0] - crosshair.get_size()[0] / 2, pygame.mouse.get_pos()[1] - crosshair.get_size()[1] / 2))  # Draw crosshair

    pygame.display.update()
