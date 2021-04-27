import serial
import time

MAX_TIME_WAIT = 20
SEND_DELAY = 1 # 1
MIN_MAG = 55 #20
MAG_BUFFER = 2.5 # 15

# Variable to initialize the Bluetooth for troube shooring purposes
# Keep true unless tryna test bluetooth independently
USE_BLUETOOTH = True

def Bluetooth_Initialize():
    # Initialize bluetooth port. RfcommX -> replace x with the port #.
    port = 0
    if(USE_BLUETOOTH):
        # port = serial.Serial("/dev/rfcomm11", baudrate=9600)
        port = serial.Serial("/dev/rfcomm0", baudrate=9600, timeout = 0.01)
    return port

# Send the mode over bluetooth
def Bluetooth_Send_Mode(mode, game_length_time, port):
    cmd = str(mode) + "," + str(game_length_time)
    print("Command to pass: " + cmd)
    b = cmd.encode()
    if (USE_BLUETOOTH):
        print("Sending + " + cmd)
        port.write(b)

    last_send_time = time.time()

    return last_send_time

# Send the TAG Bot to turn on the lights
def Bluetooth_Send_Lights(port):
    cmd = str(101) + "," + str(0)
    print("Command to pass: " + cmd)
    b = cmd.encode()
    if (USE_BLUETOOTH):
        print("Sending + " + cmd)
        port.write(b)

    last_send_time = time.time()

    return last_send_time

# Send motor commands to the TAG Bot over BT
def Bluetooth_Send_TAGBot(last_send_time, TAGBot_center, mag, direc, port, last_sent_mag):
    # Prevent Bluetooth message overload.
    print(time.time() - last_send_time)
    if (time.time() - last_send_time > SEND_DELAY and TAGBot_center != (0, 0)):
        # Parse into a coordinate to send to TAG Bot.
        # DSP the Direction
        direc *= -1
        direc += 6.28

        # DSP the mag
        # if(mag == 0):
        #     mag = 1
        # if (mag < MIN_MAG):
        #    mag = 1

        # pre_mag = mag
        # print("mag is " + str(mag))
        # print("lastmag is " + str(last_sent_mag))
        if ((mag <= MIN_MAG) and (mag > 15)):
            # mag = 1
            mag = 50
        elif (mag > MIN_MAG):
            # do nothing
            mag = mag
        else:
            mag = 1

        if(abs(mag - last_sent_mag) >= MAG_BUFFER):
            last_sent_mag = mag
            # last_sent_mag = pre_mag
        else:
            print("The Last Sent Mag is " + str(last_sent_mag) + " and we are trying to send : " + str(mag))
            return last_send_time, last_sent_mag

        cmd = str(mag) + "," + str(direc)
        print("Command to pass: " + cmd)

        last_send_time = time.time()

        # Encode the command into a byte.
        b = cmd.encode()
        if (USE_BLUETOOTH):
            print("Sending + " + cmd)
            port.write(b)
    # elif (time.time() - last_send_time >= MAX_TIME_WAIT):
    #     Bluetooth_Send_Stop(port):

    return (last_send_time, last_sent_mag)

# Tell the TAG Bot to stop
def Bluetooth_Send_Stop(port):
    cmd = str(0) + "," + str(0)
    print("Command to pass: " + cmd)
    # Encode the command into a byte.
    b = cmd.encode()
    if (USE_BLUETOOTH):
        print("Sending + " + cmd)
        port.write(b)