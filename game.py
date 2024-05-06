import pygame
from pygame.locals import *
from pygame import mixer
import random


#initialising audio mixer and fonts
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.font.init()

#set fps
clock = pygame.time.Clock()
fps = 60

#game window size
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
#creation of game window and window title
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('GAME NAME HERE')


#fonts
font10 = pygame.font.Font('assets/BarcadeBrawlRegular-plYD.ttf', 10)
font30 = pygame.font.Font('assets/BarcadeBrawlRegular-plYD.ttf', 30)


#loading of sounds 
explosion_fx = pygame.mixer.Sound("assets/exp_1.mp3")
explosion_fx.set_volume(0.175)

explosion2_fx = pygame.mixer.Sound("assets/exp_2.mp3")
explosion_fx.set_volume(0.1)

explosion3_fx = pygame.mixer.Sound("assets/moreexplosion.mp3")
explosion_fx.set_volume(0.1)

explosion4_fx = pygame.mixer.Sound("assets/laserexp2.mp3")
explosion_fx.set_volume(0.1)

laser_fx = pygame.mixer.Sound("assets/laser.mp3")
laser_fx.set_volume(0.05)

#loading of background music
music = pygame.mixer.music.load("assets/DeepSpaceA.ogg")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.05)


#defining game variables
run = True
rows = 5
cols = 5
last_alien_shot = pygame.time.get_ticks()
alien_cooldown = 1000 #milliseconds
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0 #0 is not game over, 1 is player has won, -1 is player is dead
score = 0
high_score = 0

#function to check the current highscore by reading the highscore.txt file and reading the first line as an int, it then stores that integer as the high_score
def load_high_score():
    global high_score
    high_score = []
    with open("highscore.txt", "r") as file:
        high_score = int(file.read())
    return high_score


#define colours
red = (255,0,0)
green = (0,255,0)
white = (255, 255, 255)
blue = (0, 0, 255)

#load background image
bg = pygame.image.load("assets/bg.png")

#function to draw background
def draw_bg():
    screen.blit(bg, (0, 0))


#function to add text to the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


#create spaceship class and a child of the class to inherit features
class Spaceship(pygame.sprite.Sprite):
    def  __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/Main Ship - Base - Full health.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()


    def update(self):
        #set left & right movement speed
        speed = 7
        #set shot cooldown in milliseconds
        cooldown = 500
        #game over boolean
        game_over = 0

        #get key press
        key = pygame.key.get_pressed()
        if key[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += speed



        #record current time
        time_now = pygame.time.get_ticks()
        #shooting keypress
        if event.type == pygame.MOUSEBUTTONDOWN and time_now - self.last_shot > cooldown:
            mouse_presses = pygame.mouse.get_pressed()
            if mouse_presses[0]:
                laser_fx.play()
                laser = Lasers(self.rect.centerx, self.rect.top)
                laser_group.add(laser)
                self.last_shot = time_now


        #update mask of ship
        self.mask = pygame.mask.from_surface(self.image)  


        #draw health bar
        pygame.draw.rect(screen, red, (self.rect.x,(self.rect.bottom + 8), self.rect.width, 6))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x,(self.rect.bottom + 8), int(self.rect.width * (self.health_remaining / self.health_start)), 6))
        #check remaining health and change sprite png accordingly
        if self.health_remaining == 3:
            self.image = pygame.image.load("assets/Main Ship - Base - Slight damage.png")
        if self.health_remaining == 2:
            self.image = pygame.image.load("assets/Main Ship - Base - Damaged.png")
        if self.health_remaining == 1:
            self.image = pygame.image.load("assets/Main Ship - Base - Very damaged.png")
        #if health remaining is 0 or less then, player ship explodes and the asset is destroyed, game_over bool is then changed and returned
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over
        

#creation of player's laser projectile
class Lasers(pygame.sprite.Sprite):
    def  __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/smolbluelaser.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True, pygame.sprite.collide_mask):
            self.kill()
            global score
            score = score + 50 #increments the score by 50 for each enemy destroyed
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
        return score #returns total score to global variable 

