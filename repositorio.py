import os
from os import getcwd
# Se importa el módulo 'os' y la función 'getcwd' para trabajar con operaciones relacionadas con el sistema operativo
# como obtener el directorio actual de trabajo.

# Se importan clases específicas de diferentes módulos que probablemente gestionan diversas funcionalidades
# relacionadas con un repositorio, como directorios de trabajo, commits, área de staging, pull requests y ramas.
from gestion_directoriotrabajo import GestionDirectorioTrabajo
from gestion_commits import GestionCommits
from gestion_areastaging import GestionAreaStaging
from gestion_pullrequests import GestionPullRequests
from gestion_ramas import GestionRamas

class Repositorio:
    def __init__(self, usuario):
        # La función '__init__' inicializa la clase 'Repositorio' con un nombre basado en el directorio actual 
        # y un autor proporcionado como parámetro.
        self.nombre = os.path.basename(getcwd())  # Obtiene el nombre del directorio actual como el nombre del repositorio.
        self.autor = usuario  # El autor del repositorio es definido por el parámetro 'usuario'.
        
        # Se instancian las clases importadas para asignar funcionalidades específicas al repositorio.
        self.gestion_ramas = GestionRamas()  # Gestiona las ramas del repositorio.
        self.gestion_directoriotrabajo = GestionDirectorioTrabajo()  # Gestiona el directorio de trabajo.
        self.gestion_areastaging = GestionAreaStaging()  # Gestiona el área de staging (preparación de cambios).
        self.gestion_commits = GestionCommits()  # Gestiona los commits realizados en el repositorio.
        self.gestion_pullrequest = GestionPullRequests()  # Gestiona las pull requests del repositorio.
        
        self.repositorio_siguiente = None  # Atributo que posiblemente representa un enlace a otro repositorio.
