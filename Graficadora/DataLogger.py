import csv
import time
import os
from datetime import datetime


class DataLogger:
    def __init__(self, modo: str = "continuo", limit: float = 300):
     
        #Modo:  'continuo' o 'umbral'
        
        self.modo = modo
        self.limit = limit
        self.activo = False

        self._archivo = None
        self._writer = None
        self._file_obj = None
        self._t0 = None

    
    def iniciar(self, directorio: str = ".") -> str:

        if self.activo:
            raise RuntimeError("El muestreo ya está en curso.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"muestreo_{timestamp}.csv"
        self._archivo = os.path.join(directorio, nombre)

        self._file_obj = open(self._archivo, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file_obj)
        self._writer.writerow(["tiempo_ms", "valor"])
        self._file_obj.flush()

        self._t0 = time.perf_counter()
        self.activo = True
        return self._archivo

    def detener(self):

        if not self.activo:
            return
        self.activo = False
        if self._file_obj:
            self._file_obj.flush()
            self._file_obj.close()
            self._file_obj = None
            self._writer = None

    def registrar(self, valor: float):

        if not self.activo or self._writer is None:
            return

        if self.modo == "umbral" and valor <= self.limit:
            return

        elapsed_ms = round((time.perf_counter() - self._t0) * 1000, 3)
        self._writer.writerow([elapsed_ms, valor])
        self._file_obj.flush()

    def set_modo(self, modo: str):

        if modo not in ("continuo", "umbral"):
            raise ValueError(f"Modo desconocido: {modo!r}. Use 'continuo' o 'umbral'.")
        self.modo = modo

    def set_limit(self, limit: float):

        self.limit = float(limit)

    @property
    def archivo_actual(self) -> str | None:
        
        return self._archivo if self.activo else None