from datetime import datetime  # Importa datetime para trabajar con fechas y horas.
from hashlib import sha1  # Importa sha1 para generar hashes seguros.
from uuid import uuid4  # Importa uuid4 para generar identificadores únicos.
from gestion_areastaging import ArchivoStaged  # Importa la clase ArchivoStaged, que representa archivos en el área de staging.

# Clase que representa un commit en el sistema.
class Commit:
    def __init__(self, usuario, mensaje, archivos: list[ArchivoStaged], rama, hash=None):
        self.autor = usuario  # Autor del commit.
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha y hora de creación del commit.
        self.mensaje = mensaje  # Mensaje descriptivo del commit.
        self.commit_anterior = None  # Referencia al commit anterior en la cadena de commits.
        self.archivos_modificados = archivos  # Lista de archivos modificados en el commit.
        self.nombre_rama = rama  # Nombre de la rama en la que se hizo el commit.
        if hash is None:
            self.hash = self.generar_hash()  # Genera un hash único para identificar el commit.
        else:
            self.hash = hash  # Utiliza el hash proporcionado.

    def generar_hash(self):
        # Genera un hash SHA1 único para el commit basado en su contenido.
        contenido = f"{self.fecha}{self.autor}{self.mensaje}{uuid4()}".encode('utf-8')
        return sha1(contenido).hexdigest()  # Devuelve el hash generado.

# Clase para gestionar una colección de commits.
class GestionCommits:
    def __init__(self):
        self.commit_actual = None  # Referencia al commit más reciente.
        self.commit_seleccionado = None  # Referencia al commit actualmente seleccionado (si aplica).
    
    def agregar_commit(self, usuario, mensaje, archivostaged_cabeza, rama):
        # Método para crear y agregar un nuevo commit basado en archivos staged.
        archivos = []  # Lista para almacenar los archivos que se incluirán en el commit.
        temp = archivostaged_cabeza  # Apunta al primer archivo staged.
        while temp:
            # Filtra archivos que no están eliminados ("D") ni sin cambios ("(No modificado)").
            if temp.estado != "D" and temp.estado != "(No modificado)":
                archivos.append(temp)  # Agrega el archivo a la lista de archivos modificados.
            temp = temp.archivostaged_siguiente  # Avanza al siguiente archivo staged.

        if self.commit_actual == None:  # Si no hay commits previos:
            commit_nuevo = Commit(usuario, mensaje, archivos, rama)  # Crea un nuevo commit.
            self.commit_actual = commit_nuevo  # Lo establece como el commit actual.
        else:
            # Actualiza la lista de archivos basándose en cambios previos.
            archivos = self.actualizar_archivos(archivos, archivostaged_cabeza)
            commit_nuevo = Commit(usuario, mensaje, archivos, rama)  # Crea un nuevo commit.
            commit_nuevo.commit_anterior = self.commit_actual  # Apunta al commit anterior.
            self.commit_actual = commit_nuevo  # Lo establece como el commit actual.
        
        self.commit_seleccionado = self.commit_actual  # Selecciona el commit recién creado.

    def actualizar_archivos(self, archivos: list[ArchivoStaged], archivostaged_cabeza):
        # Actualiza la lista de archivos modificados del commit según el estado de los archivos staged.
        archivos_previos = self.commit_actual.archivos_modificados  # Archivos del commit actual.
        for archivo in archivos_previos:
            temp = archivostaged_cabeza  # Apunta al primer archivo staged.
            while temp:
                # Si un archivo staged coincide con uno previo y su estado no ha cambiado:
                if temp.archivo.archivo == archivo.archivo.archivo:
                    if temp.estado == "(No modificado)":
                        archivos.append(archivo)  # Añade el archivo del commit previo a la lista actualizada.
                temp = temp.archivostaged_siguiente  # Avanza al siguiente archivo staged.
        return archivos  # Devuelve la lista actualizada de archivos.
