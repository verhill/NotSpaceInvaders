import pygame
import random
import math
import sys
from pygame.locals import *
pygame.init()
pygame.font.init()
NAME = input("Enter Name: ").upper()
pygame.display.set_caption("NOT Space Invaders")
#NAME = str(input('INSERT NAME: ')).upper() #Asks for a name before opening the window

class game():
    def __init__(self):
        self.FPS = 60
        self.FRAMES = 0
        self.PAUSED = False
        self.fpsClock = pygame.time.Clock()
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        self.STEP = 7 # Player movementspeed (pixels/frame)
        self.MAX_LASERS = 20 # To prevent system-overload
        self.PLAYER_HEALTH = 12 # 4=hard, 8=medium, 15=easy
        self.GAMESTATE = 'Menu'
        self.GAMESTATE_DEBUG = False
        self.SCORE = 0 # Score each playthrough
        self.POINTS = 0 # Total score each restart
        self.PAUSE_WINDOW = pygame.Surface((self.WINDOW_WIDTH,self.WINDOW_HEIGHT))
        self.PAUSE_WINDOW.set_alpha(150)
        self.PAUSE_WINDOW.fill((0,0,0))
        self.WINDOW = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.USERNAME = NAME # The name of the player
        self.CHARACTER = None # The player (character object)
        self.BOSS = None # Needed to see if the boss exists or not
        self.LEADERBOARD = [] # Saved leaderboard (to remember leaderboard positions)
        self.FONTS = { # All fonts used
            "Score": pygame.font.SysFont('Arial', 16),
            "Leaderboard": pygame.font.SysFont('timesnewroman',25)
        }
        self.SOUNDS = {
            "Music": pygame.mixer.music.load('sounds\MusicLOOP.wav'),
            "Pew": pygame.mixer.Sound('sounds\PEW.wav'),
            "Explosion": pygame.mixer.Sound('sounds\Explosion.wav')
        }
        self.SPRITE_GROUPS = { # All currnet sprite groups, (used for group collisions)
            "PlayerLasers": pygame.sprite.Group(),
            "EnemyLasers": pygame.sprite.Group(),
            "Enemies": pygame.sprite.Group(),
            "Buttons": pygame.sprite.Group(),
            "Players": pygame.sprite.Group(),
            "Explosions": pygame.sprite.Group()
        }
        self.IMAGES = { # List of loaded images (to not load the same image multiple times)
            "Icon": pygame.image.load('images\game_icon.png'),
            "Explosion": pygame.image.load('images\Explosion.png').convert_alpha(),
            "Laser": pygame.image.load('images\Laser.png').convert_alpha(),
            "Beam": pygame.image.load('images\Beam.png').convert_alpha(),
            "PlayerImage": pygame.image.load('images\AMC_2.png').convert_alpha(),
            "Enemy1": pygame.image.load('images\Enemy.png').convert_alpha(),
            "Enemy2": pygame.image.load('images\Enemy2.png').convert_alpha(),
            "Enemy3": pygame.image.load('images\Enemy3.png').convert_alpha(),
            "Boss": pygame.image.load('images\Boss.png').convert_alpha(),
            "Background": pygame.image.load('images\Bakgrund.png').convert(),
            "Background2": pygame.image.load('images\Bakgrund2.png').convert_alpha(),
            "ButtonImageQuit": pygame.image.load('images\Quit.png').convert_alpha(),
            "ButtonImageStart": pygame.image.load('images\Start.png').convert_alpha(),
            "ButtonImageTitleCard": pygame.image.load('images\Title.png').convert_alpha()
        }
        pygame.display.set_icon(self.IMAGES["Icon"])
    def changeGameState(self,gamestate="STAGE1"):
        #Used to start & swap between stages (default is STAGE1)
        self.GAMESTATE = gamestate
        self.GAMESTATE_DEBUG = False # Fixes repetition
        print("Changes gamestate to " + gamestate)

        # Kill sprites:
        for i in self.SPRITE_GROUPS["Buttons"]:
            i.kill()
        for i in self.SPRITE_GROUPS["Enemies"]:
            i.kill()
        for i in self.SPRITE_GROUPS["EnemyLasers"]:
            i.kill()
        
        # If the gamestate is changed to menu:
        if gamestate == "Menu": #Resets character & saves velocity (to not mess with controls)
            self.SCORE = 0
            oldx = self.CHARACTER.x
            oldy = self.CHARACTER.y

            for i in self.SPRITE_GROUPS["Players"]:
                i.kill()
            for i in self.SPRITE_GROUPS["PlayerLasers"]:
                i.kill()
            for i in self.SPRITE_GROUPS["Explosions"]:
                i.kill()

            self.CHARACTER = gameCharacter(GAME.IMAGES["PlayerImage"],GAME.WINDOW_WIDTH/2,GAME.WINDOW_HEIGHT-150, GAME.STEP, GAME.PLAYER_HEALTH)
            GAME.CHARACTER.x = oldx
            GAME.CHARACTER.y = oldy
    
    def QUIT(self): # Exits the game & updates the score
        print("Quits")
        self.UpdateScore()
        pygame.quit()
        sys.exit()
    
    def UpdateLeaderboard(self): # Updates the LEADERBOARD variable
        READ = self.LEADERBOARD

        usernameExists = False
        for i in range(len(READ)):
            if READ[i].split(',')[0] == self.USERNAME:
                usernameExists = True
                if int((READ[i].split(','))[1][:-1]) < self.SCORE:
                    READ[i] = self.USERNAME+','+str(self.SCORE)+'\n'
                break
        
        if usernameExists == False:
            READ.append(str(self.USERNAME)+','+str(self.SCORE)+'\n')

        for i in range(len(READ)):
            for j in range(len(READ)):
                if int((READ[j].split(','))[1][:-1]) < int((READ[i].split(','))[1][:-1]):
                    READ[i],READ[j] = READ[j],READ[i]
        
        self.LEADERBOARD = READ
    
    def UpdateScore(self): # Updates .txt file with LEADERBOARD
        with open('HIGHSCORE.txt', 'w') as c:
            c.writelines(self.LEADERBOARD)
            c.close()

