import pygame


class ObstacleClass():
    def __init__(self, obstacleRect, movementSpeed):
        self.obstacleRect      = obstacleRect
        self.movementSpeed     = movementSpeed
        self.hasBeenStopped    = False

    def obstacleCollidesWithPlayerF(self, playerRect):
        if self.obstacleRect.colliderect(playerRect):
            return True
        