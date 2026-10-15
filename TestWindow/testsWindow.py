from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QSizePolicy, QDoubleSpinBox
)

from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QTimer, QThread
from TestWindow.TestRutine.SignalTracker import SignalTracker
from TestWindow.TestRutine.reportWindow import ReportWindow
print("Inicio de aplicación")
emptyFile = "C:/Users/felix/OneDrive/Documents/IMU_Sensor/Interfaz/resources/EmptyTriangle.png"
fillFile = "C:/Users/felix/OneDrive/Documents/IMU_Sensor/Interfaz/resources/FillTriangle.png"
MOVIL_MODE = 1
STATIC_MODE = 0
IMU_MODE = 0
EOG_MODE = 1
class TestsWindow(QWidget):
    def __init__(self, puerto):
        super().__init__()
        #self.tracker = imuTracker()
        self.puerto = puerto

        self.signalTracker = SignalTracker(self.puerto)
        self.baseDir = "./DataSets/Sept2026/sujetos/sujeto"
        self.pic = QLabel()
        self.pixmap = QtGui.QPixmap()
        self.pixmap.load(emptyFile)

        self.setWindowTitle("Proyecto")
        self.showMaximized()
        mainLayout = QVBoxLayout()
        hl1 = QHBoxLayout()
        hl2 = QHBoxLayout()

        #Top controls
        hlayout = QHBoxLayout()
        hl1.addWidget(QLabel("ROUND NUM:"))

        self.currentRound = 1
        self.noRondas = 6
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
        directorio = self.baseDir + str(self.sujeto)
        self.signalTracker.baseDir = directorio
        hl2.addWidget(QLabel("SUBJECT: "))
        self.subjectLabel = QSpinBox()
        self.subjectLabel.setValue(self.sujeto)
        self.subjectLabel.valueChanged.connect(self.changedSujeto)
        hl2.addWidget(self.subjectLabel)

        self.calBtn = QPushButton("CALIBRATE")
        self.calBtn.clicked.connect(self.calibrate)
        hlayout.addWidget(self.calBtn)

        self.startBtn = QPushButton("START")
        self.startBtn.clicked.connect(self.startClassification)
        hlayout.addWidget(self.startBtn)

        self.stopButton = QPushButton("STOP")
        self.stopButton.clicked.connect(self.stop)
        hlayout.addWidget(self.stopButton)

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
        hlayout.addWidget(self.modeButton)

        self.dataMode = IMU_MODE
        self.dataButton = QPushButton("IMU")
        self.dataButton.setCheckable(True)
        self.dataButton.clicked.connect(self.changeDataMode)
        hlayout.addWidget(self.dataButton)

        hl1.addWidget(self.modeButton)
        hl1.addWidget(self.startBtn)
        hl2.addWidget(self.dataButton)
        hl2.addWidget(self.stopButton)

        #Imagen
        self.pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pic.setSizePolicy(QSizePolicy.Policy.Expanding    , QSizePolicy.Policy.Expanding)
        imageLayout = QHBoxLayout()
        imageLayout.addWidget(self.pic)
        mainLayout.addLayout(imageLayout, stretch=1)
        mainLayout.addLayout(hl1)
        mainLayout.addLayout(hl2)
        self.setLayout(mainLayout)
        self.update_image()
        QTimer.singleShot(0, self.update_image)

        self.emptyTriangle()

    #INTERFAZ
    def changedThreshold(self, value):
        self.thresholdIMU = float(value)
        self.signalTracker.thresholdIMU = self.thresholdIMU
        print(f"threshold: {self.thresholdIMU}")

    def changeTopThreshold(self, value):
        self.topThreshEOG = float(value)
        if self.thresholdMode == STATIC_MODE:
            self.signalTracker.topThresholdEOG = float(value)
        else:
            self.signalTracker.topModEOG = float(value)
        print(f"TOP THRESHOLD: {self.topThreshEOG}")


    def changeBottomThreshold(self, value):
        self.bottomThreshEOG = float(value)
        if self.thresholdMode == STATIC_MODE:
            self.signalTracker.bottomThresholdEOG = float(value)
        else:
            self.signalTracker.bottomModEOG = float(value)
        print(f"BOTTOM THRESHOLD: {self.bottomThreshEOG}")

    def changeMode(self):
        self.thresholdMode = MOVIL_MODE if self.modeButton.isChecked() else STATIC_MODE
        newText = "MOVIL MODE" if self.modeButton.isChecked() else "STATIC MODE"
        self.modeButton.setText(newText)
        self.signalTracker.thresholdMode = self.thresholdMode
        print(f"THRESHOLD MODE: {self.thresholdMode}")

    def changeDataMode(self):
        self.dataMode = EOG_MODE if self.dataButton.isChecked() else IMU_MODE
        newText = "EOG" if self.dataButton.isChecked() else "IMU"
        self.dataButton.setText(newText)
        self.signalTracker.dataMode = self.dataMode
        print(f"DATA MODE CHANGED: {self.dataMode}")


    def update_image(self):
        if not self.pixmap.isNull():
            scaled = self.pixmap.scaled(
                self.pic.width(),
                self.pic.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.pic.setPixmap(scaled)

    def resizeEvent(self, event):
        self.update_image()
        super().resizeEvent(event)

    #Valores de la UI
    def changedRondas(self, value):
        self.noRondas = int(value)
        self.signalTracker.noRondas = self.noRondas
        print(f"RONDAS: {self.noRondas}")
    def changeMinTime(self, value):
        self.minTime = int(value)
        self.signalTracker.minTime = self.minTime
        print(f"MIN TIME: {self.minTime}")
    def changeMaxTime(self, value):
        self.maxTime = int(value)
        self.signalTracker.maxTime = self.maxTime
        print(f"MAX TIME: {self.maxTime}")
    def changedWaitTime(self, value):
        self.waitTime = int(value)
        self.signalTracker.waitTime = self.waitTime
        print(f"WAIT TIME:  {self.waitTime}")

    def changedSujeto(self, value):
        self.sujeto = int(value)
        self.signalTracker.sujeto = self.sujeto
        
        directorio = self.baseDir + str(self.sujeto)
        self.signalTracker.baseDir = directorio
        print(directorio)
        print(f"SUJETO: {self.sujeto}")

    def updateAll(self):
        self.thresholdIMU = float(self.thresholdLabel.value())
        self.signalTracker.threshold = self.thresholdIMU
        print(f"threshold: {self.thresholdIMU}")
        self.noRondas = int(self.noRondasBox.value())
        self.signalTracker.noRondas = self.noRondas
        print(f"RONDAS: {self.noRondas}")
        self.minTime = int(self.minTimeLabel.value())
        self.signalTracker.minTime = int(self.minTime)
        print(f"MIN TIME: {self.minTime}")
        self.maxTime = int(self.maxTimeLabel.value())
        self.signalTracker.maxTime = int(self.maxTime)
        print(f"MAX TIME: {self.maxTime}")
        self.waitTime = int(self.waitTimeLabel.value())
        self.signalTracker.waitTime = self.waitTime
        print(f"WAIT TIME:  {self.waitTime}")
        self.sujeto = int(self.subjectLabel.value())
        self.signalTracker.sujeto = int(self.sujeto)
        directorio = self.baseDir + str(self.sujeto)
        self.signalTracker.baseDir = directorio
        print(directorio)
        print(f"SUJETO: {self.sujeto}")
        self.thresholdMode = MOVIL_MODE if self.modeButton.isChecked() else STATIC_MODE
        self.signalTracker.thresholdMode = self.thresholdMode
        print(f"THRESHOLD MODE: {self.thresholdMode}")

        self.dataMode = EOG_MODE if self.dataButton.isChecked() else IMU_MODE
        self.signalTracker.dataMode = self.dataMode
        print(f"DATA MODE CHANGED: {self.dataMode}")


        if self.thresholdMode == STATIC_MODE:
            self.signalTracker.topThresholdEOG = int(self.topThreshEOGLabel.value())
            self.signalTracker.bottomThresholdEOG = int(self.bottomThreshEOGLabel.value())
        else: #Movil
            self.signalTracker.topModEOG = int(self.topThreshEOGLabel.value())
            self.signalTracker.bottomModEOG = int(self.bottomThreshEOGLabel.value())

        print(f"TOP THRESHOLD: {self.topThreshEOG}")

    def startClassification(self):
        print("START IT")
        self.updateAll()

        self.classificationThread = QThread()
        self.signalTracker.moveToThread(self.classificationThread)
        self.classificationThread.started.connect(self.signalTracker.trackData)
        self.signalTracker.isTracking = True
        self.signalTracker.emptyFigure.connect(self.emptyTriangle)
        self.signalTracker.fillFigure.connect(self.fillTriangle)
        self.signalTracker.stopSignal.connect(self.stop)
        self.signalTracker.reportSignal.connect(self.showReportWindow)
        self.classificationThread.start()

        
        
    def stop(self):
        self.signalTracker.stopThread()
        self.classificationThread.quit()
        self.classificationThread.wait()
        self.signalTracker = SignalTracker(self.puerto)


    def changeTriangleColor(self, isRed):
        if isRed:
            self.pixmap.load(fillFile)
        else:
            self.pixmap.load(emptyFile)
        self.update_image()

    def emptyTriangle(self):
        self.pixmap.load(emptyFile)
        self.update_image()

    def fillTriangle(self):
        self.pixmap.load(fillFile)
        self.update_image()

    def calibrate(self):
        self.tracker.calibrateSensor()

    def showReportWindow(self, preliminarLog):
        repWindow = ReportWindow(preliminarLog)
        print("Ventana creada")
        repWindow.exec()
        if repWindow.isLastLogSaved:
            self.signalTracker.isCurrentLogSaved = True
            print("SALVADO")
        else:
            self.signalTracker.isCurrentLogSaved = False
            print("DE NUEVO")
        self.signalTracker.reviewEnded = True
        






"""app = QApplication(sys.argv)
mainWindow = ventanaPrincipal("COM7")
mainWindow.show()
sys.exit(app.exec())"""