from TestWindow.SerialCommunication.SerialReader import SerialReader
import time
import threading
import csv
#dataLock = threading.Lock()
MOVIL_MODE = 1
STATIC_MODE = 0
IMU_MODE = 0
EOG_MODE = 1
class SerialConsumer:
    """
    Representación del estado actual y últimos valores relevantes
    del que el sistema embebido pasa por medio del puerto serial.

    Attributes:
        catcher (SerialReader): Lector de puerto serial.
        baseDir (str): Directorio actual donde se guardaran los datos capturados.
        currentValue (float): Último valor leido del puerto serial.
        currentMean (float): Último promedio leído por el puerto serial.
        currentReaction (int): Última bandera de reacción leída por el puerto serial.
        reactionValue (float): Valor de la última reacción leída.
        reactionMean (float): Promedio de la última reacción leída.
        reactionTime (float): Timestamp de la última reacción leída.
        isWriting (bool): Bandera que controla si se esta escribiendo los datos en un archivo.
        isMonitoring (bool): Bandera que controla el inicio y el fin del ciclo de consumo de datos por el serial.
        hasReacted (bool): Bandera que se alza si ha leído una reacción.

    Methods:
        initMonitorThreading(): Inicia el ciclo de consumo del puerto serial en un nuevo hilo.
        stopMonitorThread(): Para el ciclo de consumo y termina el hilo.
        stopWriting(): Para la captura de datos en el archivo CSV.
        startWriting(): Inicia la captura de datos en el archivo CSV.
        stopMonitoring(): Alza la bandera para terminar el ciclo de consumo.
        monitorSerial(): Inicia el archivo CSV y el ciclo de consumo.
    """
    def __init__(self, puerto, baudrate=9600, vectorMaxSize = 20, thresholdMode = 0, dataMode = 0, 
            reactionMode=0, thresholdIMU=2, topThresholdEOG=500, bottomThresholdEOG=200):
        self.puerto = puerto
        self.baudrate = baudrate
        self.vectorMaxSize = vectorMaxSize
        self.thresholdMode = thresholdMode
        self.dataMode = dataMode
        self.reactionMode = reactionMode
        self.thresholdIMU = thresholdIMU
        self.baseDir = "."
        self.fields = ["Aceleración escalar", "Promedio", "Ronda", "Timestamp", "Estimulo"]
        self.currentRound = 0
        if dataMode == EOG_MODE and thresholdMode == MOVIL_MODE:
            self.topModEOG = topThresholdEOG
            self.bottomModEOG = bottomThresholdEOG
        else:
            self.topThresholdEOG = topThresholdEOG
            self.bottomThresholdEOG = bottomThresholdEOG
        
        if self.thresholdMode == STATIC_MODE:
            self.catcher = SerialReader(self.puerto, self.baudrate, self.vectorMaxSize, self.thresholdMode,
            self.dataMode, self.reactionMode, self.thresholdIMU, self.topThresholdEOG, self.bottomThresholdEOG)
        else: #MOVIL_MODE
            self.catcher = SerialReader(self.puerto, self.baudrate, self.vectorMaxSize, self.thresholdMode,
            self.dataMode, self.reactionMode, self.thresholdIMU, self.topModEOG, self.bottomModEOG)
        
        self.currentValue = 0
        self.currentMean = 0
        self.currentTime = 0
        self.currentReaction = 0
        self.reactionValue = 0
        self.reactionMean = 0
        self.reactionTime = 0
        self.isWriting = False
    
        self.hasReacted = False
        self.isMonitoring = True


    def initMonitorThreading(self):
        """
        Inicia el ciclo de consumo del puerto serial en un nuevo hilo.
        """
        self.monitorThread =  threading.Thread(target=self.monitorSerial, name="Monitor_Thread")
        self.monitorThread.start()
    
    def stopMonitorThread(self):
        """
        Para el ciclo de consumo y termina el hilo.
        """
        self.stopMonitoring()
        self.monitorThread.join()

    def stopWriting(self):
        """
        Para la captura de datos en los archivos CSV.
        """
        self.isWriting = False

    def startWriting(self):
        """
        Inicia la captura de datos en los archivos CSV.
        """
        self.isWriting = True

    def monitorSerial(self):
        """
        Inicia la conexión con el puerto serial, crea un archivo
        CSV en el que se guardaran los datos e inicia el ciclo de 
        consumo.

        Exceptions:
            ValueError: Los datos mandados se encuentran corruptos o incompletos.
        """
        self.catcher.openConection()
        dataFileName = self.baseDir + "/MEDIDAS.csv"
        try:
            with open(dataFileName, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(self.fields)
                while self.isMonitoring:
                    values = self.catcher.catchSerial()
                    if self.isWriting:
                        if values:
                            parts = values.split(",")
                            if len(parts) > 2:
                                #with dataLock:
                                self.currentValue, self.currentMean, self.currentReaction = map(float, parts)
                                self.currentTime = time.monotonic()
                                row = [self.currentValue, self.currentMean, self.currentRound, self.currentTime, self.currentReaction]
                                csvwriter.writerow(row)
                                #print(f"WRITING: {self.currentValue}, {self.currentMean}, {self.currentReaction}")
                                if self.currentReaction == 1:
                                    #print("REACCIONO REACCCION REACCIONO REACCIONO")
                                    self.reactionValue = self.currentValue
                                    self.reactionMean = self.currentMean
                                    self.reactionTime = self.currentTime
                                    self.hasReacted = True
                    time.sleep(0.002)
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            self.catcher.closeConection()
    def stopMonitoring(self):
        """
        Alza la bandera para terminar el ciclo de consumo.
        """
        self.isMonitoring = False
