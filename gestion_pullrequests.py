from datetime import datetime  # Importa datetime para trabajar con fechas y horas.
import hashlib  # Importa hashlib para generar hashes únicos.

# Clase que representa un Pull Request.
class PullRequest:
    def __init__(self, titulo, descripcion, autor, rama_origen, rama_destino, lista_commits):
        # Genera un identificador único (ID) para el Pull Request usando un hash SHA1 basado en sus datos clave.
        sha1 = hashlib.sha1()
        sha1.update((titulo+autor+rama_origen+rama_destino).encode('utf-8'))
        self.id = sha1.hexdigest()  # Almacena el hash generado como ID único.
        self.titulo = titulo  # Título del Pull Request.
        self.descripcion = descripcion  # Descripción del Pull Request.
        self.autor = autor  # Nombre del autor que crea el Pull Request.
        self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha y hora de creación del PR.
        self.rama_origen = rama_origen  # Rama desde la que se origina el Pull Request.
        self.rama_destino = rama_destino  # Rama de destino del Pull Request.
        self.lista_commits = lista_commits  # Lista de commits asociados al Pull Request.
        self.fecha_cierre = None  # Fecha de cierre del Pull Request (inicia como `None`).
        self.estado = "Pendiente"  # Estado inicial del Pull Request.
        self.pr_anterior = None  # Referencia al Pull Request anterior en una lista enlazada.

# Clase para gestionar múltiples Pull Requests.
class GestionPullRequests:
    def __init__(self):
        self.pullrequest_cabeza = None  # Referencia al primer Pull Request en la cola.
        self.temp_areaStaged = None  # Área temporal para staging (sin uso definido en este fragmento).
        self.commit_pr = []  # Lista temporal de commits para nuevos Pull Requests.
    
    def crear_pullRequest(self, rama_origen, rama_destino, autor): 
        # Solicita al usuario un título y una descripción para el nuevo Pull Request.
        titulo = input("\tEscriba el título del Pull Request: ")
        titulo.replace(" ", "-")  # Reemplaza espacios con guiones en el título.
        descripcion = input("\tEscriba la descripción del Pull Request: ")
        lista_commits = self.commit_pr  # Obtiene la lista de commits temporales.
        pr = PullRequest(titulo, descripcion, autor, rama_origen, rama_destino, lista_commits)  # Crea un nuevo PR.
        self.commit_pr = []  # Limpia la lista de commits temporales.
        if self.pullrequest_cabeza is None:  # Si no hay PRs en la cola:
            self.pullrequest_cabeza = pr  # Este PR se convierte en el primero.
        else:
            temp = self.pullrequest_cabeza
            while temp.pr_anterior is not None:  # Recorre la lista enlazada hasta el último PR.
                temp = temp.pr_anterior
            temp.pr_anterior = pr  # Añade el nuevo PR al final de la lista.
    
    def status_list(self):
        # Muestra la lista de Pull Requests en la cola.
        if self.pullrequest_cabeza:
            print("\n----- Cola de Pull Requests -----")
            temp = self.pullrequest_cabeza
            while temp:
                print(f"{temp.id}   {temp.titulo}   {temp.estado}")  # Muestra ID, título y estado de cada PR.
                temp = temp.pr_anterior  # Pasa al siguiente PR en la lista.
        else:
            print("> --- Error. No se han encontrado Pull Requests en la cola.")
    
    def review(self, id_pr):
        # Cambia el estado de un Pull Request a "En revisión" según su ID.
        if self.pullrequest_cabeza:
            temp = self.pullrequest_cabeza
            while temp:
                if temp.id == id_pr:  # Encuentra el PR con el ID coincidente.
                    temp.estado = "En revisión"  # Actualiza su estado.
                    print(f"{temp.id}   {temp.titulo}   {temp.estado}")
                    return
                temp = temp.pr_anterior
            print(f"> No se ha encontrado ningún Pull Request con el ID: {id_pr}")
        else:
            print("> --- Error. No se han encontrado Pull Requests en la cola.")
    
    def approve(self, id_pr):
        # Aprueba un Pull Request y lo elimina de la cola.
        if self.pullrequest_cabeza:
            temp = self.pullrequest_cabeza
            aux = None
            while temp:
                if temp.id == id_pr:  # Encuentra el PR con el ID coincidente.
                    temp.estado = "Aprobado"  # Cambia el estado del PR a aprobado.
                    temp.fecha_cierre = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Registra la fecha de cierre.
                    if temp.pr_anterior is not None:  # Elimina el PR de la cola.
                        if aux is None:
                            self.pullrequest_cabeza = temp.pr_anterior
                            return temp
                    if aux is None:
                        self.pullrequest_cabeza = temp.pr_anterior
                        return temp
                    aux.pr_anterior = temp.pr_anterior
                    return temp
                aux = temp
                temp = temp.pr_anterior
            print(f"> No se ha encontrado ningún Pull Request con el ID: {id_pr}")
        else:
            print("> --- Error. No se han encontrado Pull Requests en la cola.")

    def reject(self, id_pr):
        # Rechaza un Pull Request y lo elimina de la cola.
        if self.pullrequest_cabeza:
            temp = self.pullrequest_cabeza
            aux = None
            while temp:
                if temp.id == id_pr:
                    temp.estado = "Rechazado"  # Cambia el estado del PR a rechazado.
                    temp.fecha_cierre = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if temp.pr_anterior is not None:
                        if aux is None:
                            self.pullrequest_cabeza = temp.pr_anterior
                            return
                    aux.pr_anterior = temp.pr_anterior
                    return
                aux = temp
                temp = temp.pr_anterior
            print(f"> No se ha encontrado ningún Pull Request con el ID: {id_pr}")
        else:
            print("> --- Error. No se han encontrado Pull Requests en la cola.")
    
    def cancel(self, id_pr):
        # Cancela un Pull Request por su ID y lo elimina de la cola.
        temp = self.pullrequest_cabeza
        aux = None
        while temp is not None:
            if id_pr == temp.id:
                temp.fecha_cierre = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if temp.pr_anterior is not None:
                    if aux is None:
                        self.pullrequest_cabeza = temp.pr_anterior
                        return
                aux.pr_anterior = temp.pr_anterior
                return
            aux = temp
            temp = temp.pr_anterior
        print("No existe un Pull Request con el ID introducido.")
    
    def next_(self):
        # Cambia el estado del siguiente PR pendiente a "En revisión".
        if self.pullrequest_cabeza:
            temp = self.pullrequest_cabeza
            while temp:
                if temp.estado == "Pendiente":
                    temp.estado = "En revisión"
                    return
                temp = temp.pr_anterior
            print("> No se ha encontrado ningún Pull Request con el estado Pendiente.")
        else:
            print("> --- Error. No se han encontrado Pull Requests en la cola.")
    
    def tag(self, id_pr, etiqueta):
        # Agrega una etiqueta a la descripción de un PR específico.
        if self.pullrequest_cabeza:
            temp = self.pullrequest_cabeza
            while temp:
                if temp.id == id_pr:
                    temp.descripcion += (" Etiqueta: " + etiqueta)
                    return
                temp = temp.pr_anterior
            print("> No se ha encontrado ningún Pull Request con el ID proporcionado.")
        else:
            print("> --- Error. No se han encontrado Pull Requests en la cola.")
