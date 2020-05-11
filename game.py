import pygame
from textpanel import TextPanel

class Game:
    def __init__(self):
        self.left_player_points = 0
        self.right_player_points = 0
        self.left_player_touches = 0
        self.right_player_touches = 0
        self.last_win_player = 1
        self.player_is_touching_ball = [False, False]
        self.left_player_name = "Player1"
        self.right_player_name = "Player2"
        self.pause = False

    def left_player_got_point(self):
        print("left_player got point")
        self.left_player_points += 1
        self.last_win_player = 1

    def right_player_got_point(self):
        print("right_player got point")
        self.right_player_points += 1
        self.last_win_player = 2

    def left_player_touch(self):
        self.right_player_touches = 0
        self.left_player_touches += 1
        print("left_player_touch")

    def right_player_touch(self):
        self.left_player_touches = 0
        self.right_player_touches += 1
        print("right_player_touch")

    def is_game_over(self):
        if abs(self.left_player_points - self.right_player_points) >= 2:
            if self.left_player_points >= 15:
                return True
            elif self.right_player_points >= 15:
                return True
        else:
            return False

    def show_stats(self,w,h,win):
        text1 = self.left_player_name + ': ' + str(self.left_player_points)
        text2 = self.right_player_name + ': ' + str(self.right_player_points)
        if self.last_win_player == 1:
            text1 += '!'
        else:
            text2 += '!'
        left_player_score = TextPanel(w//4, 20,"comicsans" , 32, text1, (0, 0, 0))
        right_player_score = TextPanel(w // 2 + w // 4, 20, "comicsans", 32, text2, (0, 0, 0))
        left_player_score.draw(win)
        right_player_score.draw(win)


def reset(left_player, right_player, ball, gs, w):  # Reset gry
    left_player.x = 70
    left_player.y = 414
    right_player.x = w - 70
    right_player.y = 414
    left_player.isJump = False
    right_player.isJump = False
    left_player.jumpCount = 10
    right_player.jumpCount = 10
    ball.x_speed = 0
    ball.y_speed = 0
    ball.freeze = True
    ball.firstTouch = False
    ball.y = 250
    gs.left_player_touches = 0
    gs.right_player_touches = 0

def check_game_state(ball,left_player,right_player,gs,w):
    if ball.y > 444 - ball.radius:  # Sprawdzanie czy piłka upadła
        if ball.x < w / 2:
            right_player_win(left_player, right_player, ball, gs, w)
        else:
            left_player_win(left_player, right_player, ball, gs, w)

    elif gs.left_player_touches == 4:
        right_player_win(left_player, right_player, ball, gs, w)

    elif gs.right_player_touches == 4:
        left_player_win(left_player, right_player, ball, gs, w)
    else:
        pass

def left_player_win(left_player, right_player, ball, gs, w):
    gs.left_player_got_point()
    ball.x = 200
    ball.y = 200
    print("left_player ", gs.left_player_points, ":", gs.right_player_points, "right_player")
    reset(left_player, right_player, ball, gs, w)

def right_player_win(left_player, right_player, ball, gs, w):
    gs.right_player_got_point()
    ball.x = w - 200
    ball.y = 200
    print("left_player ", gs.left_player_points, ":", gs.right_player_points, "right_player")
    reset(left_player, right_player, ball, gs, w)