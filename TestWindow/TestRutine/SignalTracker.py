from TestWindow.SerialCommunication.SerialReader import SerialReader
import os
import csv
from PyQt6.QtCore import QObject, pyqtSignal
import random
from TestWindow.SerialCommunication.SerialConsumer import SerialConsumer
import time

#dataLock = threading.Lock()
READ_LINEAR_ACCELERATION = b":41\n"
GET_EULER = b":1\n"
GET_QUATERNION = b":0\n"
SET_BASE_OFFSET_TO_CURRENT_POSITION = b":19\n"
GET_BAUD_RATE = b":232\n" #NO AFECTA EN BLUETOOTH
SET_BAUD_RATE = b":231,115200\n" #NO AFECTA EN BLUETOOTH
FRONT_NAME = "./sujetos/FRENTE.csv"
SIDE_NAME = "./sujetos/SIDE.csv"
CLASSIFY_NAME = "./sujetos/CLASSIFICACTION.csv"
SET_AUTOCALIBRATION_MODE = b":171,0\n"
GET_AUTOCALIBRATION_MODE = b":172\n"
GET_AUTOCALIBRATION_FACTORS = b":174\n"
TARE_ORIENTATION = b":96\n"

MOVIL_MODE = 1
STATIC_MODE = 0
IMU_MODE = 0
EOG_MODE = 1
FRECUENCIA = 30
PERIODO = 1/FRECUENCIA
class SignalTracker(QObject):
    """
    Monitor de reacciones, por rondas se comunica con un puerto serial
    esperando por una bandera de reacción capturando el resultado en un
    archivo CSV, actualizando la interfaz en proceso.

    Attributes:
        serialConsumer (SerialConsumer): Datos actuales del puerto serial.
        isTracking (bool): Bandera que controla si se termina el monitoreo.
        reactionLog (list): Lista de vectores con los valores de las reacciones.
        isCurrentLogSaved (bool): Bandera que indica si al final de una ronda se salva el vector de valores o se vuelve a tomar la reacción.
        reviewEnded (bool): Bandera que indica cuando puede progresar con la siguiente ronda.
        currentRound (int): Indice de la ronda actual.
        baseDir (str): Directorio donde se guardaran los datos del reactionLog.
        noRondas (int): Cantidad de rondas de monitoreo de reacción.
        minTime (int): Tiempo mínimo de espera entre rondas.
        maxTime (int): Tiempo máximo de espera entre rondas.
        waitTime (int): Tiempo de presentación del estímulo visual.
    Methods: 
        trackData(): Inicia la rutina de monitoreo de reacciones.
        stopThread(): Termina la rutina de monitoreo abruptamente.
    """


    fillFigure = pyqtSignal()
    emptyFigure = pyqtSignal()
    stopSignal = pyqtSignal()
    reportSignal = pyqtSignal(list)
    stopLedSignal = pyqtSignal()
    continueLedSignal = pyqtSignal()
    

    def __init__(self, puerto, baudrate=9600, vectorMaxSize = 20, thresholdMode = 0, dataMode = 0,
                  reactionMode=0, thresholdIMU=2, topThresholdEOG=500, bottomThresholdEOG=200, currentDir=None):

        super().__init__()
        self.puerto = puerto
        self.baudrate = baudrate
        self.vectorMaxSize = vectorMaxSize
        self.thresholdMode = thresholdMode
        self.dataMode = dataMode
        self.reactionMode = reactionMode
        self.thresholdIMU = thresholdIMU
        self.reactionLog = []
        self.isCurrentLogSaved = False
        self.reviewEnded = False
        if dataMode == EOG_MODE and thresholdMode == MOVIL_MODE:
            self.topModEOG = topThresholdEOG
            self.bottomModEOG = bottomThresholdEOG
        else:
            self.topThresholdEOG = topThresholdEOG
            self.bottomThresholdEOG = bottomThresholdEOG

        self.serialConsumer = SerialConsumer(puerto, baudrate, vectorMaxSize, 
                thresholdMode, dataMode, reactionMode, thresholdIMU, topThresholdEOG, bottomThresholdEOG)
        
        self.isTracking = True
        self.currentRound = 0
        self.baseDir = os.path.join(os.getcwd(), "sujetos") if currentDir == None else currentDir

        self.noRondas = 5
        self.minTime = 5 #En segundos
        self.maxTime = 10 #En segundos
        self.waitTime = 5
        self.sujeto = 0
        self.threshold = .3


    def trackData(self):
        """
        Inicia la rutina de monitoreo de reacciones, por
        noRondas cantidad de rondas la rutina espera
        una cantidad de segundos aleatoria entre minTime y masTime,
        muestre el estímulo por waitTime segundos, si el usuario reacciona
        antes de waitTime la ronda termina antes y guarda la reacción, 
        caso contrario se guarda en el reactionLog como si no hubiera reaccionado. 
        """
        dataFileName = self.baseDir + "/MEDIDAS.csv"
        reactionName = self.baseDir + "/REACCIONES.csv"

        reactFields = ["no_round", "ts_start_round", "ts_end_round", "delta_ts", "embeded_time", "reaction"]

        # Check files BEFORE opening
        os.makedirs(self.baseDir, exist_ok=True)

        try:
            with open(reactionName, 'w', newline='') as reactcsvfile:
                #csvwriter = csv.writer(csvfile)
                self.continueLedSignal.emit()
                reactWriter = csv.writer(reactcsvfile)
                #csvwriter.writerow(fields)
                reactWriter.writerow(reactFields)
                print("INICIARAN LAS RONDAS")
                self.currentRound = 0
                #self.catcher.openConection()
                self.serialConsumer.baseDir = self.baseDir
                self.serialConsumer.initMonitorThreading()
                self.serialConsumer.stopWriting()
                for i in range(self.noRondas):
                    self.isCurrentLogSaved = False
                    while not self.isCurrentLogSaved:
                        print("INICIA UNA NUEVA RONDA")
                        self.currentLog = []
                        if not self.isTracking:
                            break
                        self.currentRound = i
                        self.serialConsumer.currentRound = i
                        self.waitRandom()
                        print("EMPIEZA BUSCAR REACCION")
                        self.waitForReaction()
                        self.serialConsumer.stopWriting()
                        print("TERMINA LA BUSQUEDA DE REACCIÓN")
                        self.emptyFigure.emit()
                        self.checkIfReacted()
                        self.reviewRound()
                        if self.isCurrentLogSaved:
                            print("Paso revision")
                            self.reactionLog.append(self.currentLog)
                            reactWriter.writerow(self.currentLog)
                            print(f"REACTION LOG: {self.reactionLog}")
                            print(f"RONDA {self.currentRound} TERMINO")
                        else:
                            print(f"No paso revision DE NUEVO, REPITE RONDA {self.currentRound}")
                    

        except Exception as e:
            print("Error in classification:", e)

        finally:
            self.stopSignal.emit()
            self.serialConsumer.stopMonitorThread()

    def waitRandom(self):
        esperaActual  = random.randint(self.minTime, self.maxTime)
        startTime = time.monotonic()
        currentTime = time.monotonic()
        self.emptyFigure.emit()
        while (currentTime - startTime) < esperaActual:
            time.sleep(.1)
            currentTime = time.monotonic()

    def waitForReaction(self):
        
        self.reacciono = False
        #Marca el momento del estimulo
        startTime = time.monotonic()
        currentTime = time.monotonic()
        self.startRoundTime = currentTime
        self.currentLog.append(self.currentRound)
        self.currentLog.append(self.startRoundTime)
        print(f"RONDA: {self.currentRound} TS: {currentTime}  REACCION: 0")
        self.serialConsumer.startWriting()
        #time.sleep(1)
        self.serialConsumer.startRound()
        self.fillFigure.emit()
        
        while (currentTime - startTime) < self.waitTime and self.isTracking:

            if self.serialConsumer.hasReacted:
                valor = self.serialConsumer.reactionValue
                promedio = self.serialConsumer.reactionMean
                embededTS = self.serialConsumer.reactionTime
                pcTs = self.serialConsumer.reactionPCTime
                reaccion = 1
                self.currentLog.append(pcTs)
                self.currentLog.append(pcTs-self.startRoundTime)
                self.currentLog.append(embededTS)
                self.currentLog.append(reaccion)
                print(f"REACTION: {self.serialConsumer.reactionValue} PROMEDIO: {self.serialConsumer.reactionMean}  PC_TS: {self.serialConsumer.reactionPCTime} EMBEDED_TS: {self.serialConsumer.reactionTime}")
                print(f"{valor}, {promedio}, {embededTS}, {pcTs}, {reaccion}")
                self.serialConsumer.hasReacted = False
                self.reacciono = True
                break
            time.sleep(0.002)
            currentTime = time.monotonic()


    def stopThread(self):
        """
        Termina la rutina de monitoreo abruptamente.
        """
        self.isTracking = False
        print("Cycle stopped and thread finished")

    def checkIfReacted(self):
        if not self.reacciono:
            ts = time.monotonic()
            self.currentLog.append(ts)
            self.currentLog.append(ts-self.startRoundTime)
            self.currentLog.append(self.serialConsumer.currentTime)
            self.currentLog.append(0)
            print(f"NO REACCIONO TS: {ts}")
        else:
            print(f"SI REACCIONO")

    def reviewRound(self):
        self.reviewEnded = False
        preliminarLog = []
        for log in self.reactionLog:
            preliminarLog.append(log)
        #preliminarLog = self.reactionLog
        preliminarLog.append(self.currentLog)
        self.reportSignal.emit(preliminarLog)
        print("EJECUTADO")
        #Espera hasta que le diga que continue
        self.stopLedSignal.emit()
        while not self.reviewEnded:
            time.sleep(1)
        self.continueLedSignal.emit()

        if self.isCurrentLogSaved:
            print("SALVADO")
            return True
        else:
            print("DE NUEVO")
            return False