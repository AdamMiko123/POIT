import serial

ser = serial.Serial("/dev/ttyS2")
ser.baudrate = 9600

while True: 
    read_ser = ser.readline()
    print(read_ser)
