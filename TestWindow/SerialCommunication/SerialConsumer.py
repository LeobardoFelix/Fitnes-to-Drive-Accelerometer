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
    def __init__(self, puerto, baudrate=9600, vectorMaxSize = 20, thresholdMode = 0, dataMode = 0, 
            thresholdIMU=2, topThresholdEOG=500, bottomThresholdEOG=200):
        self.puerto = puerto
        self.baudrate = baudrate
        self.vectorMaxSize = vectorMaxSize
        self.thresholdMode = thresholdMode
        self.dataMode = dataMode
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
            self.dataMode, self.thresholdIMU, self.topThresholdEOG, self.bottomThresholdEOG)
        else: #MOVIL_MODE
            self.catcher = SerialReader(self.puerto, self.baudrate, self.vectorMaxSize, self.thresholdMode,
            self.dataMode, self.thresholdIMU, self.topModEOG, self.bottomModEOG)
        
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
        self.monitorThread =  threading.Thread(target=self.monitorSerial, name="Monitor_Thread")
        self.monitorThread.start()
    
    def stopMonitorThread(self):
        self.stopMonitoring()
        self.monitorThread.join()

    def stopWriting(self):
        self.isWriting = False

    def startWriting(self):
        self.isWriting = True

    def monitorSerial(self):
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
                                print(f"WRITING: {self.currentValue}, {self.currentMean}, {self.currentReaction}")
                                if self.currentReaction == 1:
                                    #print("REACCIONO REACCCION REACCIONO REACCIONO")
                                    self.reactionValue = self.currentValue
                                    self.reactionMean = self.currentMean
                                    self.reactionTime = self.currentTime
                                    self.hasReacted = True
                    # else:
                    #     print(f"NOT WRITING: {values}")
                    time.sleep(0.002)
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            self.catcher.closeConection()
    def stopMonitoring(self):
        self.isMonitoring = False


#objeto = SerialConsumer("COM7")
#objeto.monitorSerial()