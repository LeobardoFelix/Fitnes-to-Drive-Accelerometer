#from TestWindow.SerialCommunication.SerialReader import SerialReader
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from TestWindow.SerialCommunication.SerialReader import SerialReader
SC = SerialReader('COM7', 9600, 20, 0, 0, 1, 1, 500, 200)#SerialCatcher.serialCatcher('COM10')
SC.openConection()
referencia = 300

try:
    while True:
        linea = SC.catchSerial()
        if linea is not None:   # Solo imprimir si llegó algo
            print(linea)

        
except KeyboardInterrupt:
    print("Programa detenido")
finally:
    SC.closeConection()         # Siempre cerrar el puerto al salir