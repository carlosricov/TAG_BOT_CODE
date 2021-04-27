import cv2
import numpy as np
import math

# INITIALIZED VARIABLES
#boundary_centers = []
ZONE_RANGE = 200

## Define font to use
font = cv2.FONT_HERSHEY_SIMPLEX

# Function that removes coordinates that are too close together
# Eventually, may need to change this to a moving average versus the first point I detect
def DSP(coordinates):
    to_be_removed = []

    sorted_coordinates = sorted(coordinates, key=lambda k: [k[0], k[1]])
    i = 0
    j = 0
    for i in range(len(sorted_coordinates)):
        for j in range(i + 1, len(sorted_coordinates)):
            p1 = sorted_coordinates[i]
            p2 = sorted_coordinates[j]

            if(p1[0] > 930):
                stop = 0

            if (p2 in to_be_removed):
                continue
            distance = math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))
            if (distance < ZONE_RANGE):
                to_be_removed.append(p2)

    # using list comprehension to perform task
    res = [i for i in coordinates if i not in to_be_removed]
    return res

# This function uses color detection in order to find the boundaries which will be marked in a certain color
# Returns the coordinates of where those boundaries are
def FindBoundary(image, hsv, boundary_centers):
    # Define white...
    # lower_white = np.array([0,0,168], dtype=np.uint8)
    # upper_white = np.array([172,111,255], dtype=np.uint8)
    # whiteMask = cv2.inRange(hsv, lower_white, upper_white)

    # Define blue...
    # blueLow = np.array([94, 80, 2], np.uint8)
    # blueHigh = np.array([120, 255, 255], np.uint8)
    # blueMask = cv2.inRange(hsv, blueLow, blueHigh)

    # Define Blue on Ground Original
    # blueLow = np.array([90, 31, 147], np.uint8)
    # blueHigh = np.array([120, 150, 255], np.uint8)

    # Define Blue on Table
    # blueLow = np.array([90, 97, 156], np.uint8)
    # blueHigh = np.array([120, 230, 255], np.uint8)

    # Define Blue on Atrium FLoor @ 4pm
    # blueLow = np.array([90, 127, 65], np.uint8)
    # blueHigh = np.array([120, 209, 255], np.uint8)

    # Define blue in HEC 119 @ 25%
    # blueLow = np.array([90, 101, 65], np.uint8)
    # blueHigh = np.array([120, 209, 255], np.uint8)

    # Define blue in eng 202 left side
    # blueLow = np.array([90, 65, 0], np.uint8)
    # blueHigh = np.array([120, 100, 150], np.uint8)

    # Define blue in eng 202 left side with shade
    blueLow = np.array([90, 0, 0], np.uint8)
    blueHigh = np.array([134, 161, 102], np.uint8)

    blueMask = cv2.inRange(hsv, blueLow, blueHigh)

    kernal = np.ones((5, 5), "uint8")

    # whiteMask = cv2.dilate(whiteMask, kernal)
    # resWhite = cv2.bitwise_and(image, image, mask=whiteMask)

    blueMask = cv2.dilate(blueMask, kernal)
    blueRes = cv2.bitwise_and(image, image, mask=blueMask)

    # Detecting contours in image based on area of detected object.
    # contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # contours, _ = cv2.findContours(whiteMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours, _ = cv2.findContours(blueMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if (area > 500):
            x, y, w, h = cv2.boundingRect(cnt)
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

            boundary_center = (int(x+w/2), int(y+h/2))

            cv2.putText(image, "Boundary " + str(boundary_center), boundary_center , cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))
            if(boundary_center not in boundary_centers):
                boundary_centers.append(boundary_center)

    return boundary_centers