import serial
import time 
print("hello")
arduino = serial.Serial(port = 'COM3', baudrate=11520, timeout=.1)

def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data
while True:
    num = input("Test a number for the arduino: ")
    value = write_read(num)
    print(value)