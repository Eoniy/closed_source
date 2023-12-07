# Import
import random
import pygame
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import time
import os


# Initialize
pygame.init()

# Create Window/Display
width, height = 1280, 720
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Balloon Pop")

# Initialize Clock for FPS
fps = 30
clock = pygame.time.Clock()

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # width
cap.set(4, 720)  # height

# Images
imgRedBalloon = pygame.image.load('./Resources/BalloonRed.png').convert_alpha()
imgYellowBalloon = pygame.image.load('./Resources/BalloonYellow.png').convert_alpha()
imgBlueBalloon = pygame.image.load('./Resources/BalloonBlue.png').convert_alpha()
imgBomb = pygame.image.load('Bomb.png').convert_alpha()

rectRedBalloon = imgRedBalloon.get_rect()
rectYellowBalloon = imgYellowBalloon.get_rect()
rectBlueBalloon = imgBlueBalloon.get_rect()
rectBomb = imgBomb.get_rect()

rectRedBalloon.x, rectRedBalloon.y = 500, 300
rectYellowBalloon.x, rectYellowBalloon.y = 500, 300
rectBlueBalloon.x, rectBlueBalloon.y = 500, 300
rectBomb.x, rectBomb.y = 500, 300

# Variables
speedRed = 15
speedYellow = 10
speedBlue = 20
speedBomb = 10

score = 0
startTime = time.time()
totalTime = 60
best_score = 0

best_score_file = 'best_score.txt'
if os.path.exists(best_score_file):
    with open(best_score_file, 'r') as file:
        best_score = int(file.read())

# New variable for controlling bomb frequency
bombFrequency = 0.001  # Adjust this value to control bomb frequency (lower value = fewer bombs)

# Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)


def resetRedBalloon():
    rectRedBalloon.x = random.randint(100, img.shape[1] - 100)
    rectRedBalloon.y = img.shape[0] + 50

def resetYellowBalloon():
    rectYellowBalloon.x = random.randint(100, img.shape[1] - 100)
    rectYellowBalloon.y = img.shape[0] + 50

def resetBlueBalloon():
    rectBlueBalloon.x = random.randint(100, img.shape[1] - 100)
    rectBlueBalloon.y = img.shape[0] + 50

def resetBomb():
    rectBomb.x = random.randint(100, img.shape[1] - 100)
    rectBomb.y = img.shape[0] + 500

# Main loop
start = True
while start:
    # Get Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start = False
            with open(best_score_file, 'w') as file:
                file.write(str(best_score))
            pygame.quit()

    # Apply Logic
    timeRemain = int(totalTime -(time.time()-startTime))
    if timeRemain <0:
        window.fill((255,255,255))

        font = pygame.font.Font('./Resources/Marcellus-Regular.ttf', 50)
        textScore = font.render(f'Your Score: {score}', True, (50, 50, 255))
        textTime = font.render(f'Time UP', True, (50, 50, 255))
        best_score_text = font.render(f'Best Score: {best_score}', True, (50, 50, 255))
        window.blit(best_score_text, (460, 400))
        window.blit(textScore, (450, 330))
        window.blit(textTime, (530, 255))

    else:
        # OpenCV
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)

        rectRedBalloon.y -= speedRed  # Move the balloon up
        rectYellowBalloon.y -= speedYellow
        rectBlueBalloon.y -= speedBlue
        rectBomb.y -= speedBomb
        
        # check if balloon has reached the top without pop
        if rectRedBalloon.y < 0:
            resetRedBalloon()
            speedRed += 1

        if rectYellowBalloon.y < 0:
            resetYellowBalloon()
            speedYellow += 1

        if rectBlueBalloon.y < 0:
            resetBlueBalloon()
            speedBlue += 1
            
        if rectBomb.y < 0:
            resetBomb()
            speedBomb += 1

        if hands:
            hand = hands[0]
            x, y = hand['lmList'][8][0:2]
            
            if rectRedBalloon.collidepoint(x, y):
                resetRedBalloon()
                score += 10
                speedRed += 1

            if rectYellowBalloon.collidepoint(x, y):
                resetYellowBalloon()
                score += 5
                speedYellow += 1

            if rectBlueBalloon.collidepoint(x, y):
                resetBlueBalloon()
                score += 15
                speedBlue += 1

            if rectBomb.collidepoint(x, y):
                resetBomb()
                score -= 20

        if score > best_score:
            best_score = score
            with open('best_score.txt', 'w') as file:
                file.write(str(best_score))


        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgRGB = np.rot90(imgRGB)
        frame = pygame.surfarray.make_surface(imgRGB).convert()
        frame = pygame.transform.flip(frame, True, False)
        window.blit(frame, (0, 0))
        window.blit(imgRedBalloon, rectRedBalloon)
        window.blit(imgYellowBalloon, rectYellowBalloon)
        window.blit(imgBlueBalloon, rectBlueBalloon)
        window.blit(imgBomb, rectBomb)

        font = pygame.font.Font('./Resources/Marcellus-Regular.ttf', 50)
        textScore = font.render(f'Score: {score}', True, (50, 50, 255))
        textTime = font.render(f'Time: {timeRemain}', True, (50, 50, 255))
        window.blit(textScore, (35, 35))
        window.blit(textTime, (1000, 35))

        # Adjust bomb frequency
        if random.random() < bombFrequency:
            resetBomb()

    # Update Display
    pygame.display.update()
    # Set FPS
    clock.tick(fps)