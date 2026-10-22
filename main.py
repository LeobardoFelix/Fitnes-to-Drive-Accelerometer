import sys
import matplotlib
matplotlib.use("QtAgg")
from Graficadora.graphWindow import GraphWindow

from ConfigurationWindow.configWindow import configurationWindow, GRAPH_WINDOW_MODE
from PyQt6.QtWidgets import (
    QApplication
)
from TestWindow.testsWindow import TestsWindow

def printData(puerto, topThreshold, bottomThreshold, thresholdMode, filterLength, dataMode, windowMode, imuThreshold):
    MOVIL_MODE = 1
    STATIC_MODE = 0
    IMU_MODE = 0
    EOG_MODE = 1
    print(puerto)
    print(topThreshold)
    print(bottomThreshold)
    if thresholdMode == STATIC_MODE:
        print("THRESHOLD STATICO")
    else:
        print("THRESHOLD MOVIL")

    print(filterLength)
    print(dataMode)
    if dataMode == EOG_MODE:
        print("EOG MODE")
    else:
        print("IMU MODE")
    print(windowMode)
    if windowMode == GRAPH_WINDOW_MODE:
        print("GRAPH_WINDOW_MODE")
    else:
        print("PRUEBAS_WINDOW_MODE")
    print(imuThreshold)

app = QApplication(sys.argv)
app.setStyle("Fusion")

reconectar = True
while True:

    while reconectar:
        reconectar = False

        config = configurationWindow()
        puerto, topThreshold, bottomThreshold, thresholdMode, filterLength, dataMode, \
            windowMode, thresholdImu, topFrame, bottomFrame, currentDir = config.iniciar()
        if not puerto:          # usuario cerró el diálogo sin conectar
            sys.exit(0)
        if windowMode == GRAPH_WINDOW_MODE:
            ventana = GraphWindow(puerto, topThreshold, bottomThreshold, thresholdMode, 
                    filterLength, dataMode, thresholdImu, topFrame, bottomFrame, currentDir)
            print("GRAPH")
        else:
            ventana = TestsWindow(puerto, filterLength, currentDir)
            print("PRUEBAS")
        ventana.show()
        #printData(puerto, topThreshold, bottomThreshold, thresholdMode, filterLength, dataMode, windowMode, imuThreshold)
        app.exec()

        reconectar = ventana.reconectar 
        if not reconectar:      # cerraron la ventana normalmente → salir
            sys.exit(0)

    """ventana = GraphWindow(puerto, maxC, minC, umbral, filterLength, 1, 2, 500, 200)

    def _pedir_reconexion():
        global reconectar
        reconectar = True

    ventana.reconectar_solicitado.connect(_pedir_reconexion)
    ventana.show()"""
    
    # Si reconectar=True, el while vuelve a mostrar VentanaConexion