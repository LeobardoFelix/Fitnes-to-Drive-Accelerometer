import csv
import time
import os
from datetime import datetime


class DataLogger:
    """
    Representa un capturador de datos, capaz de registrar datos 
    en archivos CSV creados de forma automática.

    Attributes:
        modo (str): Representa el tipo de límite que se usa para referencia, puede ser continuo o umbral.
        limit (float): El valor en el que el logger registra una reacción.
        activo (bool): Es True si un archivo se encuentra abierto.
        _archivo (str): Directorio y nombre del archivo donde se guardaran los datos.
        _file_obj (str): Archivo CSV actual
        _writer (Writer): Escritor de archivos CSV
        _t0 (long): Timestamp actual

    Methods:
        iniciar(str): Crea y devuelve un nuevo archivo CSV.
        detener(): Cierra el archivo CSV actualmente abierto.
        registrar(float, float): Añade una nueva entrada al archivo actualmente abierto.
        set_modo(str): Cambia el modo del límite.
        set_limit(float): Establece un nuevo valor para el limite actual.

    """
    def __init__(self, modo: str = "continuo", limit: float = 300):
        
        
        self.modo = modo
        self.limit = limit
        self.activo = False

        self._archivo = None
        self._writer = None
        self._file_obj = None
        self._t0 = None

    
    def iniciar(self, directorio: str = ".") -> str:
        """
        Crea un nuevo archivo CSV en el directorio actual, 
        con los campos: tiempo_ms, valor y promedio.

        Args:
            directorio (str): Directorio donde se creará el archivo. 

        Returns:
            _archivo (str): Directorio con el nombre del archivo creado.       
        """
        if self.activo:
            raise RuntimeError("El muestreo ya está en curso.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        currentDir = os.path.join(directorio, "Graphs")
        nombre = f"muestreo_{timestamp}.csv"
        self._archivo = os.path.join(currentDir, nombre)
        os.makedirs(currentDir, exist_ok=True)

        self._file_obj = open(self._archivo, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file_obj)
        self._writer.writerow(["tiempo_ms", "valor", "promedio"])
        self._file_obj.flush()

        self._t0 = time.perf_counter()
        self.activo = True
        return self._archivo

    def detener(self):
        """
        Cierra el archivo CSV actualmente abierto.
        """
        if not self.activo:
            return
        self.activo = False
        if self._file_obj:
            self._file_obj.flush()
            self._file_obj.close()
            self._file_obj = None
            self._writer = None

    def registrar(self, valor: float, promedio):
        """
        Añade una entrada al archivo abierto actualmente, si no existe un
        archivo abierto o el valor es menor al límite en modo umbral no 
        registra ningún valor.
        
        Args:
            valor (float): valor a registrar.
            promedio (float): promedio a registrar.

        """
        if not self.activo or self._writer is None:
            return

        if self.modo == "umbral" and valor <= self.limit:
            return

        elapsed_ms = round((time.perf_counter() - self._t0) * 1000, 3)
        self._writer.writerow([elapsed_ms, valor, promedio])
        self._file_obj.flush()

    def set_modo(self, modo: str):
        """
        Cambia el modo del límite entre umbral y continuo.

        Args:
            modo (str): Nuevo modo del sistema.

        Raises:
            ValueError: Si el límite no tiene el valor "umbral" o "continuo"
        """

        if modo not in ("continuo", "umbral"):
            raise ValueError(f"Modo desconocido: {modo!r}. Use 'continuo' o 'umbral'.")
        self.modo = modo

    def set_limit(self, limit: float):
        """
        Establece un nuevo valor para el límite actual.

        Args:
            limit (float): Nuevo límite.
        """
        self.limit = float(limit)

    @property
    def archivo_actual(self) -> str | None:
        
        return self._archivo if self.activo else None