GAME = game() # Initializes the GAME class

#   CLASSES
class gameObject(pygame.sprite.Sprite):
    def __init__(self,image,x,y):
        super().__init__()
        self.image = image
        self.x = 0 # Usually velocity in x
        self.y = 0 # Usually velocity in y
        self.rect = image.get_rect() # Gets the rectangle boundry
        self.rect.x = x #Pixel location in x (rectangle location)
        self.rect.y = y #Pixel location in y (rectangle location)
    def move(self, x, y): # Adds velocity to x/y
        self.x += x
        self.y += y

class gameImage(gameObject):
    def __init__(self, image, x, y, function=None):
        super().__init__(image,x,y)
        self.x = x # Position in x
        self.y = y # Position in y
        self.function = function # Any funktion 
        self.i = -1 # Spreadsheet information
    def updateSheet(self):
        self.i += 1
        if self.i*self.rect.y <= self.rect.x:
            GAME.WINDOW.blit(self.image,(self.x,self.y),(self.i*64,0,64,64)) #Cuts the image in 64x64 pieces
        else: # If the animation is finished, kill the object
            self.kill()
        
class gameLaser(gameObject):
    def __init__(self, image , x, y, laserClass):
        super().__init__(image,x,y)
        self.Class = laserClass
        if laserClass == "Player":
            GAME.SPRITE_GROUPS["PlayerLasers"].add(self)
        else:
            GAME.SPRITE_GROUPS["EnemyLasers"].add(self)
    def update(self):
        self.rect.x += self.x
        self.rect.y += self.y

        if self.rect.y > GAME.WINDOW_HEIGHT or self.rect.y < -132:
            self.kill()

