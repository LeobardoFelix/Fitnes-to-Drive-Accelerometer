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
    fillFigure = pyqtSignal()
    emptyFigure = pyqtSignal()
    stopSignal = pyqtSignal()

    def __init__(self, puerto, baudrate=9600, vectorMaxSize = 20, thresholdMode = 0, dataMode = 0,
                  thresholdIMU=2, topThresholdEOG=500, bottomThresholdEOG=200):

        super().__init__()
        self.puerto = puerto
        self.baudrate = baudrate
        self.vectorMaxSize = vectorMaxSize
        self.thresholdMode = thresholdMode
        self.dataMode = dataMode
        self.thresholdIMU = thresholdIMU
        self.reactionLog = []
        if dataMode == EOG_MODE and thresholdMode == MOVIL_MODE:
            self.topModEOG = topThresholdEOG
            self.bottomModEOG = bottomThresholdEOG
        else:
            self.topThresholdEOG = topThresholdEOG
            self.bottomThresholdEOG = bottomThresholdEOG

        self.monitor = SerialConsumer(puerto, baudrate, vectorMaxSize, thresholdMode, dataMode, thresholdIMU, topThresholdEOG, bottomThresholdEOG)
        
        self.isTracking = True
        self.currentRound = 0
        self.baseDir = os.path.join(os.getcwd(), "sujetos")

        self.noRondas = 5
        self.minTime = 5 #En segundos
        self.maxTime = 10 #En segundos
        self.waitTime = 5
        self.sujeto = 0
        self.threshold = .3


    def trackData(self):
        dataFileName = self.baseDir + "/MEDIDAS.csv"
        reactionName = self.baseDir + "/REACCIONES.csv"

        reactFields = ["no_round", "ts_start_round", "ts_end_round", "delta_ts", "reaction"]

        # Check files BEFORE opening
        os.makedirs(self.baseDir, exist_ok=True)

        try:
            with open(reactionName, 'w', newline='') as reactcsvfile:
                #csvwriter = csv.writer(csvfile)
                reactWriter = csv.writer(reactcsvfile)
                #csvwriter.writerow(fields)
                reactWriter.writerow(reactFields)
                print("INICIARAN LAS RONDAS")
                self.currentRound = 0
                #self.catcher.openConection()
                self.monitor.baseDir = self.baseDir
                self.monitor.initMonitorThreading()
                self.monitor.stopWriting()
                for i in range(self.noRondas):
                    self.currentLog = []
                    print("INICIA UNA NUEVA RONDA")
                    if not self.isTracking:
                        break
                    self.currentRound = i
                    self.monitor.currentRound = i
                    self.waitRandom()
                    print("EMPIEZA BUSCAR REACCION")
                    self.waitForReaction()
                    self.monitor.stopWriting()
                    print("TERMINA LA BUSQUEDA DE REACCIÓN")
                    self.emptyFigure.emit()
                    self.checkIfReacted()
                    reactWriter.writerow(self.currentLog)
                    print(f"REACTION LOG: {self.reactionLog}")
                    print(f"RONDA {self.currentRound} TERMINO")

        except Exception as e:
            print("Error in classification:", e)

        finally:
            self.stopSignal.emit()
            self.monitor.stopMonitorThread()
            #self.catcher.closeConection()

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
        self.monitor.startWriting()
        #time.sleep(1)
        
        self.fillFigure.emit()
        
        while (currentTime - startTime) < self.waitTime and self.isTracking:

            if self.monitor.hasReacted:
                valor = self.monitor.reactionValue
                promedio = self.monitor.reactionMean
                ts = self.monitor.reactionTime
                reaccion = 1
                self.currentLog.append(ts)
                self.currentLog.append(ts-self.startRoundTime)
                self.currentLog.append(reaccion)
                self.reactionLog.append(self.currentLog)
                print(f"REACTION: {self.monitor.reactionValue} PROMEDIO: {self.monitor.reactionMean}  TIEMPO: {self.monitor.reactionTime}")
                print(f"{valor}, {promedio}, {ts}, {reaccion}")
                self.monitor.hasReacted = False
                self.reacciono = True
                break
            time.sleep(0.002)
            currentTime = time.monotonic()


    def stopThread(self):
        self.isTracking = False
        print("Cycle stopped and thread finished")

    def checkIfReacted(self):
        if not self.reacciono:
            ts = time.monotonic()
            self.currentLog.append(ts)
            self.currentLog.append(ts-self.startRoundTime)
            self.currentLog.append(0)
            self.reactionLog.append(self.currentLog)
            print(f"NO REACCIONO TS: {ts}")
        else:
            print(f"SI REACCIONO")

# print("ISDOADSIJOD")
# signalMonitor = SignalTracker("COM7")
# signalMonitor.trackData()