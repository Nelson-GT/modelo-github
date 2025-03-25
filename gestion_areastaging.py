import os  # Importa funciones relacionadas con el sistema operativo.
from hashlib import sha1  # Importa sha1 para generar hashes seguros.
from uuid import uuid4  # Importa uuid4 para generar identificadores únicos.
from gestion_directoriotrabajo import Archivo  # Importa la clase Archivo que representa un archivo en el directorio.

# Clase que representa un archivo en el área de staging.
class ArchivoStaged:
    def __init__(self, archivo: Archivo, estado):
        self.archivo = archivo  # Instancia de la clase Archivo que contiene el nombre y el contenido.
        self.estado = estado  # Estado del archivo ("A" para agregado, "M" para modificado, "D" para eliminado, etc.).
        self.ruta = os.path.join(os.getcwd(), archivo.archivo)  # Ruta completa del archivo en el sistema.
        self.checksum = self.generar_checksum()  # Genera un checksum único para identificar el archivo.
        self.archivostaged_siguiente = None  # Referencia al siguiente archivo staged en la lista enlazada.

    def generar_checksum(self):
        # Genera un hash SHA1 único basado en el contenido del archivo, su ruta y un UUID.
        contenido = f"{self.archivo.archivo}{self.archivo.contenido}{self.ruta}{uuid4()}".encode('utf-8')
        return sha1(contenido).hexdigest()  # Devuelve el hash generado.

# Clase que gestiona el área de staging, donde se preparan los archivos antes de un commit.
class GestionAreaStaging:
    def __init__(self):
        self.archivostaged_cabeza = None  # Cabeza de la lista enlazada de archivos staged.
        self.ultimo_commit = None  # Último commit realizado, utilizado para validar cambios.

    def agregar_archivostaged(self, archivo: Archivo):
        # Agrega un archivo al área de staging, actualizando si ya existe.
        actual = self.archivostaged_cabeza
        while actual:  # Recorre la lista enlazada para buscar duplicados.
            if actual.archivo.archivo == archivo.archivo:  # Si el archivo ya existe en staging:
                actual.archivo.contenido = archivo.contenido  # Actualiza su contenido.
                actual.checksum = actual.generar_checksum()  # Recalcula su checksum.
                return
            actual = actual.archivostaged_siguiente
        estado = self.validar_estado(archivo)  # Determina el estado del archivo ("A", "M", etc.).
        archivostaged_nuevo = ArchivoStaged(archivo, estado)  # Crea un nuevo nodo para el archivo staged.
        if not self.archivostaged_cabeza:  # Si el área de staging está vacía:
            self.archivostaged_cabeza = archivostaged_nuevo
        else:
            # Inserta el nuevo archivo staged al inicio de la lista enlazada.
            archivostaged_nuevo.archivostaged_siguiente = self.archivostaged_cabeza
            self.archivostaged_cabeza = archivostaged_nuevo

    def validar_estado(self, archivo_nuevo):
        # Determina el estado del archivo (ejemplo: modificado "M", no modificado "(No modificado)", agregado "A").
        if self.ultimo_commit:  # Si existe un último commit:
            archivos_commit = self.ultimo_commit.archivos_modificados  # Archivos del último commit.
            for archivo in archivos_commit:
                if archivo_nuevo.archivo == archivo.archivo.archivo:  # Compara nombres de archivo.
                    if archivo_nuevo.contenido == archivo.archivo.contenido:  # Compara contenidos.
                        return "(No modificado)"  # No hay cambios en el archivo.
                    else:
                        return "M"  # El archivo ha sido modificado.
            return "A"  # Archivo no está en el último commit, es nuevo.
        else:
            return "A"  # Si no hay commits previos, el archivo es agregado.

    def validar_eliminados(self):
        # Detecta archivos eliminados comparando con los archivos del último commit.
        if self.ultimo_commit:
            archivos_commit = self.ultimo_commit.archivos_modificados
            for archivo in archivos_commit:
                i = 0
                temp = self.archivostaged_cabeza
                while temp:  # Recorre los archivos staged.
                    if archivo.archivo.archivo == temp.archivo.archivo:  # Si el archivo todavía existe:
                        i = 1
                        break
                    temp = temp.archivostaged_siguiente
                if i == 0:  # Si el archivo no está en el área de staging, se marca como eliminado.
                    archivostaged_nuevo = ArchivoStaged(archivo.archivo, "D")  # "D" para eliminado.
                    if not self.archivostaged_cabeza:
                        self.archivostaged_cabeza = archivostaged_nuevo
                    else:
                        # Inserta el archivo eliminado al inicio de la lista enlazada.
                        archivostaged_nuevo.archivostaged_siguiente = self.archivostaged_cabeza
                        self.archivostaged_cabeza = archivostaged_nuevo

    def contar_archivos_staged(self):
        # Cuenta el número de archivos en el área de staging que no están marcados como eliminados.
        contador = 0
        temp = self.archivostaged_cabeza
        while temp:  # Recorre la lista enlazada.
            if temp.estado != "D":  # Ignora los archivos eliminados.
                contador += 1
            temp = temp.archivostaged_siguiente
        return contador  # Devuelve la cantidad de archivos en staging.