class gameCharacter(gameObject):
    def __init__(self, image, x, y, speed, health):
        super().__init__(image,x,y)
        self.speed = speed
        self.health = health
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.maxhealth = health
        self.graceTimer = 0
        self.isGrace = False
        GAME.SPRITE_GROUPS["Players"].add(self)
    def update(self):
        self.rect.x += self.x
        self.rect.y += self.y
        
        if self.rect.x > GAME.WINDOW_WIDTH-self.image.get_width():
            self.rect.x = GAME.WINDOW_WIDTH-self.image.get_width()
        if self.rect.x < 0:
            self.rect.x = 0

        if self.rect.y > GAME.WINDOW_HEIGHT-self.image.get_height():
            self.rect.y = GAME.WINDOW_HEIGHT-self.image.get_height()
        elif self.rect.y < 0:
            self.rect.y = 0

        if self.isGrace == True:
            pygame.draw.rect(GAME.WINDOW, (0, 0, 255), ((self.rect.x),(self.rect.y + 48),(48*(self.health/GAME.PLAYER_HEALTH)),(6)))
        else:
            pygame.draw.rect(GAME.WINDOW, (255*(1 - (self.health/GAME.PLAYER_HEALTH)), 255*(self.health/GAME.PLAYER_HEALTH), 0), ((self.rect.x),(self.rect.y + 48),(48*(self.health/self.maxhealth)),(6)))
    def addHealth(self,hp):
        if GAME.GAMESTATE != "Menu":
            self.health += hp
            if self.health <= 0:
                GAME.UpdateLeaderboard()
                oldx = self.x
                oldy = self.y
                GAME.changeGameState("Menu")
                GAME.CHARACTER.x = oldx
                GAME.CHARACTER.y = oldy
                print("GAMEOVER")
            else:
                self.isGrace = True

class gameEnemy(gameObject):
    def __init__(self, image, x, y, speed, health, canShootLaser, classType="enemy"):
        super().__init__(image,x,y)
        self.y = speed
        self.speed = speed
        self.health = health #
        self.maxhealth = health #Score based on health
        self.canShoot = canShootLaser #Determines if the enemy can shoot
        self.currentX = x #Exact location of x
        self.currentY = y #Exact location of y
        self.classType = classType #Determines which type of enemy
        GAME.SPRITE_GROUPS["Enemies"].add(self)
    def update(self):
        self.currentX += self.x
        self.currentY += self.y
        self.rect.x = self.currentX + math.sin(self.currentY/10)*15
        self.rect.y = self.currentY + math.sin(self.currentY/5)*5

def keyInputs(): # Only used so events stay detected during pause screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GAME.QUIT()
        if event.type == pygame.KEYDOWN:
            if event.key == ord("0"):
                GAME.QUIT()
            if event.key == ord("a"):
                GAME.CHARACTER.move(-GAME.STEP,0)
            if event.key == ord("d"):
                GAME.CHARACTER.move(GAME.STEP,0)
            if event.key == ord("w"):
                GAME.CHARACTER.move(0,-GAME.STEP)
            if event.key == ord("s"):
                GAME.CHARACTER.move(0,GAME.STEP)
            if event.key == 32 and GAME.PAUSED == False: #This is a space bar (found using print(event.key))
                if len(GAME.SPRITE_GROUPS["PlayerLasers"]) < GAME.MAX_LASERS:
                    nyLaser = gameLaser(GAME.IMAGES["Laser"],GAME.CHARACTER.rect.x+GAME.CHARACTER.image.get_width()/2-3,GAME.CHARACTER.rect.y,"Player")
                    nyLaser.move(0,-5)
                    pygame.mixer.Sound.play(GAME.SOUNDS["Pew"])
            if event.key == 27: #This is escape [esc]
                if GAME.PAUSED == False:
                    GAME.PAUSED = True
                else:
                    GAME.PAUSED = False
        if event.type == pygame.KEYUP:
            if event.key == ord("a"):
                GAME.CHARACTER.move(GAME.STEP,0)
            if event.key == ord("d"):
                GAME.CHARACTER.move(-GAME.STEP,0)
            if event.key == ord("w"):
                GAME.CHARACTER.move(0,GAME.STEP)
            if event.key == ord("s"):
                GAME.CHARACTER.move(0,-GAME.STEP)

