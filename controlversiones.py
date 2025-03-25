import json
from gestion_ramas import Rama, GestionRamas
from gestion_directoriotrabajo import Archivo
from gestion_areastaging import ArchivoStaged, GestionAreaStaging
from gestion_commits import Commit
from gestion_pullrequests import PullRequest, GestionPullRequests
from repositorio import Repositorio

class ControlVersiones:
    def __init__(self):
        self.usuario = input("Usuario: ")
        self.ultimo_repositorio = None
        self.repositorio_actual = None
        self.importar_repositorios()
        self.menu_opciones()

    def menu_opciones(self, band = True, i = 0):
        while band:
            print("\n----- Sistema de Control de Versiones -----")
            print(f"\nUsuario: {self.usuario}")
            if self.repositorio_actual:
                print(f"Repositorio activo: {self.repositorio_actual.nombre}")
            print("\n1. Abrir un repositorio existente.")
            print("2. Abrir interfaz de comandos.")
            print("3. Agregar/modificar archivos.")
            print("4. Eliminar archivos.")
            print("5. Gestión de Pull Requests.")
            print("6. Cambio de usuario.")
            print("7. Salir.")
            try:
                opcion = int(input("\nIngrese una opción: "))
            except ValueError:
                print("--- Error. Opción inválida.")
                continue
            match opcion:
                case 1:
                    if self.listar_repositorios():
                        repositorio = input("\nIngrese el nombre del repositorio al que desea acceder: ").strip()
                        self.abrir_repositorio(repositorio)
                        if self.repositorio_actual is None:
                            print(f"\n--- Error. No se ha encontrado el repositorio '{repositorio}'")
                            continue
                case 2:
                    self.menu_comandos()
                case 3:
                    if self.repositorio_actual:
                        self.repositorio_actual.gestion_directoriotrabajo.agregar_archivo()
                    else:
                        print("\n--- Error. Debe seleccionar un repositorio antes de agregar/modificar archivos.")
                        continue
                case 4:
                    print("\n----- Eliminación de archivos -----")
                    nombre_archivo = input("Nombre del archivo: ")
                    if self.repositorio_actual:
                        self.repositorio_actual.gestion_directoriotrabajo.eliminar_archivo_directorio(nombre_archivo)
                    else:
                        print("\n--- Error. Debe seleccionar un repositorio antes de eliminar archivos.")
                        continue
                case 5:
                    if self.repositorio_actual:
                        self.repositorio_actual.gestion_pullrequest.status_list()
                    else:
                        print("\n--- Error. Debe seleccionar un repositorio antes de gestionar Pull Requests.")
                case 6:
                    print("\n----- Cambio de usuario -----")
                    self.usuario = input("\nUsuario: ")
                case 7:
                    band = False

    def listar_repositorios(self):
        if self.ultimo_repositorio is None:
            print("\n--- Error. No se han encontrado repositorios.")
            return False
        print("\n----- Lista de repositorios -----\n")
        temp = self.ultimo_repositorio
        while temp is not None:
            print(f"--> {temp.nombre}")
            temp = temp.repositorio_siguiente
        return True

    def abrir_repositorio(self, nombre):
        if not nombre.strip():
            print("\n--- Error. El nombre del repositorio no puede estar vacío.")
            return
        temp = self.ultimo_repositorio
        while temp is not None:
            if temp.nombre == nombre:
                self.repositorio_actual = temp
                return
            temp = temp.repositorio_siguiente
        print(f"\n--- Error. No se encontró el repositorio con el nombre: '{nombre}'.")   

    def menu_comandos(self, band = True):
        print("\n----- Interfaz de comandos -----\n")
        while band:
            try:
                comando = input("> ")
            except KeyboardInterrupt:
                print("\n--- Error. Comando inválido.")
                continue
            if self.validar_configuracion(comando):
                if comando.startswith("git init"):
                    self.git_init(self.usuario)
                elif comando.startswith("git branch"):
                    nombre_rama = comando.removeprefix("git branch").strip()
                    self.git_branch(nombre_rama)
                elif comando.startswith("git checkout -b"):
                    nombre_rama = comando.removeprefix("git checkout -b").strip()
                    self.git_checkout_branch(nombre_rama)
                elif comando.startswith("git status"):
                    self.git_status()
                elif comando.startswith("git log"):
                    self.git_log()
                elif comando.startswith("git add"):
                    if comando.strip() == "git add .":
                        self.git_add()
                    else:
                        archivos = comando.removeprefix("git add").strip()           
                        self.git_add(archivos)
                elif comando.startswith("git commit -m"):
                    mensaje = comando.split("-m")[1].replace('"', '').strip()
                    self.git_commit(mensaje)
                elif comando.startswith("git checkout"):
                    commit_id = comando.removeprefix("git checkout").strip()
                    self.git_checkout(commit_id)
                elif comando.startswith("git pr create"):
                    if self.usuario != self.repositorio_actual.autor:
                        try:
                            ramaorigen = comando.removeprefix("git pr create").split(" ")[0].strip()
                            ramadestino = comando.removeprefix("git pr create").split(" ")[1].strip()
                            self.git_pr_create(ramaorigen, ramadestino)
                        except Exception as e:
                            print(f"\n--- Error inesperado : {e}.")
                    else:
                        print("> El autor del repositorio no puede ejecutar un Pull Request.")
                elif comando.startswith("git pr status"):
                    self.git_pr_status()
                elif comando.startswith("git pr review"):
                    pr_id = comando.removeprefix("git pr review").strip()
                    self.git_pr_review(pr_id)
                elif comando.startswith("git pr approve"):
                    if self.usuario == self.repositorio_actual.autor:
                        pr_id = comando.removeprefix("git pr approve").strip()
                        self.git_pr_approve(pr_id)
                    else:
                        print("> --- Error. Los Pull Requests sólo pueden ser aprobados por el autor del repositorio.")
                elif comando.startswith("git pr reject"):
                    if self.usuario == self.repositorio_actual.autor:
                        pr_id = comando.removeprefix("git pr reject").strip()
                        self.git_pr_reject(pr_id)
                    else:
                        print("> --- Error. Los Pull Requests sólo pueden ser rechazados por el autor del repositorio.")
                elif comando.startswith("git pr cancel"):
                    if self.usuario == self.repositorio_actual.autor:
                        pr_id = comando.removeprefix("git pr cancel").strip()
                        self.git_pr_cancel(pr_id)
                    else:
                        print("> --- Error. Los Pull Requests sólo pueden ser rechazados por el autor del repositorio.")
                elif comando.startswith("git pr list"):
                    self.git_pr_list()
                elif comando.startswith("git pr next"):
                    self.git_pr_next()
                elif comando.startswith("git pr tag"):
                    if self.usuario == self.repositorio_actual.autor:
                        try:
                            pr_id = comando.removeprefix("git pr tag").split(" ")[0].strip()
                            etiqueta = comando.removeprefix("git pr tag").split(" ")[1].strip()
                            self.git_pr_tag(pr_id,etiqueta)
                        except Exception as e:
                            print(f"\n--- Error inesperado : {e}.")
                    else:
                        print("> --- Error. Los Pull Requests sólo pueden ser etiquetados por el autor del repositorio.")
                elif comando.startswith("git pr clear"):
                    self.git_pr_clear()
                self.exportar_repositorios()
            else:
                if comando == "git exit":
                    band = False
                else:
                    print("> Error. Comando no reconocido.")
                    continue

    def validar_configuracion(self, comando):
        try:
            with open("configuracion.txt", "r") as archivo:
                for registro in archivo:
                    campos = registro.strip().split("=")
                    if len(campos) == 2:
                        clave, valor = campos
                        if comando.startswith(clave) and valor.strip().lower() == "true":
                            return True
            return False
        except FileNotFoundError:
            print("\n--- Error. El archivo 'configuracion.txt' no existe.")
            return False
        except Exception as exception:
            print(f"\n--- Error inesperado al leer el archivo de configuración: {exception}.")
            return False
    
    def git_init(self, usuario):
        repositorio_nuevo = Repositorio(usuario)
        temp = self.ultimo_repositorio
        while temp is not None:
            if temp.nombre == repositorio_nuevo.nombre:
                print(f"> --- Error. Ya existe un repositorio con el nombre: '{repositorio_nuevo.nombre}'.")
                return
            temp = temp.repositorio_siguiente
        if self.ultimo_repositorio is None:
            self.ultimo_repositorio = repositorio_nuevo
        else:
            temp = self.ultimo_repositorio
            while temp.repositorio_siguiente is not None:
                temp = temp.repositorio_siguiente
            temp.repositorio_siguiente = repositorio_nuevo
        self.repositorio_actual = repositorio_nuevo
        print(f"> Repositorio inicializado: '{repositorio_nuevo.nombre}'.")

    def git_branch(self, nombre):
        if not self.repositorio_actual:
            print("> --- Error. No hay un repositorio activo.")
            return
        self.repositorio_actual.gestion_ramas.agregar_rama(nombre)

    def git_checkout_branch(self, nombre):
        if not self.repositorio_actual:
            print("> --- Error. No hay un repositorio activo.")
            return
        self.repositorio_actual.gestion_ramas.seleccionar_rama(nombre)
        if self.repositorio_actual.gestion_ramas.rama_actual.nombre == nombre:
            self.repositorio_actual.gestion_commits.commit_seleccionado = self.repositorio_actual.gestion_ramas.rama_actual.ultimo_commit
        # Actualizar el directorio de trabajo.
        self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza = None
        archivos_commit = self.repositorio_actual.gestion_commits.commit_seleccionado.archivos_modificados
        for archivo in archivos_commit:
            if not self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza:
                self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza = archivo.archivo
                self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza.archivo_siguiente = None
            else:
                actual = self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza
                while actual.archivo_siguiente:
                    actual = actual.archivo_siguiente
                actual.archivo_siguiente = archivo.archivo
                actual.archivo_siguiente.archivo_siguiente = None

    def git_status(self):
        if not self.repositorio_actual:
            print("> --- Error. No hay un repositorio activo.")
            return
        print(f"\nRama activa: {self.repositorio_actual.gestion_ramas.rama_actual.nombre}")
        if self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza:
            print("\t--- Archivos en el directorio de trabajo")
            temp = self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza
            while temp:
                print(f"\t\t{temp.archivo}")
                temp = temp.archivo_siguiente
            for archivo in self.repositorio_actual.gestion_directoriotrabajo.archivos_eliminados:
                print(f"\t\t{archivo} (Eliminado)")
        if self.repositorio_actual.gestion_areastaging.archivostaged_cabeza:
            print("\t--- Archivos en el staging area")
            temp = self.repositorio_actual.gestion_areastaging.archivostaged_cabeza
            while temp:
                print(f"\t\t{temp.checksum}   {temp.archivo.archivo}   {temp.estado}")
                temp = temp.archivostaged_siguiente
        if self.repositorio_actual.gestion_commits.commit_seleccionado:
            print(f"\t--- Archivos actualizados en el repositorio: '{self.repositorio_actual.nombre}'")
            temp = self.repositorio_actual.gestion_commits.commit_seleccionado
            for archivo in temp.archivos_modificados:
                print(f"\t\t{archivo.checksum}   {archivo.archivo.archivo}   {archivo.archivo.contenido}")
        elif not self.repositorio_actual.gestion_areastaging.archivostaged_cabeza and not self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza:
            print(f"> --- No hay cambios en el repositorio '{self.repositorio_actual.nombre}'")

    def git_log(self):
        if not self.repositorio_actual:
            print("> --- Error. No hay un repositorio activo.")
            return
        if self.repositorio_actual.gestion_commits.commit_actual:
            print(f"\n----- Historial de commits: {self.repositorio_actual.nombre} -----")
            temp = self.repositorio_actual.gestion_commits.commit_actual
            while temp:
                print(f"      {temp.hash}   {temp.autor}   {temp.fecha}   {temp.mensaje}")
                temp = temp.commit_anterior
        else:
            print(f"\n--- No hay commits en el repositorio '{self.repositorio_actual.nombre}'")

    def git_add(self, archivos = None):
        if not self.repositorio_actual:
            print("> --- Error. No hay un repositorio activo.")
            return
        if archivos is None: 
            actual = self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza
            if not actual:
                print("> --- Error. No hay archivos en el directorio de trabajo.")
                return
            while actual:
                self.repositorio_actual.gestion_areastaging.agregar_archivostaged(actual)
                actual = actual.archivo_siguiente
        else:
            nombres_archivos = archivos.split(" ")
            for nombre in nombres_archivos:
                actual = self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza
                encontrado = False
                while actual:
                    if actual.archivo == nombre:
                        self.repositorio_actual.gestion_areastaging.agregar_archivostaged(actual)
                        encontrado = True
                        break
                    actual = actual.archivo_siguiente
                if not encontrado:
                    print(f"> --- Error. El archivo '{nombre}' no existe en el directorio de trabajo.")
        self.repositorio_actual.gestion_areastaging.validar_eliminados()
        
    def git_commit(self, mensaje):
        if not self.repositorio_actual:
            print("> --- Error. No hay un repositorio activo.")
            return
        if self.repositorio_actual.gestion_directoriotrabajo.contar_archivos() != self.repositorio_actual.gestion_areastaging.contar_archivos_staged():
            print("> --- Error. No pueden existir archivos modificados fuera del staging area.")
            return
        if self.usuario == self.repositorio_actual.autor:
            self.repositorio_actual.gestion_commits.agregar_commit(self.usuario, mensaje, self.repositorio_actual.gestion_areastaging.archivostaged_cabeza, self.repositorio_actual.gestion_ramas.rama_actual)
            self.repositorio_actual.gestion_areastaging.archivostaged_cabeza = None
            self.repositorio_actual.gestion_areastaging.ultimo_commit = self.repositorio_actual.gestion_commits.commit_actual
            self.repositorio_actual.gestion_ramas.rama_actual.ultimo_commit = self.repositorio_actual.gestion_commits.commit_actual
            # Actualizar el directorio de trabajo.
            self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza = None
            archivos_commit = self.repositorio_actual.gestion_commits.commit_actual.archivos_modificados
            for archivo in archivos_commit:
                if not self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza:
                    self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza = archivo.archivo
                    self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza.archivo_siguiente = None
                else:
                    actual = self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza
                    while actual.archivo_siguiente:
                        actual = actual.archivo_siguiente
                    actual.archivo_siguiente = archivo.archivo
                    actual.archivo_siguiente.archivo_siguiente = None
        else:
            temp = self.repositorio_actual.gestion_areastaging.archivostaged_cabeza
            commit_nuevo = Commit(self.usuario, mensaje, temp, self.repositorio_actual.gestion_ramas.rama_actual)
            self.repositorio_actual.gestion_pullrequest.temp_areaStaged = temp
            self.repositorio_actual.gestion_areastaging.archivostaged_cabeza = None
            print("> Commit ejecutado como colaborador.")
        
    def git_checkout(self, commit_id):
        if not self.repositorio_actual:
            print("> --- Error. No hay un repositorio activo.")
            return
        if not self.repositorio_actual.gestion_commits.commit_actual:
            print(f"> --- Error. No hay commits en el repositorio: '{self.repositorio_actual.nombre}'.")
            return
        temp = self.repositorio_actual.gestion_commits.commit_actual
        while temp:
            if temp.hash == commit_id:
                self.repositorio_actual.gestion_commits.commit_seleccionado = temp
            temp = temp.commit_anterior
        # Actualizar el directorio de trabajo.
        self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza = None
        archivos_commit = self.repositorio_actual.gestion_commits.commit_seleccionado.archivos_modificados
        for archivo in archivos_commit:
            if not self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza:
                self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza = archivo.archivo
                self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza.archivo_siguiente = None
            else:
                actual = self.repositorio_actual.gestion_directoriotrabajo.archivo_cabeza
                while actual.archivo_siguiente:
                    actual = actual.archivo_siguiente
                actual.archivo_siguiente = archivo.archivo
                actual.archivo_siguiente.archivo_siguiente = None
        print(f"> --- Commit {commit_id} seleccionado.")

    def git_pr_create(self, ramaorigen, ramadestino):
        self.repositorio_actual.gestion_pullrequest.crear_pullRequest(ramaorigen, ramadestino, self.usuario)

    def git_pr_status(self):
        self.repositorio_actual.gestion_pullrequest.status_list()

    def git_pr_review(self, id):
        self.repositorio_actual.gestion_pullrequest.review(id)

    def git_pr_approve(self, id):
        pr = self.repositorio_actual.gestion_pullrequest.approve(id)
        area_staged = self.repositorio_actual.gestion_pullrequest.temp_areaStaged
        self.ultimo_repositorio.gestion_commits.agregar_commit(self.usuario,"Commit aprobado", area_staged, pr.rama_destino)

    def git_pr_reject(self, id):
        self.repositorio_actual.gestion_pullrequest.reject(id)

    def git_pr_cancel(self, id):
        self.repositorio_actual.gestion_pullrequest.cancel(id)

    def git_pr_list(self):
        self.repositorio_actual.gestion_pullrequest.status_list()

    def git_pr_next(self):
        self.repositorio_actual.gestion_pullrequest.next_()

    def git_pr_tag(self,id_pr,etiqueta):
        self.repositorio_actual.gestion_pullrequest.tag(id_pr,etiqueta)
    
    def git_pr_clear(self):
        self.repositorio_actual.gestion_pullrequest.pullrequest_cabeza = None
    
    def exportar_repositorios(self, archivo_salida = "repositorios.json"):
        if not self.ultimo_repositorio:
            print("\n--- Error. No hay repositorios para exportar.")
            return
        repositorios = []
        temp = self.ultimo_repositorio
        while temp:
            repositorios.append({
                "nombre": temp.nombre,
                "autor": temp.autor,
                "ramas": self._exportar_ramas(temp.gestion_ramas),
                "directorio": self._exportar_directorio(temp.gestion_directoriotrabajo.archivo_cabeza),
                "staging": self._exportar_staging(temp.gestion_areastaging),
                "commits": self._exportar_commits(temp.gestion_commits.commit_actual),
                "pullrequests": self._exportar_pullrequests()
            })
            temp = temp.repositorio_siguiente
        with open(archivo_salida, "w", encoding="utf-8") as archivo:
            json.dump(repositorios, archivo, indent=4, ensure_ascii=False)
    
    def _exportar_ramas(self, gestion_ramas):
        gestionramas = [
            {"rama_actual": gestion_ramas.rama_actual.nombre}
        ]
        ramas = []
        temp = gestion_ramas.rama_cabeza
        while temp:
            ramas.append({
                "nombre": temp.nombre,
                "ultimo_commit": temp.ultimo_commit.hash if temp.ultimo_commit else None,
                "rama_siguiente": temp.rama_siguiente.nombre if temp.rama_siguiente else None
            })
            temp = temp.rama_siguiente
        gestionramas.append(ramas)
        return gestionramas
    
    def _exportar_directorio(self, archivo_cabeza):
        gestiondirectorio = []
        temp = archivo_cabeza
        while temp:
            gestiondirectorio.append({
                "archivo": temp.archivo,
                "contenido": temp.contenido,
                "archivo_siguiente": temp.archivo_siguiente.archivo if temp.archivo_siguiente else None
            })
            temp = temp.archivo_siguiente
        return gestiondirectorio

    def _exportar_staging(self, gestion_staging):
        gestionstaging = [
            {"ultimo_commit": gestion_staging.ultimo_commit.hash if gestion_staging.ultimo_commit else None}
        ]
        areas = []
        temp = gestion_staging.archivostaged_cabeza
        while temp:
            areas.append({
                "nombre": temp.archivo.archivo,
                "contenido": temp.archivo.contenido,
                "archivo_siguiente": temp.archivo.archivo_siguiente.archivo if temp.archivo.archivo_siguiente else None,
                "estado": temp.estado,
                "ruta": temp.ruta,
                "checksum": temp.checksum,
                "archivostaged_siguiente": temp.archivostaged_siguiente.checksum if temp.archivostaged_siguiente else None 
            })
            temp = temp.archivostaged_siguiente
        gestionstaging.append(areas)
        return gestionstaging

    def _exportar_commits(self, commit_actual):
        commits = []
        temp = commit_actual
        while temp:
            try:
                nombre_rama = temp.nombre_rama.nombre
            except AttributeError:
                nombre_rama = None
            commits.append({
                "hash": temp.hash,
                "autor": temp.autor,
                "fecha": temp.fecha,
                "mensaje": temp.mensaje,
                "commitanterior": temp.commit_anterior.hash if temp.commit_anterior else None,
                "archivos_modificados": [
                    {"nombre": archivo.archivo.archivo, "contenido": archivo.archivo.contenido, "estado": archivo.estado, "ruta": archivo.ruta, "checksum": archivo.checksum}
                    for archivo in temp.archivos_modificados
                ],
                "rama": nombre_rama,
                "hash": temp.hash,
            })
            temp = temp.commit_anterior
        return commits
    
    def _exportar_pullrequests(self):
        gestion_pullrequests = []
        temp = self.repositorio_actual.gestion_pullrequest.pullrequest_cabeza
        while temp:
            gestion_pullrequests.append({
                "id": temp.id,
                "rama_origen": temp.rama_origen,
                "rama_destino": temp.rama_destino,
                "autor": temp.autor,
                "estado": temp.estado,
                "lista_commits": [
                    {"hash": commit.hash, "autor": commit.autor, "fecha": commit.fecha, "mensaje": commit.mensaje, "rama": commit.nombre_rama.nombre}
                    for commit in temp.lista_commits
                ]
            })
            break
            temp = temp.pullrequest_siguiente
        return gestion_pullrequests

    def importar_repositorios(self, archivo_entrada = "repositorios.json"):
        try:
            with open(archivo_entrada, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            self.ultimo_repositorio = None
            for repo_data in datos:
                nuevo_repositorio = Repositorio(repo_data["autor"])
                nuevo_repositorio.nombre = repo_data["nombre"]
                nuevo_repositorio.gestion_ramas = self._importar_ramas(repo_data["ramas"])
                nuevo_repositorio.gestion_directoriotrabajo.archivo_cabeza = self._importar_directorio(repo_data["directorio"])
                nuevo_repositorio.gestion_areastaging = self._importar_staging(repo_data["staging"])
                nuevo_repositorio.gestion_commits.commit_actual = self._importar_commits(repo_data["commits"], nuevo_repositorio.gestion_ramas)
                nuevo_repositorio.gestion_pullrequest = self._importar_pullrequests(repo_data["pullrequests"])
                if self.ultimo_repositorio is None:
                    self.ultimo_repositorio = nuevo_repositorio
                else:
                    temp = self.ultimo_repositorio
                    while temp.repositorio_siguiente is not None:
                        temp = temp.repositorio_siguiente
                    temp.repositorio_siguiente = nuevo_repositorio
        except FileNotFoundError:
            return
        except Exception as e:
            print(f"\n--- Error inesperado al importar repositorios: {e}.")

    def _importar_ramas(self, ramas_data):
        gestion_ramas = GestionRamas()
        ramas = {}
        for rama_data in ramas_data[1]:
            nueva_rama = Rama(rama_data["nombre"])
            nueva_rama.ultimo_commit = None
            ramas[rama_data["nombre"]] = nueva_rama
            if rama_data["rama_siguiente"]:
                nueva_rama.rama_siguiente = ramas.get(rama_data["rama_siguiente"])
        gestion_ramas.rama_cabeza = next(iter(ramas.values()), None)
        gestion_ramas.rama_actual = ramas[ramas_data[0]["rama_actual"]]
        return gestion_ramas

    def _importar_directorio(self, directorio_data):
        cabeza = None
        actual = None
        for archivo_data in directorio_data:
            nuevo_archivo = Archivo(archivo_data["archivo"], archivo_data["contenido"])
            if not cabeza:
                cabeza = nuevo_archivo
            else:
                actual.archivo_siguiente = nuevo_archivo
            actual = nuevo_archivo

        return cabeza

    def _importar_staging(self, staging_data):
        gestion_staging = GestionAreaStaging()
        gestion_staging.ultimo_commit = None  # Se asignará al importar commits
        cabeza = None
        actual = None
        for archivo_data in staging_data[1]:  # Saltar el primer elemento (último commit)
            nuevo_archivo_staged = ArchivoStaged(
                archivo=Archivo(archivo_data["nombre"], archivo_data["contenido"]),
                estado=archivo_data["estado"],
                ruta=archivo_data["ruta"],
                checksum=archivo_data["checksum"]
            )
            if not cabeza:
                cabeza = nuevo_archivo_staged
            else:
                actual.archivostaged_siguiente = nuevo_archivo_staged
            actual = nuevo_archivo_staged

        gestion_staging.archivostaged_cabeza = cabeza
        return gestion_staging

    def _importar_commits(self, commits_data, gestion_ramas):
        commits = {}
        commit_actual = None
        for commit_data in commits_data:
            nuevo_commit = Commit(
                autor=commit_data["autor"],
                mensaje=commit_data["mensaje"],
                hash=commit_data["hash"],
                fecha=commit_data["fecha"],
                nombre_rama=gestion_ramas.rama_actual
            )
            nuevo_commit.archivos_modificados = [
                ArchivoStaged(
                    archivo=Archivo(archivo["nombre"], archivo["contenido"]),
                    estado=archivo["estado"],
                    ruta=archivo["ruta"],
                    checksum=archivo["checksum"]
                )
                for archivo in commit_data["archivos_modificados"]
            ]
            if commit_data["commitanterior"]:
                nuevo_commit.commit_anterior = commits[commit_data["commitanterior"]]
            commits[commit_data["hash"]] = nuevo_commit
            commit_actual = nuevo_commit
        return commit_actual
    
    def _importar_pullrequests(self, pullrequests_data):
        gestion_pullrequests = GestionPullRequests()
        for pr_data in pullrequests_data:
            nuevo_pr = PullRequest(
                id=pr_data["id"],
                rama_origen=pr_data["rama_origen"],
                rama_destino=pr_data["rama_destino"],
                autor=pr_data["autor"],
                estado=pr_data["estado"],
                lista_commits=[Commit(
                    hash=commit["hash"],
                    autor=commit["autor"],
                    fecha=commit["fecha"],
                    mensaje=commit["mensaje"],
                    nombre_rama=Rama(commit["rama"])
                ) for commit in pr_data["lista_commits"]]
            )
            gestion_pullrequests.agregar_pullrequest(nuevo_pr)
        return gestion_pullrequests