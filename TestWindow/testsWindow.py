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
    """
    Interfaz de monitoreo y captura de reacciones, compuesta
    por una pantalla de presentación de estímulos visuales y
    una de configuración de variables.


    Attributes:
        reportWindow (ReportWindow): Ventana de configuración anidada a la ventana de estímulos.
        reconectar (bool): Variable de reconección con la ventana de configuración. Si es True al cerrar la ventana volverá a configuración.
        pixmap (QPixmap): Imagen que cambia para generar el estímulo visual.


    Methods:
        update_image(): Actualiza y reescala la imagen dentro de pixmap.
        emptyTriangle(): Carga la imagen perteneciente al estímulo inactivo en el pixmap.
        fillTriangle(): Carga la imagen perteneciente al estímulo activo en el pixmap.
        reconnect(): Activa la bandera reconectar y cierra la interfaz.
   
    """
    def __init__(self, puerto, vectorSize, currentDir):
        super().__init__()
        #self.tracker = imuTracker()
        self.puerto = puerto
        self.reconectar = False
        self.vectorSize = vectorSize
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
        self.reportWindow = ReportWindow([], self.puerto, self.vectorSize, currentDir)
        self.reportWindow.show()
        self.reportWindow.emptyFigure.connect(self.emptyTriangle)
        self.reportWindow.fillFigure.connect(self.fillTriangle)
        self.reportWindow.reconnectSignal.connect(self.reconnect)

    def update_image(self):
        """
        Actualiza y reescala la imagen cargada en pixmap
        si esta no es nula o vacía.
        """
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

    def emptyTriangle(self):
        """
        Carga la imagen perteneciente al estímulo inactivo en el pixmap.
        """
        self.pixmap.load(emptyFile)
        self.update_image()

    def fillTriangle(self):
        """
        Carga la imagen perteneciente al estímulo activo en el pixmap.
        """
        self.pixmap.load(fillFile)
        self.update_image()
    def reconnect(self):
        """
        Activa la bandera reconectar y cierra la interfaz.
        """
        self.reconectar = True
        self.reportWindow.close()
        self.close()
