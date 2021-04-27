import numpy as np
import cv2

# INITIALIZED VARIABLES
TAG_Bot_center = (0,0)

# This function uses color detection in order to find the TAG_Bot in the zone
# Returns the coordinates of where those boundaries are
def FindTAGBot(image, hsv):

    # Define the red threshold & apply mask

    # For the white TAG Bot
    # TAGBotLow = np.array([0, 0, 225], np.uint8)
    # TAGBotHigh = np.array([180, 11, 255], np.uint8)

    # For the Orange Lid
    # TAGBotLow = np.array([0, 156, 195], np.uint8)
    # TAGBotHigh = np.array([12, 255, 227], np.uint8)

    # # For the Pink Bag
    # TAGBotLow = np.array([149, 24, 182], np.uint8)
    # TAGBotHigh = np.array([179, 115, 255], np.uint8)

    # # For the Pink Bag in Atrium @ 4pm
    # TAGBotLow = np.array([155, 101, 112], np.uint8)
    # TAGBotHigh = np.array([169, 141, 255], np.uint8)

    # # For the Pink Bag in Atrium @ laterpm
    # TAGBotLow = np.array([155, 101, 112], np.uint8)
    # TAGBotHigh = np.array([169, 150, 255], np.uint8)

    # # For the Pink Bag in Atrium @ laterpm on pi
    TAGBotLow = np.array([155, 101, 112], np.uint8)
    TAGBotHigh = np.array([169, 210, 255], np.uint8)

    TAGBotMask = cv2.inRange(hsv, TAGBotLow, TAGBotHigh)

    kernal = np.ones((5, 5), "uint8")

    TAGBotMask = cv2.dilate(TAGBotMask, kernal)
    resTAGBot = cv2.bitwise_and(image, image, mask=TAGBotMask)

    contours, hierarchy = cv2.findContours(TAGBotMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    TAG_Bot_center = (0,0)

    # detect the TAGBot
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        # change from 1000
        if (area > 500):
            x, y, w, h = cv2.boundingRect(contour)
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 2)
            TAG_Bot_center = (int(x + w/2), int(y + h/2))
            cv2.putText(image, "TAGBot", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))

    return TAG_Bot_center