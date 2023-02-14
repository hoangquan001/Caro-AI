import pygame
import threading as th
import sys
from gameUI import *
from board import *

from config import *
################## SETTING FOR COMPONENT ####################
# PYGAME
pygame.init()
pygame.display.set_caption("Game Caro")
screen = pygame.display.set_mode((1080, 660))
clock = pygame.time.Clock()

FPS = 30

# Define Constance

isRuning = True
gridObject = GridObject()
boardObject = BoardOject()
# menuObject = Menu()
boardGame = BoardGame()
UndoButton = Button(pygame.Rect(50, 600, 100, 40))


# UNDO BUTTON
UndoButton.addText("Undo",)


def undoButtonOnclick():
    boardObject.Undo = True


UndoButton.onMouseClick = undoButtonOnclick


# BOARD OBJECT
boardObject.setBoard(boardGame)


listObjects: list[GameObject] = [
    gridObject, boardObject, UndoButton]


################## RUN GAME ####################
while isRuning:
    screen.fill(BackgroundColor)

    # Draw Object and Update
    for object in listObjects:
        object.update()
        object.drawObject(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRuning = False
            sys.exit(1)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos_click = pygame.mouse.get_pos()
            # print(pos_click)
            for object in listObjects:
                if(object.shape.collidepoint(pos_click)):
                    object.onMouseClick()

    pygame.display.update()
    clock.tick(FPS)
