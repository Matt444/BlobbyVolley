import pygame
import math


class Ball:
    def __init__(self, x, y, x_speed, y_speed, radius, freeze=True):
        self.x = x
        self.y = y
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.radius = radius
        self.freeze = freeze
        self.firstTouch = False

    def draw(self, win):
        pygame.draw.circle(win, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

    def move(self, players, gs, w):
        # mechanika piłki
        radius_sum = players[0].radius + self.radius

        dist = [math.sqrt((self.x - players[0].x) ** 2 + (self.y - players[0].y) ** 2),
                math.sqrt((self.x - players[1].x) ** 2 + (self.y - players[1].y) ** 2)]

        for player in range(0, 2):
            if dist[player] <= radius_sum:
                print(dist[player])
                self.freeze = False
                if not gs.player_is_touching_ball[player]:
                    gs.player_is_touching_ball[player] = True
                    if player == 0:
                        gs.left_player_touch()
                    else:
                        gs.right_player_touch()
                    diffx = (self.x + self.radius) - (players[player].x + players[player].radius)
                    diffy = (self.y + self.radius) - (players[player].y + players[player].radius)
                    vel = 12.5;
                    self.x_speed = diffx / (abs(diffx) + abs(diffy)) * vel;
                    self.y_speed = diffy / (abs(diffx) + abs(diffy)) * vel;
            else:
                gs.player_is_touching_ball[player] = False

        if not self.freeze:
            self.x += self.x_speed
            self.y += self.y_speed
            self.y_speed += 0.22;

        if abs(self.x + self.x_speed - 394) < self.radius and self.y + self.y_speed > 200:
            self.x_speed = -self.x_speed
        elif abs(self.x + self.x_speed - 394) < self.radius and self.y + self.y_speed > 200 - self.radius:
            self.y_speed = -self.y_speed
            if self.x + self.x_speed - 394 > 0:
                self.x_speed = abs(self.x_speed)
            else:
                self.x_speed = -abs(self.x_speed)

        if self.x + self.x_speed - self.radius < 0 or self.x + self.x_speed + self.radius > w:
            self.x_speed = -self.x_speed