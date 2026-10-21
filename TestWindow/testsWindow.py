from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSizePolicy
)

from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QTimer
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
    def __init__(self, puerto, vectorSize):
        super().__init__()
        #self.tracker = imuTracker()
        self.puerto = puerto
        self.vectorSize = vectorSize
        self.signalTracker = SignalTracker(self.puerto)
        self.baseDir = "./DataSets/Sept2026/sujetos/sujeto"
        self.setStyleSheet(f"""QWidget {{background-color: {"#FFFFFF"};}}""")
        self.pic = QLabel()
        self.pixmap = QtGui.QPixmap()
        self.pixmap.load(emptyFile)
        self.setWindowTitle("Proyecto")
        self.showMaximized()
        mainLayout = QVBoxLayout()
        #Imagen
        self.pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pic.setSizePolicy(QSizePolicy.Policy.Expanding    , QSizePolicy.Policy.Expanding)
        imageLayout = QHBoxLayout()
        imageLayout.addWidget(self.pic)
        mainLayout.addLayout(imageLayout, stretch=1)

        self.setLayout(mainLayout)
        self.update_image()
        QTimer.singleShot(0, self.update_image)

        self.emptyTriangle()
        self.reportWindow = ReportWindow([], self.puerto, self.vectorSize)
        self.reportWindow.show()
        self.reportWindow.emptyFigure.connect(self.emptyTriangle)
        self.reportWindow.fillFigure.connect(self.fillTriangle)

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

"""app = QApplication(sys.argv)
mainWindow = ventanaPrincipal("COM7")
mainWindow.show()
sys.exit(app.exec())"""