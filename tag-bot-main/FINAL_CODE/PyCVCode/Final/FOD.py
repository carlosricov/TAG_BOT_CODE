import numpy as np
import cv2

# Function to find the center point of a set of boundary coordinates
def find_center_point(enemy_points):
    size = len(enemy_points)
    sum_x = 0
    sum_y = 0
    i = 0
    for i in range(size):
        sum_x += enemy_points[i][0]
        sum_y += enemy_points[i][1]

    center_x = sum_x / size
    center_y = sum_y / size
    return (center_x, center_y)

# This function uses color detection in order to find the enemies in the zone
# Returns the coordinates of where those enemies are
# def FindFO(image, hsv, boundary, use_red, use_green, use_blue, use_noodle):
# def FindFO(image, hsv, use_red, use_green, use_blue, use_noodle):
def FindFO(image, hsv):

    # INITIALIZED VARIABLES
    FOD_centers = []

    # # Define the red threshold & apply mask
    # redLow = np.array([136, 87, 111], np.uint8)
    # redHigh = np.array([180, 255, 255], np.uint8)
    # redMask = cv2.inRange(hsv, redLow, redHigh)
    #
    # # Define the green threshold & apply mask
    # greenLow = np.array([25, 52, 72], np.uint8)
    # greenHigh = np.array([102, 255, 255], np.uint8)
    # greenMask = cv2.inRange(hsv, greenLow, greenHigh)
    #
    # # Define blue...
    # blueLow = np.array([94, 80, 2], np.uint8)
    # blueHigh = np.array([120, 255, 255], np.uint8)
    # blueMask = cv2.inRange(hsv, blueLow, blueHigh)
    #
    # # Define pool Noodle...
    # noodleLow = np.array([43, 88, 152], np.uint8)
    # noodleHigh = np.array([58, 142, 255], np.uint8)

    # # Define pool Noodle in atrium @ 4pm
    # noodleLow = np.array([33, 87, 171], np.uint8)
    # noodleHigh = np.array([63, 185, 255], np.uint8)

    # # Define pool Noodle in 202 left side
    # noodleLow = np.array([25, 86, 171], np.uint8)
    # noodleHigh = np.array([63, 180, 255], np.uint8)

    # # Define pool Noodle in 202 left side with shade
    noodleLow = np.array([6, 89, 170], np.uint8)
    noodleHigh = np.array([73, 192, 245], np.uint8)

    # # Define pool Noodle with light...
    # noodleLow = np.array([28, 0, 168], np.uint8)
    # noodleHigh = np.array([60, 81, 255], np.uint8)

    # # Define the orange lid...
    # noodleLow = np.array([28, 0, 168], np.uint8)
    # noodleHigh = np.array([60, 81, 255], np.uint8)

    noodleMask = cv2.inRange(hsv, noodleLow, noodleHigh)

    kernal = np.ones((5, 5), "uint8")
    #
    # redMask = cv2.dilate(redMask, kernal)
    # resRed = cv2.bitwise_and(image, image, mask=redMask)
    #
    # greenMask = cv2.dilate(greenMask, kernal)
    # greenRes = cv2.bitwise_and(image, image, mask=greenMask)
    #
    # blueMask = cv2.dilate(blueMask, kernal)
    # blueRes = cv2.bitwise_and(image, image, mask=blueMask)

    noodleMask = cv2.dilate(noodleMask, kernal)
    noodleRes = cv2.bitwise_and(image, image, mask=noodleMask)

    # Find the noodle based on the noodle size and if the area is within a certain area
    contours, hierarchy = cv2.findContours(noodleMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)

        if (area > 1000):
        # if (area > 1000):
            x, y, w, h = cv2.boundingRect(contour)
            # if (WithinBoundary(boundary, x, y)):
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            enemy_center = ((x + x + w) / 2, (y + y + h) / 2)
            FOD_centers.append(enemy_center)
            #FOD_centers.append((x, y))
            cv2.putText(image, "Noodle", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0))

    return FOD_centers
