from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import (
    QHBoxLayout, QPushButton, QLabel, QSpinBox,
    QVBoxLayout, QSizePolicy, QWidget, QTableWidget, 
    QTableWidgetItem, QDoubleSpinBox, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from TestWindow.TestRutine.SignalTracker import SignalTracker
emptyFile = "C:/Users/felix/OneDrive/Documents/IMU_Sensor/Interfaz/resources/EmptyTriangle.png"
fillFile = "C:/Users/felix/OneDrive/Documents/IMU_Sensor/Interfaz/resources/FillTriangle.png"
MOVIL_MODE = 1
STATIC_MODE = 0
IMU_MODE = 0
EOG_MODE = 1
BASE_DIR = "./DataSets/Sept2026/sujetos/sujeto"
COLUMN_WIDTH = 100
class ReportWindow(QWidget):
    fillFigure = pyqtSignal()
    emptyFigure = pyqtSignal()
    stopSignal = pyqtSignal()
    reportSignal = pyqtSignal(list)
    def __init__(self, reactionLog=[], puerto=None, vectorSize=20):
        super().__init__()
        self.reactionLog = reactionLog
        headers = ["no_round", "ts_start_round", "ts_end_round", "delta_ts", "reaction"]
        self.resize(len(headers) * (COLUMN_WIDTH+7), (len(reactionLog))*55)
        self.hasEnded = False
        layout = QVBoxLayout()

        #Top controls
        hl1 = QHBoxLayout()
        hl2 = QHBoxLayout()
        hl1.addWidget(QLabel("ROUND NUM:"))

        self.puerto = puerto
        self.vectorSize = vectorSize
        self.currentRound = 1
        self.noRondas = 6
        self.sujeto = 0
        self.isTracking = False
        self.currentDir = BASE_DIR + str(self.sujeto)
        self.noRondasBox = QSpinBox()
        self.noRondasBox.setValue(self.noRondas)
        self.noRondasBox.valueChanged.connect(self.changedRondas)
        hl1.addWidget(self.noRondasBox)

        self.minTime = 3 #En segundos
        hl1.addWidget(QLabel("MIN TIME: "))
        self.minTimeLabel = QSpinBox()
        self.minTimeLabel.setValue(self.minTime)
        self.minTimeLabel.valueChanged.connect(self.changeMinTime)
        hl1.addWidget(self.minTimeLabel)

        self.maxTime = 8 #En segundos
        hl1.addWidget(QLabel("MAX TIME: "))
        self.maxTimeLabel = QSpinBox()
        self.maxTimeLabel.setValue(self.maxTime)
        self.maxTimeLabel.valueChanged.connect(self.changeMaxTime)
        hl1.addWidget(self.maxTimeLabel)

        self.waitTime = 5
        hl1.addWidget(QLabel("WAIT TIME:"))
        self.waitTimeLabel = QSpinBox()
        self.waitTimeLabel.setValue(self.waitTime)
        self.waitTimeLabel.valueChanged.connect(self.changedWaitTime)
        hl1.addWidget(self.waitTimeLabel)

        self.sujeto = 0
        self.currentDir = BASE_DIR + str(self.sujeto)
        hl2.addWidget(QLabel("SUBJECT: "))
        self.subjectLabel = QSpinBox()
        self.subjectLabel.setValue(self.sujeto)
        self.subjectLabel.valueChanged.connect(self.changedSujeto)
        hl2.addWidget(self.subjectLabel)

        self.startBtn = QPushButton("START")
        self.startBtn.clicked.connect(self.startTracking)

        self.stopButton = QPushButton("STOP")
        self.stopButton.clicked.connect(self.stopTracking)

        self.thresholdIMU = 0.3
        hl2.addWidget(QLabel("IMU:"))
        self.thresholdLabel = QDoubleSpinBox()
        self.thresholdLabel.setSingleStep(0.1)
        self.thresholdLabel.setValue(self.thresholdIMU)
        self.thresholdLabel.setDecimals(1)
        self.thresholdLabel.valueChanged.connect(self.changedThreshold)
        hl2.addWidget(self.thresholdLabel)

        self.topThreshEOG = 500
        hl2.addWidget(QLabel("TOP EOG:"))
        self.topThreshEOGLabel = QSpinBox()
        self.topThreshEOGLabel.setMaximum(1000)
        self.topThreshEOGLabel.setSingleStep(10)
        self.topThreshEOGLabel.setValue(self.topThreshEOG)
        self.topThreshEOGLabel.valueChanged.connect(self.changeTopThreshold)
        hl2.addWidget(self.topThreshEOGLabel)

        self.bottomThreshEOG = 200
        hl2.addWidget(QLabel("BOTTOM EOG:"))
        self.bottomThreshEOGLabel = QSpinBox()
        self.bottomThreshEOGLabel.setMaximum(1000)
        self.bottomThreshEOGLabel.setSingleStep(10)
        self.bottomThreshEOGLabel.setValue(self.bottomThreshEOG)
        self.bottomThreshEOGLabel.valueChanged.connect(self.changeBottomThreshold)
        hl2.addWidget(self.bottomThreshEOGLabel)

        self.thresholdMode = STATIC_MODE
        self.modeButton = QPushButton("STATIC MODE")
        self.modeButton.setCheckable(True)
        self.modeButton.clicked.connect(self.changeMode)

        self.dataMode = IMU_MODE
        self.dataButton = QPushButton("IMU")
        self.dataButton.setCheckable(True)
        self.dataButton.clicked.connect(self.changeDataMode)

        hl1.addWidget(self.modeButton)
        hl1.addWidget(self.startBtn)
        hl2.addWidget(self.dataButton)
        hl2.addWidget(self.stopButton)

        layout.addLayout(hl1)
        layout.addLayout(hl2)



        self.mainTable = QTableWidget()
        
        self.mainTable.setColumnCount(len(headers))
        self.mainTable.setRowCount(len(self.reactionLog))
        self.mainTable.setHorizontalHeaderLabels(headers)
        #aux = QSizePolicy.}
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.mainTable.setSizePolicy(sizePolicy)
        self.mainTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        #for i in range(mainTable.rowCount()):
        #    mainTable.setColumnWidth(i, COLUMN_WIDTH)
        #    mainTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        for i, log in enumerate(self.reactionLog):
            for j, content in enumerate(log):
                if 0 < j and j < 4:
                    content = round(content, 3)
                label = QTableWidgetItem(str(content))
                label.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
                #label.setTextAlig(Qt.AlignmentFlag.AlignHCenter)
                self.mainTable.setItem(i, j, label)
        layout.addWidget(self.mainTable)
        btnLayout = QHBoxLayout()
        self.saveBtn = QPushButton("CONTINUE")
        self.rerunBtn = QPushButton("REPEAT")
        btnLayout.addWidget(self.saveBtn)
        btnLayout.addWidget(self.rerunBtn)
        self.saveBtn.clicked.connect(self.saveLog)
        self.rerunBtn.clicked.connect(self.reDoLog)
        layout.addLayout(btnLayout)
        self.setLayout(layout)

    #TODO: Quitar 
    def saveLog(self):
        self.hasEnded = True

        self.signalTracker.isCurrentLogSaved = True
        self.signalTracker.reviewEnded = True
        #self.close()

    def reDoLog(self):
        self.hasEnded = True

        self.signalTracker.isCurrentLogSaved = False
        self.signalTracker.reviewEnded = True
        #self.close()


    #INTERFAZ
    def changedThreshold(self, value):
        self.thresholdIMU = float(value)
        print(f"threshold: {self.thresholdIMU}")

    def changeTopThreshold(self, value):
        self.topThreshEOG = float(value)
        """ #TODO: APPLY THIS TO START
        if self.thresholdMode == STATIC_MODE:
            self.signalTracker.topThresholdEOG = float(value)
        else:
            self.signalTracker.topModEOG = float(value)"""
        print(f"TOP THRESHOLD: {self.topThreshEOG}")

    def changeBottomThreshold(self, value):
        self.bottomThreshEOG = float(value)
        #TODO: APPLY THIS TO START
        """if self.thresholdMode == STATIC_MODE:
            self.signalTracker.bottomThresholdEOG = float(value)
        else:
            self.signalTracker.bottomModEOG = float(value)"""
        print(f"BOTTOM THRESHOLD: {self.bottomThreshEOG}")

    def changeMode(self):
        self.thresholdMode = MOVIL_MODE if self.modeButton.isChecked() else STATIC_MODE
        newText = "MOVIL MODE" if self.modeButton.isChecked() else "STATIC MODE"
        self.modeButton.setText(newText)
        print(f"THRESHOLD MODE: {self.thresholdMode}")

    def changeDataMode(self):
        self.dataMode = EOG_MODE if self.dataButton.isChecked() else IMU_MODE
        newText = "EOG" if self.dataButton.isChecked() else "IMU"
        self.dataButton.setText(newText)
        print(f"DATA MODE CHANGED: {self.dataMode}")
    #Valores de la UI
    def changedRondas(self, value):
        self.noRondas = int(value)
        print(f"RONDAS: {self.noRondas}")
    def changeMinTime(self, value):
        self.minTime = int(value)
        print(f"MIN TIME: {self.minTime}")
    def changeMaxTime(self, value):
        self.maxTime = int(value)
        print(f"MAX TIME: {self.maxTime}")
    def changedWaitTime(self, value):
        self.waitTime = int(value)
        print(f"WAIT TIME:  {self.waitTime}")

    def changedSujeto(self, value):
        self.sujeto = int(value)
        self.currentDir = BASE_DIR + str(self.sujeto)
        print(self.currentDir)
        print(f"SUJETO: {self.sujeto}")

    def updateAll(self):
        self.thresholdIMU = float(self.thresholdLabel.value())
        print(f"threshold: {self.thresholdIMU}")
        self.noRondas = int(self.noRondasBox.value())
        print(f"RONDAS: {self.noRondas}")
        self.minTime = int(self.minTimeLabel.value())
        print(f"MIN TIME: {self.minTime}")
        self.maxTime = int(self.maxTimeLabel.value())
        print(f"MAX TIME: {self.maxTime}")
        self.waitTime = int(self.waitTimeLabel.value())
        print(f"WAIT TIME:  {self.waitTime}")
        self.sujeto = int(self.subjectLabel.value())
        self.currentDir = BASE_DIR + str(self.sujeto)
        print(self.currentDir)
        print(f"SUJETO: {self.sujeto}")
        self.thresholdMode = MOVIL_MODE if self.modeButton.isChecked() else STATIC_MODE
        print(f"THRESHOLD MODE: {self.thresholdMode}")

        self.dataMode = EOG_MODE if self.dataButton.isChecked() else IMU_MODE
        print(f"DATA MODE CHANGED: {self.dataMode}")
        print(f"TOP THRESHOLD: {self.topThreshEOG}")

    def startTracking(self):
        print("START IT")
        self.updateAll()
        if not self.isTracking:
            self.isTracking = True
            self.signalTracker = SignalTracker(self.puerto, 9600,
                self.vectorSize, self.thresholdMode, self.dataMode,
                self.thresholdIMU, self.topThreshEOG, self.bottomThreshEOG, self.currentDir)
            #Thread configuration
            self.trackingThread = QThread()
            self.signalTracker.moveToThread(self.trackingThread)
            self.trackingThread.started.connect(self.signalTracker.trackData)
            #Signals
            self.signalTracker.isTracking = True
            self.signalTracker.emptyFigure.connect(self.emptyFigure.emit)
            self.signalTracker.fillFigure.connect(self.fillFigure.emit)
            self.signalTracker.stopSignal.connect(self.stopTracking)
            self.signalTracker.reportSignal.connect(self.updateTable) #Esta actualiza esta tabla no el triangulo
            self.trackingThread.start()

    def stopTracking(self):
        self.signalTracker.stopThread()
        self.trackingThread.quit()
        self.trackingThread.wait()
        #self.signalTracker = SignalTracker(self.puerto)

    def updateTable(self, newLog):
        self.reactionLog = newLog
        self.setMinimumHeight((len(self.reactionLog))*70)
        rowPos = self.mainTable.rowCount()
        numCol = self.mainTable.columnCount()
        self.mainTable.setRowCount(len(self.reactionLog))
        #aux = QSizePolicy.}
        #sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        #self.mainTable.setSizePolicy(sizePolicy)
        #self.mainTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i, log in enumerate(self.reactionLog):
            for j, content in enumerate(log):
                if 0 < j and j < 4:
                    content = round(content, 3)
                label = QTableWidgetItem(str(content))
                label.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
                #label.setTextAlig(Qt.AlignmentFlag.AlignHCenter)
                self.mainTable.setItem(i, j, label)


    #TODO: En start initialize signalTracker 
#TestWindow/TestRutine/reportWindow.py
"""app = QApplication(sys.argv)
app.setStyle("Fusion")
pruebaLog = [[0,6693.7325156,6698.7338546,5.001339000000371,0],
[1,6702.771452,6703.835072,1.0636199999999008,1],
[2,6710.8934594,6715.8945745,5.001115099999879,0],
[3,6723.947009,6725.2070988,1.2600897999991503,1]]
reportWindow = ReportWindow(pruebaLog)
reportWindow.show()

app.exec()"""