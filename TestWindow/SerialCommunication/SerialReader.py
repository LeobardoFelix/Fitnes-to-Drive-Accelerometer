import serial
import time
BAUD_RATE = 9600


class SerialReader:

    def __init__(self, puerto, baudrate=9600, vectorMaxSize = 20, thresholdMode = 0, dataMode = 0,
                  thresholdIMU=2, topThresholdEOG=500, bottomThresholdEOG=200):
        self.serialLocation = puerto
        self.baudrate = baudrate
        self.vectorMaxSize = vectorMaxSize
        self.thresholdMode = thresholdMode
        self.dataMode = dataMode
        self.thresholdIMU = thresholdIMU
        self.topThresholdEOG = topThresholdEOG
        self.bottomThresholdEOG = bottomThresholdEOG
        self.ser = None  

    def openConection(self):
        self.ser = serial.Serial(self.serialLocation, self.baudrate, timeout=1)
        time.sleep(2)  # Esperar aquí una sola vez, tras abrir la conexión
        self.ser.reset_input_buffer()
        self.sendSignal(str(self.vectorMaxSize)+"\n")
        time.sleep(0.1)
        self.sendSignal(str(self.thresholdMode)+"\n")
        time.sleep(0.1)
        self.sendSignal(str(self.dataMode)+"\n")
        time.sleep(0.1)
        self.sendSignal(str(self.thresholdIMU)+"\n")
        time.sleep(0.1)
        self.sendSignal(str(self.topThresholdEOG)+"\n")
        time.sleep(0.1)
        self.sendSignal(str(self.bottomThresholdEOG)+"\n")
        

    def catchSerial(self):
        if self.ser and self.ser.in_waiting > 0:
            linea = self.ser.readline().decode('utf-8', errors='ignore').rstrip()
            return linea
        return None  

    def closeConection(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def sendSignal(self, data):
        bites = data.encode()
        self.ser.write(bites)
            