import time
import Bluetooth
import FOD
import TAGBotFinder
import ControlMath
import math
import cv2
import OutputHits

# Variable to initialize the Bluetooth Recieving for troube shooring purposes
# Keep true unless tryna test bluetooth independently
RECIEVING = False

# Initialize Game Mode Variables
RANDOM_GAME_TIME_DELAY = 1

def Basic_Mode(image, hsv, boundary_corners, last_send_time, port, last_sent_mag, max_magnitude):
    # Find enemies, the last true value means find based on pool noodle
    FOD_centers = FOD.FindFO(image, hsv)

    # Find TAG_BOT
    # Method 1: using color Detection
    TAGBot_center = TAGBotFinder.FindTAGBot(image, hsv)

    # Find the total forces applied by the center and the enemies
    mag, direc = ControlMath.getForces(TAGBot_center, FOD_centers, boundary_corners, image, max_magnitude)

    # Send the commands over Bluetooth
    last_send_time, last_sent_mag = Bluetooth.Bluetooth_Send_TAGBot(last_send_time, TAGBot_center, mag, direc, port, last_sent_mag)

    return last_send_time, last_sent_mag

def Therapy_Mode(image, hsv, boundary_corners, last_send_time, therapy_zone, port, last_sent_mag, max_magnitude, output_file, game_cntr, game_start_time):
    # Find TAG_BOT
    # port = 0
    # Method 1: using color Detection
    TAGBot_center = TAGBotFinder.FindTAGBot(image, hsv)

    boundary_coord = boundary_corners[therapy_zone]
    mag, direc = ControlMath.boundary_forcev2(TAGBot_center, boundary_coord, max_magnitude)
    end_point_offset = (int(mag * math.cos(direc)), int(mag * math.sin(direc)))
    end_point = (TAGBot_center[0] + end_point_offset[0], TAGBot_center[1] + end_point_offset[1])
    cv2.arrowedLine(image, TAGBot_center, end_point, (255, 0, 0), 5)

    # Send the commands over Bluetooth
    last_send_time, last_sent_mag = Bluetooth.Bluetooth_Send_TAGBot(last_send_time, TAGBot_center, mag, direc, port, last_sent_mag)

    # If you are at the corner
    if(last_sent_mag == 1):
        # If you recieve Arduino message that you were hit
        if(RECIEVING):
            hit_var = port.readline().decode()
            if(hit_var):
                # if you were hit, add 1 to zone
                therapy_zone += 1
                OutputHits.Write_To_Output_File(output_file, "TherapyMode", game_cntr, game_start_time - time.time())
        else:
            therapy_zone += 1
            OutputHits.Write_To_Output_File(output_file, "TherapyMode", game_cntr, game_start_time - time.time())

    # Find the next boundary corner you need to go to
    therapy_zone = int(math.fmod(therapy_zone, len(boundary_corners)))

    return therapy_zone, last_send_time, last_sent_mag

def Time_Trial(image, hsv, boundary_corners, last_send_time, port, last_sent_mag, game_score, max_magnitude, output_file, game_cntr, game_start_time):
    # Find enemies, the last true value means find based on pool noodle
    FOD_centers = FOD.FindFO(image, hsv)

    # Find TAG_BOT
    # Method 1: using color Detection
    TAGBot_center = TAGBotFinder.FindTAGBot(image, hsv)

    # Find the total forces applied by the center and the enemies
    mag, direc = ControlMath.getForces(TAGBot_center, FOD_centers, boundary_corners, image, max_magnitude)

    if(RECIEVING):
        # If you recieve a hit
        hit_var = port.readline().decode()
        if (hit_var):
            # if you were hit, add 1 to score
            print("Score : " + str(game_score))
            game_score += 1
            OutputHits.Write_To_Output_File(output_file, "TherapyMode", game_cntr, game_start_time - time.time())

    # Send the commands over Bluetooth
    last_send_time, last_sent_mag = Bluetooth.Bluetooth_Send_TAGBot(last_send_time, TAGBot_center, mag, direc, port, last_sent_mag)

    return last_send_time, last_sent_mag, game_score

def Whack_a_Mole(image, hsv, boundary_corners, last_send_time, port, last_sent_mag, game_score, max_magnitude, output_file, game_cntr, game_start_time):
    # Find enemies, the last true value means find based on pool noodle
    FOD_centers = FOD.FindFO(image, hsv)

    # Find TAG_BOT
    # Method 1: using color Detection
    TAGBot_center = TAGBotFinder.FindTAGBot(image, hsv)

    # Find the total forces applied by the center and the enemies
    mag, direc = ControlMath.getForces(TAGBot_center, FOD_centers, boundary_corners, image, max_magnitude)

    if(RECIEVING):
        # If you recieve a hit
        hit_var = port.readline().decode()
        if (hit_var):
            # if you were hit, add 1 to score
            print("Score : " + str(game_score))
            game_score += 1
            OutputHits.Write_To_Output_File(output_file, "TherapyMode", game_cntr, game_start_time - time.time())

        # Every other second randomly decide whether to turn the lights on
        if(math.fmod(int(time.time()), RANDOM_GAME_TIME_DELAY)):
            Bluetooth.Bluetooth_Send_Lights(port)

    # Send the commands over Bluetooth
    last_send_time, last_sent_mag = Bluetooth.Bluetooth_Send_TAGBot(last_send_time, TAGBot_center, mag, direc, port, last_sent_mag)

    return last_send_time, last_sent_mag, game_score