import serial

# Initialize the Bluetooth
port = serial.Serial("/dev/rfcomm7", baudrate=9600, timeout = 0.05)

while True:
    rcv = port.readline().decode()
    if(rcv == ''):
        y=2+2
    else:
        print("We recieved : " + str(rcv))