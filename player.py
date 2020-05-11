import pygame

class Player:
    def __init__(self, x, y, radius, colorRGB,leftBorder,rightBorder,lbutton,rbutton,jumpButton):
        self.x = x
        self.y = y
        self.isJump = False
        self.jumpCount = 10
        self.radius = radius
        self.vel = 5
        self.colorRGB = colorRGB
        self.leftBorder = leftBorder
        self.rightBorder = rightBorder
        self.lbutton = lbutton
        self.rbutton = rbutton
        self.jumpButton = jumpButton

    def draw(self,win):
        pygame.draw.circle(win, self.colorRGB, (int(self.x), int(self.y)), self.radius)

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[self.lbutton] and self.x > self.leftBorder + self.vel:  # Ruch lewo/prawo
            self.x -= self.vel
        elif keys[self.rbutton] and self.x < self.rightBorder - self.vel:
            self.x += self.vel

        if not self.isJump:  # Skok
            if keys[self.jumpButton]:
                self.isJump = True
        else:
            if self.jumpCount >= -10:
                self.y -= self.jumpCount * abs(self.jumpCount) * 0.20  # W tych dwóch liniach można
                self.jumpCount -= 0.5  # przeskalować szybkość/wysokość skoku
            else:
                self.isJump = False
                self.jumpCount = 10

    def move_left(self):
        if self.x > self.leftBorder + self.vel:
            self.x -= self.vel

    def move_right(self):
        if self.x < self.rightBorder - self.vel:
            self.x += self.vel

    def jump(self):
        if self.isJump:
            if self.jumpCount >= -10:
                self.y -= self.jumpCount * abs(self.jumpCount) * 0.20  # W tych dwóch liniach można
                self.jumpCount -= 0.5  # przeskalować szybkość/wysokość skoku
            else:
                self.isJump = False
                self.jumpCount = 10