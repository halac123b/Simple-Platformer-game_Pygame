import pygame
import pickle
from os import path
from pygame import mixer

# Init pygame engine
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
TILE_SIZE = 30
FPS = 60
clock = pygame.time.Clock()

# Define game variables
isRunning = True
isGameOver = 0
isMainMenu = True
# Level hiện tại và level tối đa của game
level = 0
maxLevel = 7
# Score nhận được khi nhặt xu
score = 0

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer")

# Define font
font = pygame.font.SysFont('Bauhaus 93', 70)
fontScore = pygame.font.SysFont('Bauhaus 93', 30)

# Define colors
white = (255, 255, 255)
blue = (0, 0, 255)

# Load images
sunImg = pygame.image.load("img/sun.png")
backgroundImg = pygame.image.load("img/sky.png")
grassImg = pygame.image.load("img/grass.png")
restartImg = pygame.image.load("img/restart_btn.png")
startImg = pygame.image.load("img/start_btn.png")
exitImg = pygame.image.load("img/exit_btn.png")

# Load sounds
pygame.mixer.music.load('img/music.wav')    # Background music
pygame.mixer.music.play(-1, 0.0, 5000)

coinFx = pygame.mixer.Sound('img/coin.wav')
coinFx.set_volume(0.5)
jumpFx = pygame.mixer.Sound('img/jump.wav')
jumpFx.set_volume(0.5)
gameOverFx = pygame.mixer.Sound('img/game_over.wav')
gameOverFx.set_volume(0.5)

# Draw text on screen in game
def drawText(text, font, textColor, x, y):
    img = font.render(text, True, textColor)
    screen.blit(img, (x, y))

# Function to load game levels
def resetLevel(level):
    player.reset(100, SCREEN_HEIGHT - 100)
    enemyGroup.empty()
    lavaGroup.empty()
    exitGroup.empty()
    platformGroup.empty()

    if path.exists(f"./level{level}_data"):
        # Load level data from file and create world
        pickleInput = open(f"./level{level}_data", "rb")
        worldData = pickle.load(pickleInput)

    world = World(worldData)

    return world