class Aliens(pygame.sprite.Sprite):
    def  __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        rand = random.randint(1,6)
        self.image = pygame.image.load("assets/alien" + str(rand) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1
        self.name = "alien" + str(rand)

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction
        self.mask = pygame.mask.from_surface(self.image) #mask is used to make hit detection far cleaner


class Alien_Lasers(pygame.sprite.Sprite):
    def  __init__(self, x, y, laser_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/redshiplaser.png") #assigns projectile to red ships and then
        if laser_type == "alien3" or laser_type == "alien4" or laser_type == "alien6": #in this code I have identified the 3 green ships and assigned them a different projectile
            self.image = pygame.image.load("assets/greenshiplaser.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask): #masking is used again for cleaner hit detection
            self.kill() #asset is destroyed on collision
            explosion_fx.play() #sound fx played for explosion
            global score
            score = score - 20 #score is reduced if player is hit
            #reduce health here if hit
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion) #adds explosion entity to explosion group
        return score #returns current score to global variable score
            


#creation of Exposion class
class Explosion(pygame.sprite.Sprite):
    def  __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range (1,65): #my explosions use 64 different png images so i use a for loop to cycle through them
            img = pygame.image.load(f"assets/greenexplosion/frame{num}.png")
            if size == 1:
                img = pygame.transform.scale(img,(30, 30)) #have the option or making the explosions larger or smaller
            if size == 2:
                img = pygame.transform.scale(img,(60, 60))
            if size == 3:
                img = pygame.transform.scale(img,(80, 80))
            #add the image to a list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.counter = 0

    def update(self):
        explosion_speed = 5
        #update of explosion animation
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        #check for animation completion and delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill() #destroy the explosion images


#creation of sprite group
spaceship_group = pygame.sprite.Group()
laser_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_laser_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def create_aliens():
    #spawn aliens
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(100 + item * 100, 30 + row * 70)
            alien_group.add(alien)
create_aliens() #create alien items and spawn them after x amount of pixels along the rows and columns

#create player
spaceship = Spaceship(int (SCREEN_WIDTH / 2), SCREEN_HEIGHT - 50, 4)
spaceship_group.add(spaceship)

#game code
while run:

    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False     

    #sets fps on runtime
    clock.tick(fps)
    #draw background
    draw_bg()
    #calls the function to retrieve the current high score
    load_high_score()
    

    #start countdown
    if countdown == 0:
        #create random alien lasers
        #record current time
        time_now = pygame.time.get_ticks()
        #alienlasershot with cool down
        if (time_now - last_alien_shot > alien_cooldown and len(alien_laser_group) < 5) and (len(alien_group.sprites()) > 0):
            attacking_alien = random.choice(alien_group.sprites())
            alien_laser = Alien_Lasers(attacking_alien.rect.centerx, attacking_alien.rect.bottom, attacking_alien.name)
            alien_laser_group.add(alien_laser)
            last_alien_shot = time_now

        draw_text('score = ', font10, white, int(SCREEN_WIDTH - 590), int(SCREEN_HEIGHT - 20)) #displaying 'score' on bottom left of display

        if (score <= high_score):
            draw_text(str(score), font10, red, int(SCREEN_WIDTH - 505), int(SCREEN_HEIGHT - 20)) #if score is less than or equal to highscore, the text is red
        elif (score > high_score):
            draw_text(str(score), font10, green, int(SCREEN_WIDTH - 505), int(SCREEN_HEIGHT - 20)) #if score is greater than highscore, the text is green

        #checks if all aliens are dead, if yes, game over, player wins
        if len(alien_group) == 0:
            game_over = 1
        if game_over == 0: #game runs as no win/loss condition has been met
        #update spaceship
            game_over = spaceship.update()
            #update sprite groups
            laser_group.update()
            alien_group.update()
            alien_laser_group.update()
        else: #else statement to check which win or loss condition has been met
            if game_over == -1:            
                draw_text('YOU ARE DEAD', font30, red, int(SCREEN_WIDTH / 2 - 180), int(SCREEN_HEIGHT / 2 + 50)) #text displayed in larger red font to tell the player they are dead
                if (score > high_score): #check to see if score at time of death was larger than highscore, if it is, file is accessed and rewritten
                    high_score = score
                    with open("highscore.txt", "w") as file:
                        file.write(str(high_score))

            if game_over == 1:            
                draw_text('YOU WIN', font30, blue, int(SCREEN_WIDTH / 2 - 110), int(SCREEN_HEIGHT / 2 - 30)) #text displayed in larger blue font to tell the player they won
                if (score > high_score): #check to see if score at time of win was larger than highscore, if it is, file is accessed and rewritten
                    high_score = score
                    with open("highscore.txt", "w") as file:
                        file.write(str(high_score))
            
            

    #check if countdown is active, if yes, draw text on screen to prep player, countdown from 5 is shown too
    if countdown > 0:
        draw_text('GET READY TO PLAY', font30, white, int(SCREEN_WIDTH / 2 - 260), int(SCREEN_HEIGHT / 2 + 50))
        draw_text(str(countdown), font30, red, int(SCREEN_WIDTH / 2 - 15), int(SCREEN_HEIGHT / 2 + 100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer
    
    explosion_group.update() #keep seperate to countdown if statement so that it isn't cut off mid animation

    #draw sprite groups
    spaceship_group.draw(screen)
    laser_group.draw(screen)
    alien_group.draw(screen)
    alien_laser_group.draw(screen)
    explosion_group.draw(screen)

    pygame.display.update()

pygame.quit()


