# Clase que representa un archivo dentro de un sistema de directorio.
class Archivo:
    def __init__(self, archivo, contenido):
        self.archivo = archivo  # Nombre del archivo.
        self.contenido = contenido  # Contenido del archivo.
        self.archivo_siguiente = None  # Referencia al siguiente archivo en una lista enlazada.

# Clase que gestiona un directorio de trabajo y las operaciones relacionadas con archivos.
class GestionDirectorioTrabajo:
    def __init__(self):
        self.archivo_cabeza = None  # Primer archivo en el directorio (cabeza de la lista enlazada).
        self.archivos_eliminados = []  # Lista para almacenar los nombres de archivos eliminados.

    def agregar_archivo(self):
        # Permite al usuario agregar un archivo con su contenido al directorio de trabajo.
        print("\n----- Carga de archivos -----")
        archivo = input("Ingrese el nombre del archivo: ")  # Solicita el nombre del archivo.
        contenido = input("Ingrese el contenido del archivo: ")  # Solicita el contenido del archivo.
        nuevo_archivo = Archivo(archivo, contenido)  # Crea una nueva instancia de la clase Archivo.
        self.detectar_duplicados(nuevo_archivo)  # Comprueba si existe un archivo duplicado.
        
        # Si no hay archivos en el directorio, el nuevo archivo se convierte en la cabeza.
        if not self.archivo_cabeza:
            self.archivo_cabeza = nuevo_archivo
        else:
            # Recorre la lista enlazada hasta encontrar el último archivo.
            actual = self.archivo_cabeza
            while actual.archivo_siguiente:
                actual = actual.archivo_siguiente
            actual.archivo_siguiente = nuevo_archivo  # Añade el nuevo archivo al final de la lista.
        print(f"\nArchivo '{archivo}' agregado/modificado exitosamente.")

    def detectar_duplicados(self, archivo):
        # Detecta si ya existe un archivo con el mismo nombre en el directorio.
        temp = self.archivo_cabeza
        while temp:
            if temp.archivo == archivo.archivo:  # Si los nombres coinciden:
                self.eliminar_archivo(archivo.archivo)  # Elimina el archivo duplicado.
            temp = temp.archivo_siguiente

    def eliminar_archivo(self, archivo):
        # Elimina un archivo por su nombre de la lista enlazada.
        if self.archivo_cabeza.archivo == archivo:  # Si el archivo a eliminar es la cabeza:
            self.archivo_cabeza = self.archivo_cabeza.archivo_siguiente
            return
        actual = self.archivo_cabeza
        # Busca el archivo en la lista enlazada.
        while actual.archivo_siguiente and actual.archivo_siguiente.archivo != archivo:
            actual = actual.archivo_siguiente
        if actual.archivo_siguiente:
            # Enlaza el nodo anterior con el siguiente, eliminando el archivo.
            actual.archivo_siguiente = actual.archivo_siguiente.archivo_siguiente

    def eliminar_archivo_directorio(self, archivo):
        # Elimina un archivo por nombre y lo registra en la lista de archivos eliminados.
        if self.archivo_cabeza.archivo == archivo:  # Si el archivo a eliminar es la cabeza:
            self.archivo_cabeza = self.archivo_cabeza.archivo_siguiente
            return
        actual = self.archivo_cabeza
        while actual:
            if actual.archivo_siguiente:  # Comprueba el siguiente archivo.
                if actual.archivo_siguiente.archivo == archivo:  # Si encuentra el archivo:
                    actual.archivo_siguiente = actual.archivo_siguiente.archivo_siguiente
                    self.archivos_eliminados.append(archivo)  # Registra el archivo como eliminado.
                actual = actual.archivo_siguiente
            else:
                actual = None  # Fin de la lista.
                print(f"\n--- Error. No se ha encontrado el archivo '{archivo}'.")

    def contar_archivos(self):
        # Cuenta el número de archivos en el directorio.
        contador = 0
        temp = self.archivo_cabeza
        while temp:  # Recorre la lista enlazada y cuenta cada archivo.
            contador += 1
            temp = temp.archivo_siguiente
        return contador  # Devuelve el número total de archivos.
