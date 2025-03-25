class Rama:
    def __init__(self, nombre):
        self.nombre = nombre  # Almacena el nombre de la rama.
        self.ultimo_commit = None  # Apunta al último commit realizado en la rama (aún no implementado).
        self.rama_siguiente = None  # Enlace a la siguiente rama en la lista (estructura de lista enlazada).

class GestionRamas:
    def __init__(self):
        # La clase 'GestionRamas' administra las ramas de un repositorio.
        self.rama_cabeza = Rama('main')  # Inicializa la rama principal 'main' como la rama cabeza.
        self.rama_actual = self.rama_cabeza  # Define la rama actual como 'main' por defecto.

    def agregar_rama(self, nombre: str):
        # Método para crear una nueva rama con el nombre especificado.
        nueva_rama = Rama(nombre)  # Se crea una instancia de la clase 'Rama' con el nombre proporcionado.
        temp = self.rama_cabeza  # Comienza desde la rama cabeza.
        while temp.rama_siguiente != None:  # Recorre la lista de ramas.
            if temp.nombre.lower() == nombre.lower():  # Comprueba si ya existe una rama con el mismo nombre.
                print(f"> --- Error. Rama '{nombre}' existente.")  # Mensaje de error si la rama ya existe.
                return
            temp = temp.rama_siguiente  # Avanza a la siguiente rama.
        temp.rama_siguiente = nueva_rama  # Enlaza la nueva rama al final de la lista.
        print(f"> Rama creada: '{nombre}'.")  # Mensaje de confirmación.

    def seleccionar_rama(self, nombre: str):
        # Método para seleccionar una rama existente como la rama actual.
        temp = self.rama_cabeza  # Comienza desde la rama cabeza.
        while temp != None:  # Recorre la lista de ramas.
            if temp.nombre.lower() == nombre.lower():  # Busca una rama con un nombre coincidente (ignora mayúsculas/minúsculas).
                self.rama_actual = temp  # Actualiza la rama actual.
                print(f"> Rama actual: '{self.rama_actual.nombre}'.")  # Mensaje de confirmación.
                return
            temp = temp.rama_siguiente  # Avanza a la siguiente rama.
        print(f"> --- Error. No se ha encontrado la rama '{nombre}'.")  # Mensaje de error si la rama no existe.
