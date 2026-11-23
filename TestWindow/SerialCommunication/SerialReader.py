import serial
import time

class SerialReader:
    """
    Lector y decodificador del puerto serial destinado
    a la comunicación con el sistema embebido.

    Attributes:
        serialLocation (str): Locación del puerto de comunicación serial.
        baudrate (int): Tasa de cambios de estados en el que se comunica el puerto serial.
        vectorMaxSize (int): El tamaño de muestras del promedio.
        thresholdMode (bool): El tipo de límite que el sistema toma registrar una reacción; False para un límite estático, True para uno móvil con respecto al promedio.
        dataMode (bool): El tipo de dato que el sistema va capturar; False para la aceleración lineal, True para el valor en el electroculograma. 
        reactionMode (bool): El tipo de dato que toma en cuenta para registrar una reacción; False para el valor del sensor, True para el promedio de la medidas.
        thresholdIMU (float): Límite de la reacción por sensor inercial.
        topThresholdEOG (float): Límite superior de la reacción por electroculograma.
        bottomThresholdEOG (float): Límite superior de la reacción por electroculograma.
        ser (Serial): Puerto de comunicación serial.

    Methods:
        openConection(): Abre conexión con el sistema embebido.
        catchSerial(): Lee la información disponible en el puerto serial.
        closeConnection(): Cierra el puerto de comunicación serial.
        sendSignal(any): Manda un valor por el puerto serial.
    """
    def __init__(self, puerto, baudrate=9600, vectorMaxSize = 20, thresholdMode = 0, dataMode = 0,
                  reactionMode=0, thresholdIMU=2, topThresholdEOG=500, bottomThresholdEOG=200):
        self.serialLocation = puerto
        self.baudrate = baudrate
        self.vectorMaxSize = vectorMaxSize
        self.thresholdMode = thresholdMode
        self.dataMode = dataMode
        self.reactionMode=reactionMode
        self.thresholdIMU = thresholdIMU
        self.topThresholdEOG = topThresholdEOG
        self.bottomThresholdEOG = bottomThresholdEOG
        self.ser = None  

    def openConection(self):
        """
        Abre el puerto serial y manda los datos de configuración
        necesarios para establecer conexión con el sistema embebido.
        """
        self.ser = serial.Serial(self.serialLocation, self.baudrate, timeout=1)
        time.sleep(2)  # Esperar aquí una sola vez, tras abrir la conexión
        self.ser.reset_input_buffer()
        self.sendSignal(str(self.vectorMaxSize)+"\n")
        time.sleep(0.1)
        self.sendSignal(str(self.thresholdMode)+"\n")
        time.sleep(0.1)
        self.sendSignal(str(self.dataMode)+"\n")
        time.sleep(0.1)
        self.sendSignal(str(self.reactionMode)+"\n")
        time.sleep(0.1)
        self.sendSignal(str(self.thresholdIMU)+"\n")
        time.sleep(0.1)
        self.sendSignal(str(self.topThresholdEOG)+"\n")
        time.sleep(0.1)
        self.sendSignal(str(self.bottomThresholdEOG)+"\n")
        time.sleep(0.1)
        

    def catchSerial(self):
        """
        Si hay bytes en espera en el puerto serial, lee y decodifica
        los datos disponibles, en caso contrario regresa None

        Returns:
            linea (str): Cadena de caracteres de los datos recibidos por serial.
        """
        if self.ser and self.ser.in_waiting > 0:
            linea = self.ser.readline().decode('utf-8', errors='ignore').rstrip()
            return linea
        return None  

    def closeConection(self):
        """
        Cierra el puerto de comunicación serial.
        """
        if self.ser and self.ser.is_open:
            self.ser.close()

    def sendSignal(self, data):
        """
        Manda un valor hacia el sistema embebido
        por medio del puerto serial.

        Args:
            data (any): El valor que es mandado por el puerto serial.
        """
        bites = data.encode()
        self.ser.write(bites)

    def sendStartRoundPulse(self):
        """
        Manda un caracter al puerto serial,
        es usado una vez que la conexión ya se ha establecido
        y el sistema ya esta mandando datos. Inicia el timer
        entre la presentación de estimulo hasta la siguiente reacción.
        """
        dato = "1"
        bites = dato.encode()
        self.ser.write(bites)

            