class World():
    def __init__(self, data):
        self.tileList = []
        dirtImg = pygame.image.load("img/dirt.png")
        rowCount = 0
        for row in data:
            colCount = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirtImg, (TILE_SIZE, TILE_SIZE))
                    imgRect = img.get_rect()
                    imgRect.x = colCount * TILE_SIZE
                    imgRect.y = rowCount * TILE_SIZE
                    tile = (img, imgRect)
                    self .tileList.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grassImg, (TILE_SIZE, TILE_SIZE))
                    imgRect = img.get_rect()
                    imgRect.x = colCount * TILE_SIZE
                    imgRect.y = rowCount * TILE_SIZE
                    tile = (img, imgRect)
                    self .tileList.append(tile)
                if tile == 3:
                    enemy = Enemy(colCount * TILE_SIZE, rowCount * TILE_SIZE)
                    enemyGroup.add(enemy)
                if tile == 4:
                    platform = Platform(colCount * TILE_SIZE, rowCount * TILE_SIZE, 1, 0)
                    platformGroup.add(platform)
                if tile == 5:
                    platform = Platform(colCount * TILE_SIZE, rowCount * TILE_SIZE, 0, 1)
                    platformGroup.add(platform)
                if tile == 6:
                    lava = Lava(colCount * TILE_SIZE, rowCount * TILE_SIZE + TILE_SIZE // 2)
                    lavaGroup.add(lava)
                if tile == 7:
                    coin = Coin(colCount * TILE_SIZE + (TILE_SIZE // 2), rowCount * TILE_SIZE + (TILE_SIZE // 2))
                    coinGroup.add(coin)
                if tile == 8:
                    exit = Exit(colCount * TILE_SIZE, rowCount * TILE_SIZE - TILE_SIZE // 2)
                    exitGroup.add(exit)

                colCount += 1
            rowCount += 1

    def draw(self):
        for tile in self.tileList:
            screen.blit(tile[0], tile[1])

# Replay button
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # Get mouse position
        mousePos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mousePos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)
        return action

class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, isGameOver):
        # Player's velocity
        velX = 0
        velY = 0
        frameDelay = 10
        colThreshold = 20   # Giá trị để check player có khả năng va chạm với địa hình

        if isGameOver == 0:
        # Hanlde input action to move
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.isJumping == False:
                jumpFx.play()
                self.gravity = -15
                self.isJumping = True
            if key[pygame.K_a]:
                velX -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_d]:
                velX += 5
                self.counter += 1
                self.direction = 1
            if (key[pygame.K_a] == False) and (key[pygame.K_d] == False):
                self.counter = 0
                self.frameIndex = 0
                if self.direction == 1:
                    self.image = self.imageRightList[self.frameIndex]
                if self.direction == -1:
                    self.image = self.imageLeftList[self.frameIndex]

            # Hanlde animation
            if self.counter > frameDelay:
                self.counter = 0
                self.frameIndex += 1
                if self.frameIndex >= len(self.imageRightList):
                    self.frameIndex = 0
                if self.direction == 1:
                    self.image = self.imageRightList[self.frameIndex]
                if self.direction == -1:
                    self.image = self.imageLeftList[self.frameIndex]

            # Gravity of y
            self.gravity += 1
            if self.gravity > 10:
                self.gravity = 10
            velY += self.gravity

            # Hanlde collision
            for tile in world.tileList:
                # Check for horizontal
                if tile[1].colliderect(self.rect.x + velX, self.rect.y, self.width, self.height):
                    velX = 0
                # Check for vertical
                if tile[1].colliderect(self.rect.x, self.rect.y + velY, self.width, self.height):
                    # Va chạm khi đang nhảy lên
                    if self.gravity < 0:
                        velY = tile[1].bottom - self.rect.top
                        self.gravity = 0
                    # Va chạm khi tiếp đất
                    elif self.gravity >= 0:
                        velY = tile[1].top - self.rect.bottom
                        self.gravity = 0
                        self.isJumping = False

            # Handle collision with enemy
            if pygame.sprite.spritecollide(self, enemyGroup, False) or pygame.sprite.spritecollide(self, lavaGroup, False):
                isGameOver = -1
                gameOverFx.play()

            # Collision with Exit gate
            if pygame.sprite.spritecollide(self, exitGroup, False):
                isGameOver = 1

            # Check for collision with platforms
            for platform in platformGroup:
                # collision in the x direction
                if platform.rect.colliderect(self.rect.x + velX, self.rect.y, self.width, self.height):
                    velX = 0
                # collision in the y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + velY, self.width, self.height):
                    # check if below platform
                    if abs((self.rect.top + velY) - platform.rect.bottom) < colThreshold:
                        self.gravity = 0
                        velY = platform.rect.bottom - self.rect.top
                    # check if above platform
                    elif abs((self.rect.bottom + velY) - platform.rect.top) < colThreshold:
                        self.rect.bottom = platform.rect.top - 1
                        velY = 0
                        self.isJumping = False
                    # move sideways with the platform
                    if platform.move_x != 0:
                        self.rect.x += platform.moveDirection

            # Update position
            self.rect.x += velX
            self.rect.y += velY

        elif isGameOver == -1:
            drawText('GAME OVER!', font, blue, (SCREEN_WIDTH // 2) - 200, SCREEN_HEIGHT // 2 - 100)
            self.image = self.deadImg
            if self.rect.y > 200:
                self.rect.y -= 5

        screen.blit(self.image, self.rect)
        return isGameOver

    def reset(self, x, y):
        self.imageRightList = []
        self.imageLeftList = []
        self.frameIndex = 0
        self.counter = 0
        for frame in range(1, 5):
            img = pygame.image.load(f'img/guy{frame}.png')
            img = pygame.transform.scale(img, (24, 48))
            imgLeft = pygame.transform.flip(img, True, False)
            self.imageRightList.append(img)
            self.imageLeftList.append(imgLeft)
        self.deadImg = pygame.image.load("img/ghost.png")
        self.image = self.imageRightList[self.frameIndex]
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect.x = x
        self.rect.y = y
        self.gravity = 0
        self.isJumping = False
        self.direction = 0  # Hướng di chuyển

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/blob.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.moveDirection = 1
        self.moveDistance = 0

    def update(self):
        # Đổi hướng di chuyển khi đi đc 1 khoảng
        self.rect.x += self.moveDirection
        self.moveDistance += 1
        if abs(self.moveDistance) > 50:
            self.moveDirection *= -1
            self.moveDistance *= -1


class Platform(pygame.sprite.Sprite):
    '''
    Class đại diện cho tile địa hình chuyển động
    '''
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/platform.png')
        self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.moveCounter = 0
        self.moveDirection = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.moveDirection * self.move_x
        self.rect.y += self.moveDirection * self.move_y
        self.moveCounter += 1
        if abs(self.moveCounter) > 50:
            self.moveDirection *= -1
            self.moveCounter *= -1

class Lava(pygame.sprite.Sprite):
    '''
    Class đại diện cho tile dung nham
    '''
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/lava.png")
        self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    '''
    Class đại diện cho tile coin
    '''
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img, (TILE_SIZE // 2, TILE_SIZE // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Exit(pygame.sprite.Sprite):
    '''
    Class đại diện cho cánh cửa exit và load level tiếp theo
    '''
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/exit.png")
        self.image = pygame.transform.scale(img, (TILE_SIZE, int(TILE_SIZE * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

enemyGroup = pygame.sprite.Group()
lavaGroup = pygame.sprite.Group()
exitGroup = pygame.sprite.Group()
coinGroup = pygame.sprite.Group()
platformGroup = pygame.sprite.Group()

# Icon Coin để hiện điểm số
scoreCoin = Coin(TILE_SIZE // 2, TILE_SIZE // 2 + 10)
coinGroup.add(scoreCoin)

if path.exists(f"./level{level}_data"):
    # Load level data from file and create world
    pickleInput = open(f"./level{level}_data", "rb")
    worldData = pickle.load(pickleInput)

world = World(worldData)
player = Player(100, SCREEN_HEIGHT - 100)

restartButton = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2, restartImg)
startButton = Button(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2, startImg)
exitButton = Button(SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2, exitImg)

while isRunning:
    clock.tick(FPS)
    screen.blit(backgroundImg, (0, 0))
    screen.blit(sunImg, (100, 100))

    if isMainMenu == True:
        if startButton.draw() == True:
            isMainMenu = False
        if exitButton.draw() == True:
            isRunning = False
    else:
        world.draw()
        enemyGroup.draw(screen)
        if isGameOver == 0:
            enemyGroup.update()
            platformGroup.update()
            # update score
            #check if a coin has been collected
            if pygame.sprite.spritecollide(player, coinGroup, True):
                score += 1
                coinFx.play()
            drawText('X ' + str(score), fontScore, white, TILE_SIZE, 10)

        lavaGroup.draw(screen)
        exitGroup.draw(screen)
        coinGroup.draw(screen)
        platformGroup.draw(screen)

        isGameOver = player.update(isGameOver)

        if isGameOver == -1:
            if restartButton.draw():
                worldData = []
                world = resetLevel(level)
                isGameOver = 0
                score = 0

        # If player completed the level
        if isGameOver == 1:
            # Reset game and go to next level
            level += 1
            if level <= maxLevel:
                worldData = []
                world = resetLevel(level)
                isGameOver = 0
            else:
                # Restart option
                drawText('YOU WIN!', font, blue, (SCREEN_WIDTH // 2) - 140, SCREEN_HEIGHT // 2)
                if restartButton.draw():
                    level = 0
                    worldData = []
                    world = resetLevel(level)
                    isGameOver = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
    pygame.display.update()

pygame.quit()