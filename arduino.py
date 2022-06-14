import serial

ser = serial.Serial("/dev/ttyS2")
ser.baudrate = 9600

while True: 
    read_ser = ser.readline()
    read_ser = read_ser.decode()
    print(read_ser)
    if len(read_ser) == 17:
        distance = float(read_ser[:1])
        humidity = float(read_ser[2:7])
        temperature = float(read_ser[8:13])
        photo = float(read_ser[14])
    if len(read_ser) == 18:
        distance = float(read_ser[:2])
        humidity = float(read_ser[3:8])
        temperature = float(read_ser[9:14])
        photo = float(read_ser[15])
    if len(read_ser) == 19:
        distance = float(read_ser[:3])
        humidity = float(read_ser[4:9])
        temperature = float(read_ser[10:15])
        photo = float(read_ser[16])
    if len(read_ser) == 20:
        distance = float(read_ser[:4])
        humidity = float(read_ser[5:10])
        temperature = float(read_ser[11:16])
        photo = float(read_ser[17])
    print(distance)
    print(humidity)
    print(temperature)
    print(photo)
