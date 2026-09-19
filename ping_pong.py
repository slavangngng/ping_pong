from pygame import *
import io
import os
import subprocess
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

WIN_WIDTH= 600
WIN_HEIGHT = 400
fps = 60

win = transform.scale(image.load(resource_path('you win.png')),(WIN_WIDTH, WIN_HEIGHT))
lose = transform.scale(image.load(resource_path('game+over.png')),(WIN_WIDTH, WIN_HEIGHT))
background=transform.scale(image.load(resource_path('фон.jpg')),(WIN_WIDTH, WIN_HEIGHT))
main_win = display.set_mode((WIN_WIDTH,WIN_HEIGHT))

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed, wight, height):
        super().__init__()
        self.image = transform.scale(image.load(resource_path(player_image)), (wight, height))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.start_x = player_x
        self.start_y = player_y   
        self.start_speed = player_speed
    def reset(self):
        main_win.blit(self.image, (self.rect.x, self.rect.y))

    def restart(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.speed = self.start_speed

class Player_L(GameSprite):
    score = 0
    def update(self):
        keys = key.get_pressed()
        if keys[K_w] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_s] and self.rect.bottom < WIN_HEIGHT - 5:
            self.rect.y += self.speed

class Player_R(GameSprite):
    score = 0
    def update(self):
        keys = key.get_pressed()
        if keys[K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.bottom < WIN_HEIGHT - 5:
            self.rect.y += self.speed

class Ball(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed, wight, height, direction_x, direction_y):
        super().__init__(player_image, player_x, player_y, player_speed, wight, height)
        self.dx = direction_x
        self.dy = direction_y

    def bounce_from_paddle(self, player, from_left):
        mid = player.rect.inflate(-PADDLE_W // 2, 0)
        if not self.rect.colliderect(mid):
            return
        if from_left and self.dx > 0:
            return
        if not from_left and self.dx < 0:
            return

        self.speed *=1.1
        if from_left:
            self.dx = self.speed
        else:
            self.dx = -self.speed
        half = player.rect.height / 2
        offset = (self.rect.centery - player.rect.centery) / half
        if offset > 1:
            offset = 1
        elif offset < -1:
            offset = -1
        self.dy = (self.speed * offset)

        if from_left:
            self.rect.left = mid.right
        else:
            self.rect.right = mid.left
        kick.play()

    def update(self, player_l, player_r):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.top < 0:
            self.rect.top = 0
            self.dy *= -1
        elif self.rect.bottom > WIN_HEIGHT:
            self.rect.bottom = WIN_HEIGHT
            self.dy *= -1

        self.bounce_from_paddle(player_l, from_left=True)
        self.bounce_from_paddle(player_r, from_left=False)

    def is_outside(self):
        winner = ''
        if self.rect.left >= WIN_WIDTH:
            winner = 'player_l'
        elif self.rect.right <= 0:
            winner = 'player_r'
        return winner

font.init()
class Word(sprite.Sprite):
    def __init__(self,text,x,y,text_size=40,color='red'):
        super().__init__()
        self.image =  font.Font(None, text_size).render(text,True,color)
        self.rect  =  self.image.get_rect(center=(x,y+10))

    def draw(self):
        main_win.blit(self.image, (self.rect.x, self.rect.y))

    def set_text(self, text, text_size=40,color='red'):
        self.image =  font.Font(None, text_size).render(text,True,color)


PADDLE_W = 50
PADDLE_H = 100
PADDLE_MARGIN = 5
player_l = Player_L('рокетка.png', PADDLE_MARGIN, 200, 8, PADDLE_W, PADDLE_H)
player_r = Player_R('рокетка2.png', WIN_WIDTH - PADDLE_MARGIN - PADDLE_W, 200, 8, PADDLE_W, PADDLE_H)
ball = Ball('3D-rendering-sport-icon.png', 200, 200, 4, 50, 50, 4, 4)
count = Word(f'{player_l.score}:{player_r.score}',300,10)

print(resource_path('you_win.ogg'))
mixer.init()  #подключение музыки
mixer.music.load(resource_path("music.ogg"))
mixer.music.set_volume(0.25)
mixer.music.play(loops=-1,)
you_win = mixer.Sound(resource_path('you_win1.ogg'))
game_over = mixer.Sound(resource_path('gamw_over1.ogg'))
kick = mixer.Sound(resource_path('kick.ogg'))
clock = time.Clock()


game = True
finish = False

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
    if finish != True:
        main_win.blit(background, (0, 0))
        player_l.update()
        player_r.update()
        ball.update(player_l, player_r)
        count.draw()
        player_l.reset()
        player_r.reset()
        ball.reset()

        is_out = ball.is_outside()
        if is_out == 'player_l':
            game_over.play()
            player_l.score+=1
            count.set_text(f'{player_l.score}:{player_r.score}')
        elif is_out == 'player_r':
            game_over.play()
            player_r.score+=1
            count.set_text(f'{player_l.score}:{player_r.score}')
    
    display.update()
    clock.tick(fps)