#STARTUP CODE
pygame.mixer.music.play(-1)

GAME.CHARACTER = gameCharacter(GAME.IMAGES["PlayerImage"],GAME.WINDOW_WIDTH/2,GAME.WINDOW_HEIGHT-150, GAME.STEP, GAME.PLAYER_HEALTH)

with open('HIGHSCORE.txt') as h:
    GAME.LEADERBOARD = h.readlines()
    h.close()

looping = True
while looping:
    #EVENTS
    keyInputs()

    #COUNT GAME FRAMES (game duration)
    GAME.FRAMES += 1
    
    # Background update
    GAME.WINDOW.blit(GAME.IMAGES["Background"],(0,0))
    GAME.WINDOW.blit(GAME.IMAGES["Background2"],(0,GAME.FRAMES/2 % GAME.WINDOW_HEIGHT))
    GAME.WINDOW.blit(GAME.IMAGES["Background2"],(0,GAME.FRAMES/2 % GAME.WINDOW_HEIGHT-GAME.WINDOW_HEIGHT))
    GAME.WINDOW.blit(GAME.FONTS["Score"].render("SCORE: " + str(GAME.SCORE), False, (255,255,255)),(5,25))
    GAME.WINDOW.blit(GAME.FONTS["Score"].render("NAME: " + GAME.USERNAME, False, (255,255,255)),(5,5))
    
    # GAMESTATES
    if GAME.GAMESTATE == 'Menu':
        if GAME.GAMESTATE_DEBUG == False: #Plays once after each gamestate change
            TitleCard = gameImage(GAME.IMAGES["ButtonImageTitleCard"], 0, 0, None)
            StartButton = gameImage(GAME.IMAGES["ButtonImageStart"], 0, 400, GAME.changeGameState)
            QuitButton = gameImage(GAME.IMAGES["ButtonImageQuit"], GAME.WINDOW_WIDTH-100, 400, GAME.QUIT)
            # The last argument is the function that should be played when
            # the player hits the button, no function does not remove lasers on collision

            GAME.SPRITE_GROUPS["Buttons"].add(TitleCard)
            GAME.SPRITE_GROUPS["Buttons"].add(StartButton)
            GAME.SPRITE_GROUPS["Buttons"].add(QuitButton)
        GAME.GAMESTATE_DEBUG = True

        #Main Code (Only renders the leaderboard)
        GAME.WINDOW.blit(GAME.FONTS["Score"].render('TOP 10', False, (255,255,255)),(400,190))
        for i in range(min(len(GAME.LEADERBOARD),10)):
            GAME.WINDOW.blit(GAME.FONTS["Score"].render(str(i+1) + ': ' + str((GAME.LEADERBOARD[i].split(','))[0]), False, (255,255,255)),(200,210 + 20*i))
            GAME.WINDOW.blit(GAME.FONTS["Score"].render(str((GAME.LEADERBOARD[i].split(','))[1][:-1]), False, (255,255,255)),(600,210 + 20*i))
    else: #When the player is not in the menu
        for i in GAME.SPRITE_GROUPS["Enemies"]:
            if i.classType == "Boss" and GAME.FRAMES % 25 == 0: #BOSS shoots diffrently #v1.3.0 #Added beams v1.4.4
                    nyLaser = gameLaser(GAME.IMAGES["Beam"],int(800*random.random()),-131,"Enemy")
                    nyLaser.move(0,5)
            if i.canShoot and GAME.FRAMES % 40 == 0:
                if random.random() >= 0.9:
                    if i.classType == "Tank": # New enemy class type that shoots beams instead of lasers
                        nyLaser = gameLaser(GAME.IMAGES["Beam"],i.rect.x+i.image.get_width()/2,i.rect.y+i.image.get_height(),"Enemy")
                        nyLaser.move(0,5)
                    else:
                        nyLaser = gameLaser(GAME.IMAGES["Laser"],i.rect.x+i.image.get_width()/2,i.rect.y+i.image.get_height(),"Enemy")
                        nyLaser.move(0,5)
            
            if i.rect.y > GAME.WINDOW_HEIGHT:
                GAME.CHARACTER.addHealth(-(i.health)) #v1.3.0
                i.kill()
        
    if GAME.GAMESTATE == 'STAGE1':
        if GAME.SCORE >= 100:
            if len(GAME.SPRITE_GROUPS["Enemies"]) == 0: #Condition to go to next stage (100+ score & 0 enemies left)
                GAME.changeGameState("STAGE4")
        else: # After 100 score, enemies stop coming;
            if GAME.FRAMES % 240 == 0:
                randomChance = random.random()
                if randomChance >= 0.6:
                    for i in range(1,random.randrange(4,10)+1):
                        enemyPositionX = GAME.WINDOW_WIDTH/2-(30*i)*(-1)**i
                        enemy = gameEnemy(GAME.IMAGES["Enemy1"],enemyPositionX,0,0.8,2,True)
                elif randomChance >= 0.4:
                    for i in range(1,random.randrange(3,6)+1):
                        enemyPositionX = GAME.WINDOW_WIDTH/2-(40*i)*(-1)**i
                        enemy = gameEnemy(GAME.IMAGES["Enemy2"],enemyPositionX,0,0.5,4,True,"Tank")
                else:
                    for i in range(1,random.randrange(8,12)+1):
                        enemyPositionX = GAME.WINDOW_WIDTH/2-(30*i)*(-1)**i
                        enemy = gameEnemy(GAME.IMAGES["Enemy3"],enemyPositionX,0,1.5,1,False)
    
    if GAME.GAMESTATE == 'STAGE4': #v1.3.0
        if GAME.GAMESTATE_DEBUG == False:
            GAME.BOSS = gameEnemy(GAME.IMAGES["Boss"],(GAME.WINDOW_WIDTH/2)-41,50,0,50,False,"Boss")
            GAME.SPRITE_GROUPS["Enemies"].add(GAME.BOSS)
            GAME.SPRITE_GROUPS["Enemies"].draw(GAME.WINDOW)
        GAME.GAMESTATE_DEBUG = True

        if GAME.FRAMES % 300 == 0 and GAME.BOSS != None: # Summons waves of random enemy types; v1.4.4
            randomChance = random.random()
            if randomChance >= 0.6:
                for i in range(1,random.randrange(4,10)+1):
                    enemyPositionX = GAME.WINDOW_WIDTH/2-(30*i)*(-1)**i
                    enemy = gameEnemy(GAME.IMAGES["Enemy1"],enemyPositionX,0,0.8,2,True)
            elif randomChance >= 0.4:
                for i in range(1,random.randrange(3,6)+1):
                    enemyPositionX = GAME.WINDOW_WIDTH/2-(40*i)*(-1)**i
                    enemy = gameEnemy(GAME.IMAGES["Enemy2"],enemyPositionX,0,0.5,4,True,"Tank")
            else:
                for i in range(1,random.randrange(8,12)+1):
                    enemyPositionX = GAME.WINDOW_WIDTH/2-(30*i)*(-1)**i
                    enemy = gameEnemy(GAME.IMAGES["Enemy3"],enemyPositionX,0,1.5,1,False)
        if len(GAME.SPRITE_GROUPS["Enemies"]) == 0:
            print('VICTORY SCORE:' + str(GAME.SCORE))
            GAME.UpdateLeaderboard()
            GAME.changeGameState("Menu")

    # Collisions
    if GAME.GAMESTATE == "Menu":
        for button, laser in pygame.sprite.groupcollide(GAME.SPRITE_GROUPS["Buttons"],GAME.SPRITE_GROUPS["PlayerLasers"],0,0).items():
            if button.function is not None:
                laser[0].kill()
                button.function()
    for enemy in pygame.sprite.groupcollide(GAME.SPRITE_GROUPS["Enemies"],GAME.SPRITE_GROUPS["PlayerLasers"],0,1).keys():
        enemy.health -= 1
        if enemy.health <= 0:
            GAME.SCORE += enemy.maxhealth
            GAME.POINTS += enemy.maxhealth
            if enemy.classType == "Boss":
                GAME.BOSS = None
            y = enemy.currentY
            x = enemy.currentX
            enemy.kill()
            pygame.mixer.Sound.play(GAME.SOUNDS["Explosion"])
            explosion = gameImage(GAME.IMAGES["Explosion"],x,y)
            GAME.SPRITE_GROUPS["Explosions"].add(explosion)
    if GAME.CHARACTER.isGrace == False:
        for player in pygame.sprite.groupcollide(GAME.SPRITE_GROUPS["Players"],GAME.SPRITE_GROUPS["EnemyLasers"],0,1).keys():
            GAME.CHARACTER.addHealth(-1)
        for enemy in pygame.sprite.groupcollide(GAME.SPRITE_GROUPS["Enemies"],GAME.SPRITE_GROUPS["Players"],0,0).keys():
            GAME.CHARACTER.addHealth(-enemy.health)
            
            y = enemy.currentY 
            x = enemy.currentX
            enemy.kill()
            pygame.mixer.Sound.play(GAME.SOUNDS["Explosion"])
            explosion = gameImage(GAME.IMAGES["Explosion"],x,y)
            GAME.SPRITE_GROUPS["Explosions"].add(explosion)
    for explosion in GAME.SPRITE_GROUPS["Explosions"]:
        if GAME.FRAMES % 5 == 0:
            explosion.updateSheet()
        else:
            GAME.WINDOW.blit(explosion.image,(explosion.x,explosion.y),(explosion.i*64,0,64,64))

    #Players.draw(WINDOW)
    GAME.SPRITE_GROUPS["PlayerLasers"].update()
    GAME.SPRITE_GROUPS["PlayerLasers"].draw(GAME.WINDOW)
    GAME.SPRITE_GROUPS["Players"].update()
    GAME.SPRITE_GROUPS["Players"].draw(GAME.WINDOW)
    GAME.SPRITE_GROUPS["Enemies"].update()
    GAME.SPRITE_GROUPS["Enemies"].draw(GAME.WINDOW)
    GAME.SPRITE_GROUPS["EnemyLasers"].update()
    GAME.SPRITE_GROUPS["EnemyLasers"].draw(GAME.WINDOW)
    GAME.SPRITE_GROUPS["Buttons"].draw(GAME.WINDOW)

    pygame.display.update() # uppdaterar skärmen

    #Grace timer
    if GAME.CHARACTER.isGrace == True:
        GAME.CHARACTER.graceTimer += 1
        if GAME.CHARACTER.graceTimer == 60:
            GAME.CHARACTER.isGrace = False
            GAME.CHARACTER.graceTimer = 0
    GAME.fpsClock.tick(GAME.FPS)

    if GAME.PAUSED == True:
        #Render the pause screen once
        GAME.WINDOW.blit(GAME.PAUSE_WINDOW,(0,0))
        GAME.WINDOW.blit(GAME.FONTS["Leaderboard"].render("PAUSED",False,(230,50,50)),(GAME.WINDOW_WIDTH/2,GAME.WINDOW_HEIGHT/2))
        pygame.display.update()

        #Some form of loop is required to process the (x) button, which is why we used another while loop.
        while GAME.PAUSED == True:
            keyInputs()
            GAME.fpsClock.tick(30)