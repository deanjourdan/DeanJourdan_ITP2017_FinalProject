#CODE IS ORIGINALLY FROM DANIEL WESTBROOK
#I DID SOME MODIFICATION REGARDING THE GAMEPLAY, GAME CONCEPT, SOME APPEARANCE CHANGE AND THE ADDING
#SOME MENUS, BUG CLEAN UPS, AND ETC


import pygame
from pygame.locals import *
import random
import time

#Prefrences(Screen Settings, Gameplay, etc)
screensize = (800, 600)
SCREENRECT = pygame.Rect(0, 0, screensize[0], screensize[1])
CAPTION = 'The Snake Game'
FPS = 40

START_TILE = (20, 20) #Snake's Starting Point
START_SEGMENTS = 7 #Starting Snake Size

MOVE_RATE = 2
DIFFICULTY_INCREASE_RATE = 1  #Snake Speed Increasing everytime it eats the food
MOVE_THRESHOLD = 5
BLOCK_SPAWN_RATE = 1 #Spawn Trick Block

TILE_SIZE = (10, 10)
TILE_RECT = pygame.Rect(0, 0, TILE_SIZE[0], TILE_SIZE[1])

SCREENTILES = ((screensize[0] / TILE_SIZE[0]) - 1, (screensize[1] / TILE_SIZE[1]) - 1)

SNAKE_HEAD_RADIUS = 5
SNAKE_SEGMENT_RADIUS = 4
FOOD_RADIUS = 4

BG_Colour = (255, 255, 255)
SNAKE_HEAD_COLOR = (219, 79, 70)
SNAKE_SEGMENT_COLOR = (36, 200, 243)
FOOD_COLOR = (0, 255, 0)
BLOCK_COLOR = (0, 0, 150)
COLORKEY_COLOR = (255, 255, 0)

SCORE_COLOR = (0, 0, 0) #Score Test Colour
SCORE_POS = (20, 20) # Score position on Screen
SCORE_PREFIX = 'Score: ' #Score text template

MOVE_VECTORS = {'left' : (-1, 0),
				'right' : (1, 0),
				'up' : (0, -1),
				'down' : (0, 1)
				}
MOVE_VECTORS_PIXELS = {'left' : (-TILE_SIZE[0], 0),
					   'right' : (TILE_SIZE[0], 0),
					   'up' : (0, -TILE_SIZE[1]),
					   'down' : (0, TILE_SIZE[1])
					   }

#-----------------------------------------------------------------
# Game Objects
class Button(pygame.sprite.Sprite):
	def __init__(self, message, coor):
		pygame.sprite.Sprite.__init__(self)
		f = pygame.font.Font(None, 30)
		self.image = f.render(message, True, (0, 0, 0))
		self.rect = self.image.get_rect()
		self.rect.center = coor


class snake_segment(pygame.sprite.Sprite):
	def __init__(self, tilepos, segment_groups, color = SNAKE_SEGMENT_COLOR, radius = SNAKE_SEGMENT_RADIUS):
		pygame.sprite.Sprite.__init__(self)
		self.image = self.image = pygame.Surface(TILE_SIZE).convert()
		self.image.fill(COLORKEY_COLOR)
		self.image.set_colorkey(COLORKEY_COLOR)
		pygame.draw.circle(self.image, color, TILE_RECT.center, radius)

		self.tilepos = tilepos

		self.rect = self.image.get_rect()
		self.rect.topleft = (tilepos[0] * TILE_SIZE[0], tilepos[1] * TILE_SIZE[1])

		self.segment_groups = segment_groups
		for group in segment_groups:
			group.add(self)

		self.behind_segment = None

		self.movedir = 'left'

	def add_segment(self): #to add the length of the snake
		seg = self
		while True:
			if seg.behind_segment == None:
				x = seg.tilepos[0]
				y = seg.tilepos[1]
				if seg.movedir == 'left':
					x += 1
				elif seg.movedir == 'right':
					x -= 1
				elif seg.movedir == 'up':
					y += 1
				elif seg.movedir == 'down':
					y -= 1
				seg.behind_segment = snake_segment((x, y), seg.segment_groups)
				seg.behind_segment.movedir = seg.movedir
				break
			else:
				seg = seg.behind_segment

	def update(self):
		pass

	def move(self):
		self.tilepos = (self.tilepos[0] + MOVE_VECTORS[self.movedir][0], self.tilepos[1] + MOVE_VECTORS[self.movedir][1])
		self.rect.move_ip(MOVE_VECTORS_PIXELS[self.movedir])
		if self.behind_segment != None:
			self.behind_segment.move()
			self.behind_segment.movedir = self.movedir

class snake_head(snake_segment):
	def __init__(self, tilepos, movedir, segment_groups):
		snake_segment.__init__(self, tilepos, segment_groups, color = SNAKE_HEAD_COLOR, radius = SNAKE_HEAD_RADIUS)
		self.movedir = movedir
		self.movecount = 0

	def update(self):
		self.movecount += MOVE_RATE
		if self.movecount > MOVE_THRESHOLD:
			self.move()
			self.movecount = 0

