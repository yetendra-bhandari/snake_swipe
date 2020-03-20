#import prerequisites
# for fast push-pop operations on both ends of the snake's body-cells
from collections import deque
import math  # to use the mathematical functions
import numpy as np  # to create an empty 2-D array for the canvas
import cv2  # the OpenCV Library for image processing
import random  # to generate a random number
import time  # to calculate periods of time


def collision(head, body):
    # check if snake's head is in any existing body-cell(excluding the head-cell)
    flag = False  # to ignore the head-cell
    for cell in body:  # loop over every cell in body
        # check if the X & Y coordinates match
        if(flag and cell[0] == head[0] and cell[1] == head[1]):
            return True
        flag = True
    return False


def angle(x, y):
    # return the angle between origin and a pair of coordinates in degrees
    return math.atan2(y, x)*180/math.pi


# approximate lower and upper HSV-values for green color
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
# Begin the video-capture from source('0' means default device i.e. webcam)
cap = cv2.VideoCapture(0)
# Create a 2-D array filled with zeroes of 500px width & height and order 3
img = np.zeros((500, 500, 3), dtype='uint8')
# open a blank window named 'processed_image'
cv2.imshow('Processed_Image', img)
# put text on the empty canvas 'img' at position X=65, Y=250 with thickness of 1px using an in-built font
# of white color(rgb values '255,255,255') and default anti-aliasing mode.
cv2.putText(img, 'Press Any Key To Start', (65, 250),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
# display the generated image 'img' in a new window named 'Snake_Swipe'
cv2.imshow('Snake_Swipe', img)
while(cv2.waitKey(1) == -1):  # wait until the user presses a key
    _, frame = cap.read()  # generate a frame using the input from the video-source
    frame = cv2.flip(frame, 1)  # mirror the original video-feed
    # display the mirrored frame in a new window named 'Video_Feed'
    cv2.imshow('Video_Feed', frame)
img.fill(0)  # once the user presses a key, empty the original canvas.
# place the apple at a random coordinate
apple = [random.randrange(1, 49) * 10, random.randrange(1, 49) * 10]
# initial positions of the snake's body-cells
snake = deque([(250, 250), (260, 250), (270, 250), (280, 250), (290, 250)])
head = [250, 250]  # position of the snake's head-cell
direction = 'l'  # initial direction of the snake's movement
score = 0  # initial score
refresh = 0.2  # set the refresh time of the canvas to 0.2 seconds
# set the end time of the current canvas to the present time + 0.2 seconds
end = time.time() + refresh
coord = deque()  # store the coordinates of the centroids of the contours(edges)
key = -1  # initially no key has been pressed
while(True):  # start an infinite loop
    swipe = '0'  # indicates the initial direction of swipe-gesture
    _, frame = cap.read()  # input a frame from web-cam
    frame = cv2.flip(frame, 1)  # mirror the video feed
    # apply gaussian blur using a kernel size of 11 by 11
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    # generate the hsv-values of the frame
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    # apply 3 types of masking techniques on the image to smooth out the green color
    # in order to make it easy for the OpenCV algorithm to detect the edges
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    # detect contours(edges) in the generated images
    contours, hier = cv2.findContours(
        mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if(len(contours) > 0):  # if any contours exist in the image
        # we find the contour in the frame which has the largest area
        cnt = contours[0]
        area = cv2.contourArea(cnt)  # calculate area of contour
        for c in contours[1:]:
            a = cv2.contourArea(c)
            if a > area:
                cnt = c
                area = a
        if(area > 1000):  # if the largest contour has an area of over 1000px
            # draw the contours on the video-frame in green color i.e rgb(0, 255, 0) with thickness of 3px
            cv2.drawContours(frame, [cnt], 0, (0, 255, 0), 3)
            # generate the moments(centroid) for the given contours
            M = cv2.moments(cnt)
            X = int(M["m10"] / M["m00"])  # X-coordinate of centroid
            Y = int(M["m01"] / M["m00"])  # Y-coordinate of centroid
            # add the coordinates of the new centroid to 'coord'
            coord.append((X, Y))
            if(len(coord) > 6):  # if there exist more than 6 coordinates in 'coord'
                coord.popleft()  # remove the first coordinate in 'coord'
            # Find the direction of swipe by calculating the direction of the movement of centroids
            # difference in X-coordinate of the last and the first centroid
            diffX = coord[-1][0]-coord[0][0]
            # difference in Y-coordinate of the last and the first centroid
            diffY = coord[-1][1]-coord[0][1]
            # if there is a difference of atleast 20px accept it as a swipe
            if(abs(diffX) + abs(diffY) > 20):
                # calculate the angle(in degrees) of the swipe
                ang = angle(diffX, diffY)
                # find the direction of swipe using the value of 'ang'
                if(ang < 30 and ang > -30):
                    swipe = 'r'
                elif(ang > 60 and ang < 120):
                    swipe = 'd'
                elif(ang < -60 and ang > -120):
                    swipe = 'u'
                elif(ang > 150 or ang < -150):
                    swipe = 'l'
    # draw a filled red(0, 0, 255) circle in 'img' at the coordinates of 'apple'
    # using the center coordinates and radius of 5px
    cv2.circle(img, (apple[0] + 5, apple[1] + 5), 5, (0, 0, 255), -1)
    # empty the last coordinates of the snake's head i.e. fill them with black color(0, 0, 0)
    cv2.rectangle(img, (snake[1][0], snake[1][1]),
                  (snake[1][0] + 10, snake[1][1] + 10), (0, 0, 0), -1)
    # draw a filled green(0, 255, 0) rectangle at the snake's head-coordinates
    cv2.rectangle(img, (head[0], head[1]),
                  (head[0] + 10, head[1] + 10), (0, 255, 0), -1)
    # draw a hollow green(0, 255, 0) rectangle at all cell positions of 'snake'
    for cell in snake:
        cv2.rectangle(img, (cell[0], cell[1]),
                      (cell[0] + 10, cell[1] + 10), (0, 255, 0), 1)
    # Open 3 windows to show the generated images
    cv2.imshow('Snake_Swipe', img)
    cv2.imshow('Video_Feed', frame)
    cv2.imshow('Processed_Image', mask)
    pressed = cv2.waitKey(1)  # Capture user input
    if(key == -1 and pressed != -1):  # if a key has not been registered and the user has pressed a key
        key = pressed  # register the pressed key
    if(time.time() < end):  # this ensures that the frame will not be refreshed before refresh time
        continue
    else:
        end += refresh  # set the end time of next frame by 0.2 seconds
        if(key == ord('e')):  # the user can press 'e' to exit the game
            break
        # set the direction of snake's head appropriately
        elif((key == ord('w') or swipe == 'u') and direction != 'd'):
            direction = 'u'
        elif((key == ord('a') or swipe == 'l') and direction != 'r'):
            direction = 'l'
        elif((key == ord('s') or swipe == 'd') and direction != 'u'):
            direction = 'd'
        elif((key == ord('d') or swipe == 'r') and direction != 'l'):
            direction = 'r'
        # move the snake's head in the new direction
        if(direction == 'u'):
            head[1] -= 10
        elif(direction == 'l'):
            head[0] -= 10
        elif(direction == 'd'):
            head[1] += 10
        elif(direction == 'r'):
            head[0] += 10
        # insert the new head-coordinates to the beginning of 'snake'
        snake.insert(0, (head[0], head[1]))
        # check whether the snake's head touches the apple
        if(head[0] == apple[0] and head[1] == apple[1]):
            score += 1  # increment the score counter
            # erase the apple from its last position
            cv2.circle(img, (apple[0] + 5, apple[1] + 5), 5, (0, 0, 0), -1)
            # generate new random position for apple
            apple[0] = random.randrange(1, 49) * 10
            apple[1] = random.randrange(1, 49) * 10
        # check if the snake goes out of the canvas or collides with itself, exit the loop
        elif(head[0] < 0 or head[0] >= 500 or head[1] < 0 or head[1] >= 500 or collision(head, snake)):
            break
        else:
            tail = snake.pop()  # remove the tail-cell of snake
            # erase the tail-cell
            cv2.rectangle(img, (tail[0], tail[1]),
                          (tail[0] + 10, tail[1] + 10), (0, 0, 0), 1)
        key = -1  # reset the key
# when the loop exits display the score in the same window
cv2.putText(img, 'Your Score is {}'.format(score), (115, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
cv2.imshow('Snake_Swipe', img)
# exit the windows not required
cv2.destroyWindow('Video_Feed')
cv2.destroyWindow('Processed_Image')
cap.release()
cv2.waitKey(0)
# exit all windows
cv2.destroyAllWindows()
