
import pygame
from pygame import draw
from pygame import Color
import numpy as np
import pygame
from config import *
from board import *


# INTERFACE FOR GAME OBJECT  #
class GameObject(object):
    shape = pygame.Rect(0, 0, 0, 0)

    def drawObject(self, surface: pygame.surface.Surface):
        pass

    # call every frame
    def update(self):

        pass

    # call every 0.02s
    def fixedUpdate(self):
        pass

    # evet
    def onMouseClick(self):
        pass


class GridObject(GameObject):
    def __init__(self, shape=pygame.Rect(210, 0, 660, 660)):
        self.shape = shape
        self.mouse_pos = (0, 0)

    def drawMouseHoverOnGrid(self, surface: pygame.surface.Surface):
        if(self.shape.collidepoint(self.mouse_pos)):
            idX, inY = (
                self.mouse_pos[0]-210)//CellSize[0], (self.mouse_pos[1])//CellSize[1]
            pygame.draw.rect(surface, HoverColor,
                             (idX*CellSize[0]+211, inY*CellSize[1]+1, CellSize[0]-1, CellSize[1]-1))

    def drawGrid(self, surface: pygame.surface.Surface):
        pygame.draw.rect(surface, (255, 255, 255), self.shape)
        smallfont = pygame.font.SysFont('Arial', 20)
        for row in range(21):
            draw.line(surface, BlackColor,
                      (self.shape.left, row*CellSize[0]), (self.shape.right, row*CellSize[0]))
            # if row == 20:
            #     continue
            # text = smallfont.render(str(row), True, (0, 0, 0))
            # surface.blit(text, (180, row*CellSize[0]+5))

        for col in range(21):
            draw.line(surface, BlackColor,
                      (self.shape.left+col*CellSize[0], self.shape.top), (self.shape.left+col*CellSize[0], self.shape.bottom))
            # if col == 20:
            #     continue
            # text = smallfont.render(str(col), True, (0, 0, 0))
            # surface.blit(text, (self.shape.left+col*CellSize[0]+5, 660))

    def drawObject(self, surface: pygame.surface.Surface):
        self.drawGrid(surface)
        self.drawMouseHoverOnGrid(surface)

    def update(self):
        self.mouse_pos = pygame.mouse.get_pos()
        pass


class Button(GameObject):
    def __init__(self, shape=pygame.Rect(0, 0, 0, 0), color=(100, 100, 100), text=None):
        self.shape = shape
        self.text = text
        self.color = color
        self.isVisible = True

    def addText(self, text: str, fontSize=25, fontColor=(34, 34, 255)):
        smallfont = pygame.font.SysFont('Corbel', fontSize)
        self.text = smallfont.render(text, True, fontColor)

    def drawOnHover(self, surface):
        pygame.draw.rect(surface, (0, 255, 255), self.shape)
        if(self.text):
            surface.blit(self.text, self.shape)

    def drawObject(self, surface: pygame.surface.Surface):
        if(self.isVisible):
            pygame.draw.rect(surface,   self.color, self.shape)
            if(self.text):
                surface.blit(self.text, self.shape)
            pos_click = pygame.mouse.get_pos()
            if self.shape.collidepoint(pos_click):
                self.drawOnHover(surface)


class TimeCounter:

    TimeLoss = 60*1000
    startTime = pygame.time.get_ticks()
    expireTime = startTime + 60*1000
    curPlayer = O

    @classmethod
    def uplatePlayer(cls, curentPlayer):
        if(cls.curPlayer != curentPlayer):
            cls.startTime = pygame.time.get_ticks()
            cls.endTime = cls.startTime + 60*1000
            cls.curPlayer = curentPlayer
    #

    @classmethod
    def get_tick(cls):
        return (pygame.time.get_ticks()-cls.startTime) // 1000

    @classmethod
    def reset(cls):
        cls.startTime = pygame.time.get_ticks()
        cls.endTime = cls.startTime + 60*1000

    @classmethod
    def isExpiredTime(cls):
        return (pygame.time.get_ticks() > cls.expireTime)


# class Menu(GameObject):
#     def __init__(self):
#         self.shape = pygame.Rect(200, 200, 200, 200)

#     def drawObject(self, surface: pygame.surface.Surface):
#         pygame.draw.rect(surface, (56, 56, 56), self.shape)
#         pass

#     def update(self):
#         pass
#         # print(pygame.time.get_ticks())


class BoardOject(GameObject):
    def __init__(self):
        self.shape = pygame.Rect(210, 0, 660, 660)
        self.X_Img = pygame.transform.scale(
            pygame.image.load("./asset/X15.png"), CellSize)
        self.O_Img = pygame.transform.scale(
            pygame.image.load("./asset/O15.png"), CellSize)
        self.Undo = False
        self.prePlayer = X
        self.isStart = False
        self.newGameBtn = Button(pygame.Rect(
            390, 280, 300, 100), color=(222, 0, 255))
        self.newGameBtn.addText("New Game")

        def newgameevent():
            self.isStart = True
            self.newGameBtn.isVisible = False
            self.Board.reset()
        self.newGameBtn.onMouseClick = newgameevent

    def setBoard(self, board: BoardGame):
        self.Board = board

    def onMouseClick(self):
        if(self.isStart):
            if(self.Board.player == O):
                pos_click = pygame.mouse.get_pos()
                idY, idX = int((pos_click[0]-self.shape.left)/CellSize[0]
                               ), int(pos_click[1]/CellSize[0])
                self.Board.PlayerOGo((idX, idY))
        else:
            pos_click = pygame.mouse.get_pos()
            if(self.newGameBtn.shape.collidepoint(pos_click)):
                self.newGameBtn.onMouseClick()

    def drawObject(self, surface: pygame.surface.Surface):
        if(self.Board.isWin):
            for pos in self.Board.Line:
                pygame.draw.rect(surface, (255, 0, 0),
                                 (self.shape.left+pos[1]*CellSize[0]+1, self.shape.top + pos[0]*CellSize[1]+1, CellSize[0]-1, CellSize[1]-1))

        for i in range(self.Board.nRow):
            for j in range(self.Board.nCol):
                img = None
                if(self.Board[i, j] == X):
                    img = self.X_Img
                if(self.Board[i, j] == O):
                    img = self.O_Img

                if(img):
                    surface.blit(
                        img, (self.shape.left + j*CellSize[0], i*CellSize[1]))
        if self.isStart:

            smallfont = pygame.font.SysFont('Arial', 40)
            text = smallfont.render(
                str(TimeCounter.get_tick()), True, (200, 0, 0))
            if(self.Board.player == X):
                surface.blit(text, (970, 110))
            else:
                surface.blit(text, (100, 110))
        self.newGameBtn.drawObject(surface)

    def update(self):
        if(self.Board.isWin):
            self.isStart = False
            self.newGameBtn.isVisible = True

        if(self.prePlayer != self.Board.player):
            TimeCounter.reset()
            self.prePlayer = self.Board.player

        if(self.Board.player == X):
            self.Board.PlayerXGo()

        if(self.Undo):
            self.Board.undo()
            self.Undo = False
        # print(pygame.time.get_ticks())