class food(pygame.sprite.Sprite):
	def __init__(self, takenupgroup):
		pygame.sprite.Sprite.__init__(self)
		self.image = self.image = pygame.Surface(TILE_SIZE).convert()
		self.image.fill(COLORKEY_COLOR)
		self.image.set_colorkey(COLORKEY_COLOR)
		pygame.draw.circle(self.image, FOOD_COLOR, TILE_RECT.center, FOOD_RADIUS)

		self.rect = self.image.get_rect()
		while True:
			self.rect.topleft = (random.randint(0, SCREENTILES[0]) * TILE_SIZE[0], random.randint(0, SCREENTILES[1]) * TILE_SIZE[1])
			for sprt in takenupgroup:
				if self.rect.colliderect(sprt):
					continue # collision, food cant go here
			break # no collision, food can go here

class block(pygame.sprite.Sprite):
	def __init__(self, takenupgroup):
		pygame.sprite.Sprite.__init__(self)
		self.image = self.image = pygame.Surface(TILE_SIZE).convert()
		self.image.fill(BLOCK_COLOR)

		self.rect = self.image.get_rect()
		while True:
			self.rect.topleft = (random.randint(0, SCREENTILES[0]) * TILE_SIZE[0], random.randint(0, SCREENTILES[1]) * TILE_SIZE[1])
			for sprt in takenupgroup:
				if self.rect.colliderect(sprt):
					continue # collision, food cant go here
			break # no collision, food can go here

#------------------------------------------------------
#Game Conditions
def main():
	pygame.init()
	screen = pygame.display.set_mode(screensize)
	pygame.display.set_caption(CAPTION)
	bg = pygame.Surface(screensize).convert()
	bg.fill(BG_Colour)
	screen.blit(bg, (0, 0))

	snakegroup = pygame.sprite.Group()
	snakeheadgroup = pygame.sprite.Group()
	foodgroup = pygame.sprite.Group()
	blockgroup = pygame.sprite.Group()
	takenupgroup = pygame.sprite.Group()
	all = pygame.sprite.RenderUpdates()

	snake = snake_head(START_TILE, 'right', [snakegroup, all, takenupgroup])
	snakeheadgroup.add(snake)
	for index in range(START_SEGMENTS):
		snake.add_segment()

	currentfood = 'no food'

	block_frame = 0

	currentscore = 0

	pygame.display.flip()

#----------------------------------------------------------
#GameLoop
	quit = False
	clock = pygame.time.Clock()
	lose = False
	while not quit:
		# events
		for event in pygame.event.get():
			if event.type == QUIT:
				quit = True
			elif event.type == KEYDOWN:
				currentmovedir = snake.movedir
				if event.key == K_UP:
					tomove = 'up'
					dontmove = 'down'
				elif event.key == K_DOWN:
					tomove = 'down'
					dontmove = 'up'
				elif event.key == K_LEFT:
					tomove = 'left'
					dontmove = 'right'
				elif event.key == K_RIGHT:
					tomove = 'right'
					dontmove = 'left'
				if not currentmovedir == dontmove:
					snake.movedir = tomove

# clearing
		all.clear(screen, bg)
# updates
		all.update()

		if currentfood == 'no food':
			currentfood = food(takenupgroup)
			foodgroup.add(currentfood)
			takenupgroup.add(currentfood)
			all.add(currentfood)

		pos = snake.rect.topleft
		if pos[0] < 0:
			quit = True
			lose = True
		if pos[0] >= screensize[0]:
			quit = True
			lose = True
		if pos[1] < 0:
			quit = True
			lose = True
		if pos[1] >= screensize[1]:
			quit = True
			lose = True

# Head collides to Food
		col = pygame.sprite.groupcollide(snakeheadgroup, foodgroup, False, True)
		for head in col:
			for tail in col[head]:
				currentfood = 'no food'
				snake.add_segment()

				currentscore += 1
				global MOVE_RATE, DIFFICULTY_INCREASE_RATE
				MOVE_RATE += DIFFICULTY_INCREASE_RATE
				block_frame += 1
				if block_frame >= BLOCK_SPAWN_RATE:
					block_frame = 0
					b = block(takenupgroup)
					blockgroup.add(b)
					takenupgroup.add(b)
					all.add(b)

# Head Collides to trick block
		col = pygame.sprite.groupcollide(snakeheadgroup, blockgroup, False, False)
		for head in col:
			for collidedblock in col[head]:
				quit = True
				lose = True

		#Scoring System
		d = screen.blit(bg, SCORE_POS, pygame.Rect(SCORE_POS, (50, 100)))
		f = pygame.font.Font(None, 25)
		scoreimage = f.render(SCORE_PREFIX + str(currentscore), True, SCORE_COLOR)
		d2 = screen.blit(scoreimage, SCORE_POS)

		# Draw Game
		dirty = all.draw(screen)
		dirty.append(d)
		dirty.append(d2)

		# Display Update
		pygame.display.update(dirty)

		# waiting
		clock.tick(FPS)

	#Game Over
	if lose == True:
		losetext = pygame.font.Font(None, 60)
		failmessage = losetext.render('Game Over', True, (0, 0, 0))
		restart_button = Button("Restart", (300,400))
		quit_button = Button("Exit", (490,400))
		buttons_group = pygame.sprite.Group(restart_button, quit_button)
		while lose == True:
			screen.fill((255, 0, 0))
			screen.blit(failmessage, (285,200))
			buttons_group.draw(screen)
			pygame.display.flip()
			for ev in pygame.event.get():
				if ev.type == QUIT:
					exit()
				if ev.type == MOUSEBUTTONDOWN:
					if restart_button.rect.collidepoint(pygame.mouse.get_pos()):
						lose = False
						main()
					if quit_button.rect.collidepoint(pygame.mouse.get_pos()):
						exit()

if __name__ == "__main__":
	main()
