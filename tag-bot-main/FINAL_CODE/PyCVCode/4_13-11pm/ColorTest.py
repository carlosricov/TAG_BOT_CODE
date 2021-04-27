import numpy as np
import cv2
import math

cam = cv2.VideoCapture(0)

def empty():
    pass

cv2.namedWindow("HSV")
cv2.resizeWindow("HSV",640,240)
cv2.createTrackbar("Hue Min", "HSV", 0, 179, empty)
cv2.createTrackbar("Hue Max", "HSV", 0, 179, empty)
cv2.createTrackbar("Sat Min", "HSV", 0, 255, empty)
cv2.createTrackbar("Sat Max", "HSV", 255, 255, empty)
cv2.createTrackbar("Val Min", "HSV", 0, 255, empty)
cv2.createTrackbar("Val Max", "HSV", 255, 255, empty)

cv2.namedWindow("Trackbars")
hh='Max'
hl='Min'
wnd = 'Colorbars'


while True:
    _, imgFrame = cam.read()
    hueF = cv2.cvtColor(imgFrame, cv2.COLOR_BGR2HSV)
    # EXIT

    h_min = cv2.getTrackbarPos("Hue Min", "HSV")
    h_max = cv2.getTrackbarPos("Hue Max", "HSV")
    s_min = cv2.getTrackbarPos("Sat Min", "HSV")
    s_max = cv2.getTrackbarPos("Sat Max", "HSV")
    v_min = cv2.getTrackbarPos("Val Min", "HSV")
    v_max = cv2.getTrackbarPos("Val Max", "HSV")

    lower = np.array([h_min, s_min, v_min], np.uint8)
    upper = np.array([h_max, s_max, v_max], np.uint8)
    mask = cv2.inRange(hueF, lower, upper)
    kernal = np.ones((5, 5), "uint8")

    mask2 = cv2.dilate(mask, kernal)
    res = cv2.bitwise_and(imgFrame, imgFrame, mask=mask2)

    # # Define the red threshold & apply mask
    # redLow = np.array([136, 87, 111], np.uint8)
    # redHigh = np.array([180, 255, 255], np.uint8)
    # redMask = cv2.inRange(hueF, redLow, redHigh)

    cv2.imshow("orig", imgFrame)
    #cv2.imshow("hsv", hueF)
    #cv2.imshow("mask", mask2)
    cv2.imshow("res", res)

    contours, hierarchy = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # detect red
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        #
        # if (area > 300):
        #     x, y, w, h = cv2.boundingRect(contour)
        #     imgFrame = cv2.rectangle(imgFrame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        #
        #     cv2.putText(imgFrame, "Color", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))

        M = cv2.moments(contour)

        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

        # Use contour if size is bigger then 1000 and smaller then 50000
        if area > 1000:
            if area < 50000:
                x, y, w, h = cv2.boundingRect(contour)
                approx = cv2.approxPolyDP(contour, 0.001 * cv2.arcLength(contour, True), True)
                # draw contour
                cv2.drawContours(imgFrame, contour, -1, (0, 255, 0), 3)
                # draw circle on center of contour
                # cv2.circle(imgFrame, (cX, cY), 7, (255, 255, 255), -1)
                # perimeter = cv2.arcLength(contour, True)
                # approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
                # # fit elipse
                # _, _, angle = cv2.fitEllipse(contour)
                # P1x = cX
                # P1y = cY
                # length = 35
                #
                # # calculate vector line at angle of bounding box
                # P2x = int(P1x + length * math.cos(math.radians(angle)))
                # P2y = int(P1y + length * math.sin(math.radians(angle)))
                # # draw vector line
                # cv2.line(imgFrame, (cX, cY), (P2x, P2y), (255, 255, 255), 5)
                #
                # # output center of contour
                # print(angle)

                # detect bounding box
                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                # draw bounding box
                cv2.drawContours(imgFrame, [box], 0, (0, 0, 255), 2)
                cv2.putText(imgFrame, "Points: " + str((x, y)), (x + w + 20, y + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

    # EXIT
    cv2.imshow("multiple colors", imgFrame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break