import cv2
import numpy as np
import time
import math
import BoundaryDetection
import VideoStream
import FOD
import TAGBotFinder
import ControlMath
import pyrebase
import Bluetooth
import Game_Modes
import OutputHits

## Camera settings
# Old : 1280 x 720
IM_WIDTH = 1280
IM_HEIGHT = 720
FRAME_RATE = 10

# INITIALIZED VARIABLES
INITIALIZE_TIME = 4
NUM_QR_CODES = 4

# variables for the different Game Modes
Game_Mode = "Basic_Mode"
game_difficulty = "Easy"
max_magnitude = 50
game_length_time = 60
game_start_time = -1
new_game = True
therapy_zone = 0
game_score = 0
game_cntr = 0

output_file_name = "Tag_Bot_Hits.csv"

last_sent_mag = 0
last_send_time = -2


# BKG_THRESH = 60
frame_rate_calc = 1
freq = cv2.getTickFrequency()
boundary_points = 0
boundary_corners = []
FOD_centers = []
TAGBot_center = (0,0)
boundaries_processed = 0

## Define font to use
font = cv2.FONT_HERSHEY_SIMPLEX
ZONE_RANGE = 50
red = (0, 0, 255)

cam_quit = 0  # Loop control variable

## CHANGE THE THIRD ARGUMENT FROM 1 TO 2 IN THE FOLLOWING LINE:
videostream = VideoStream.VideoStream((IM_WIDTH, IM_HEIGHT), FRAME_RATE, 2, 0).start()
time.sleep(1)  # Give the camera time to warm up

start_time = time.time()

## Confgure the Pi to connect to Firebase
config = {
  "apiKey": "AIzaSyBcuL2qDigb_3q9yu1UaHx7Sw8fpYI-fpU",
  "authDomain": "tag-bot-f4476.firebaseapp.com",
  "databaseURL": "https://tag-bot-f4476-default-rtdb.firebaseio.com/",
  "storageBucket": "tag-bot-f4476.appspot.com"
}

firebase = pyrebase.initialize_app(config)

# Initialize the Bluetooth
port = Bluetooth.Bluetooth_Initialize()

# Initialize the output file
output_file = OutputHits.Initialize_Output_File(output_file_name)

## Continuous Loop
while (cam_quit == 0):

    # Retrieve the current mode from Firebase to the app
    database = firebase.database()
    next_Game_Mode = str(database.child("TAG_Bot").child("Mode").get().val())
    next_Game_Mode = next_Game_Mode[1:len(next_Game_Mode) - 1]
    print("Game " + str(next_Game_Mode))
    print(game_difficulty)
    print(game_length_time)

    # If we started a new game
    # if(next_Game_Mode != Game_Mode or database.child("TAG_Bot").child("Difficulty").get().val() != game_difficulty or database.child("TAG_Bot").child("Time").get().val() != game_length_time):
    if(next_Game_Mode != Game_Mode):
        Game_Mode = next_Game_Mode
        game_start_time = time.time()
        new_game = True
        game_length_time = int(database.child("TAG_Bot").child("Time").get().val())
        game_difficulty = str(database.child("TAG_Bot").child("Difficulty").get().val())
        game_difficulty = game_difficulty[1:len(game_difficulty) - 1]
        last_sent_mag = 0
        game_score = 0
        game_cntr += 1

        # retrieve the max magnitude and set the max magnitude to it
        if(game_difficulty == "Hard"):
            max_magnitude = 100
        elif (game_difficulty == "Medium"):
            max_magnitude = 75
        else:
            max_magnitude = 50

        print("Mode: " + str(next_Game_Mode) + " time: " + str(game_start_time) + " Difficulty " + str(game_difficulty))

    # Grab frame from video stream
    image = videostream.read()

    t1 = cv2.getTickCount()

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Initialize the boundary for certain amount of seconds
    if (time.time() - start_time < INITIALIZE_TIME):
        # Method 1: using color Detection
        BoundaryDetection.FindBoundary(image, hsv, boundary_corners)
        # Method 2: Using QRCode Detection
        # QRCode.find_boundary(image,boundary_corners)

    # Smoothen out the boundary noise
    elif(not boundaries_processed):
        boundary_corners = BoundaryDetection.DSP(boundary_corners)
        boundaries_processed = 1

    # Detect Enemy Objects as well as TAGBot objects
    elif(len(boundary_corners) > 0):

        # This next part draws the boundary box for us
        for boundary_corner in boundary_corners:
            # Draw a circle of red color of thickness -1 px
            image = cv2.circle(image, boundary_corner, ZONE_RANGE, red, -1)

    # Therapy Mode means driving to the 4 corners
    if(Game_Mode == "TherapyMode" and boundaries_processed):
        print("In Therapy Mode")
        if(new_game):
            last_send_time = Bluetooth.Bluetooth_Send_Mode(-1, game_length_time, port)
            therapy_zone = 0
            therapy_zone, last_send_time, last_sent_mag = Game_Modes.Therapy_Mode(image, hsv, boundary_corners,
                                                                                  last_send_time, therapy_zone, port, last_sent_mag,
                                                                                  max_magnitude, output_file, game_cntr, game_start_time)
            new_game = False
        else:
            # new_game = False
            therapy_zone, last_send_time, last_sent_mag = Game_Modes.Therapy_Mode(image, hsv, boundary_corners, last_send_time, therapy_zone, port, last_sent_mag, max_magnitude,
                                                                                  output_file, game_cntr, game_start_time)
    # Basic Mode is the avoidance with no scoring and just base model
    elif(Game_Mode == "BasicMode" and boundaries_processed):
        if(new_game):
            last_send_time = Bluetooth.Bluetooth_Send_Mode(-2, game_length_time, port)
            last_send_time, last_sent_mag = Game_Modes.Basic_Mode(image, hsv, boundary_corners, last_send_time, port, last_sent_mag, max_magnitude)
            new_game = False
        else:
            # Only send commands if game is not done
            # add 2 for the delay between sending
            if(time.time() - game_start_time - 1.5 < game_length_time):
                # new_game = False
                last_send_time, last_sent_mag = Game_Modes.Basic_Mode(image, hsv, boundary_corners, last_send_time, port, last_sent_mag, max_magnitude)

            # Print the post game report
            else:
                EDIT = True
    # Time Trial is to see how many hits you can get in a certain amount of time
    elif (Game_Mode == "TimeTrial" and boundaries_processed):
        if (new_game):
            last_send_time = Bluetooth.Bluetooth_Send_Mode(-3, game_length_time, port)
            last_send_time, last_sent_mag, game_score = Game_Modes.Time_Trial(image, hsv, boundary_corners, last_send_time, port,
                                                                  last_sent_mag, game_score, max_magnitude, output_file, game_cntr, game_start_time)
            new_game = False
        else:
            # Only send commands if game is not done
            # add 2 for the delay between sending
            if (time.time() - game_start_time - 1.5 < game_length_time):
                # new_game = False
                last_send_time, last_sent_mag, game_score = Game_Modes.Time_Trial(image, hsv, boundary_corners, last_send_time,
                                                                      port, last_sent_mag, game_score, max_magnitude, output_file, game_cntr, game_start_time)
            # Print the post game report
            else:
                EDIT = True
    # Whack a Mole is only a hit counts when the lights turn on
    elif (Game_Mode == "WhackAMole" and boundaries_processed):
        if (new_game):

            last_send_time = Bluetooth.Bluetooth_Send_Mode(-4, game_length_time, port)
            last_send_time, last_sent_mag, game_score = Game_Modes.Whack_a_Mole(image, hsv, boundary_corners, last_send_time, port,
                                                                  last_sent_mag, game_score, max_magnitude, output_file, game_cntr, game_start_time)
            new_game = False
        else:
            # Only send commands if game is not done
            # add 2 for the delay between sending
            if (time.time() - game_start_time - 1.5 < game_length_time):
                # new_game = False
                last_send_time, last_sent_mag, game_score = Game_Modes.Whack_a_Mole(image, hsv, boundary_corners, last_send_time, port,
                                                                  last_sent_mag, game_score, max_magnitude, output_file, game_cntr, game_start_time)

            # Print the post game report
            else:
                EDIT = True

    elif (Game_Mode == "STOP" and new_game):
        new_game = False
        last_send_time = Bluetooth.Bluetooth_Send_Stop(port)

    # Places text of the frame rate at the top of the stream
    cv2.putText(image, "FPS: " + str(int(frame_rate_calc)), (10, 26), font, 0.7, (255, 0, 255), 2, cv2.LINE_AA)

    # Display the final image
    cv2.imshow("Image with FPS", image)

    # Calculate framerate
    t2 = cv2.getTickCount()
    time1 = (t2 - t1) / freq
    frame_rate_calc = 1 / time1

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        end_time = time.time()
        total_time = end_time - start_time
        print(total_time)
        cam_quit = 1
        last_send_time = Bluetooth.Bluetooth_Send_Stop(port)

    # If needed to slow down the code:
    # time.sleep(.5)

# Close all windows and close the PiCamera video stream.
cv2.destroyAllWindows()
videostream.stop()