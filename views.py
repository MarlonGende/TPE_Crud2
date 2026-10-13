from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


class CrudBase(ABC):
    # Origen: Importado y usado por views.py.
    # Destino: views.py -> Define la interfaz y los métodos abstractos para EstudianteController, MateriaController y MatriculaController.

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


class EstudianteController(CrudBase):
    # Origen: views.py -> Implementa CrudBase. Instanciado en main.py.
    # Destino: models.py (Estudiante), shared/json_manager.py (GestorJSON) y main.py.

    def __init__(self, archivo="data/estudiantes.json"):
        # Origen: main.py -> Invocado al iniciar el sistema.
        # Destino: shared/json_manager.py -> Inicializa GestorJSON, lee disco y carga self.lista mediante Estudiante.desde_diccionario().
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        # Origen: views.py -> Invocado por crear(), actualizar() y eliminar().
        # Destino: shared/json_manager.py -> Serializa los objetos de self.lista llamando a a_diccionario() y los guarda en disco.
        datos = [e.a_diccionario() for e in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        # Origen: views.py -> Invocado internamente por crear() y actualizar().
        # Destino: shared/herramientas.py -> Llama a es_email_valido() y verifica unicidad de carnet y email mediante conjuntos (set). Retorna error o None.
        if id_actual is None:
            for campo in ("nombre", "apellido", "email", "carnet"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            emails_usados = {e.email for e in self.lista if e.id != id_actual}
            if email in emails_usados:
                return "Ese email ya está registrado"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()
            carnets_usados = {e.carnet.upper() for e in self.lista if e.id != id_actual}
            if carnet in carnets_usados:
                return f"El carnet '{carnet}' ya está registrado"

        return None

    def leer(self):
        # Origen: main.py -> Invocado por listar_estudiantes(), matricular() y resumen().
        # Destino: main.py -> Retorna la lista en memoria self.lista.
        return self.lista

    def obtener(self, id_estudiante):
        # Origen: main.py (ver, actualizar, eliminar) y MatriculaController (validar).
        # Destino: Retorna la instancia de Estudiante coincidente o None.
        for estudiante in self.lista:
            if estudiante.id == id_estudiante:
                return estudiante
        return None

    def buscar(self, texto):
        # Origen: main.py -> Invocado por buscar_estudiante().
        # Destino: main.py -> Retorna una lista filtrada de objetos Estudiante según los términos coincidentes.
        texto = texto.strip().lower()
        if not texto:
            return []

        encontrados = []
        for e in self.lista:
            if (texto in e.nombre.lower()
                    or texto in e.apellido.lower()
                    or texto in e.email.lower()
                    or texto in e.carnet.lower()
                    or texto in e.carrera.lower()):
                encontrados.append(e)
        return encontrados

    def siguiente(self):
        # Origen: views.py -> Invocado internamente por crear().
        # Destino: Retorna un entero correspondiente al siguiente ID correlativo.
        mayor = 0
        for e in self.lista:
            if e.id > mayor:
                mayor = e.id
        return mayor + 1

    def crear(self, datos):
        # Origen: main.py -> Invocado por crear_estudiante() con datos de entrada por consola.
        # Destino: views.py (validar, siguiente), models.py (Estudiante), shared/json_manager.py (guardar) -> Retorna (bool, mensaje) a main.py.
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos.get("carnet", "")).strip().upper(),
            str(datos.get("carrera", "")).strip().title()
        )
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        # Origen: main.py -> Invocado por actualizar_estudiante() con los campos a modificar.
        # Destino: views.py (obtener, validar, guardar) -> Muta el objeto Estudiante y retorna (bool, mensaje) a main.py.
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        # Origen: main.py -> Invocado por eliminar_estudiante() tras confirmación.
        # Destino: views.py (obtener, guardar) -> Remueve el objeto de self.lista y retorna (bool, mensaje) a main.py.
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    def carreras(self):
        # Origen: main.py -> Invocado por resumen().
        # Destino: main.py -> Retorna una lista ordenada de carreras únicas mediante un conjunto (set).
        return sorted({e.carrera for e in self.lista if e.carrera != ""})


class MateriaController(CrudBase):
    # Origen: views.py -> Implementa CrudBase. Instanciado en main.py.
    # Destino: models.py (Materia), shared/json_manager.py (GestorJSON) y main.py.

    def __init__(self, archivo="data/materias.json"):
        # Origen: main.py -> Invocado al iniciar el sistema.
        # Destino: shared/json_manager.py -> Inicializa GestorJSON y puebla self.lista mediante Materia.desde_diccionario().
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        # Origen: views.py -> Invocado por crear(), actualizar(), eliminar() y MatriculaController.
        # Destino: shared/json_manager.py -> Serializa los objetos llamando a a_diccionario() y los guarda en disco.
        datos = [m.a_diccionario() for m in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        # Origen: views.py -> Invocado internamente por crear() y actualizar().
        # Destino: Evalúa campos obligatorios, unicidad de código mediante conjuntos (set), créditos y cupos. Retorna error o None.
        if id_actual is None:
            for campo in ("nombre", "codigo"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            codigos_usados = {m.codigo for m in self.lista if m.id != id_actual}
            if codigo in codigos_usados:
                return f"El código '{codigo}' ya existe"

        if "creditos" in datos:
            try:
                cred = int(datos["creditos"])
                if not (1 <= cred <= 10):
                    return "Los créditos deben ser un número entero entre 1 y 10"
            except (TypeError, ValueError):
                return "Los créditos deben ser un número entero"

        if "cupos" in datos:
            try:
                cup = int(datos["cupos"])
                if not (0 <= cup <= Materia.CUPOS_MAXIMOS):
                    return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}"
            except (TypeError, ValueError):
                return "Los cupos deben ser un número entero"

        return None

    def leer(self):
        # Origen: main.py -> Invocado por listar_materias(), matricular() y resumen().
        # Destino: main.py -> Retorna la lista en memoria self.lista.
        return self.lista

    def obtener(self, id_materia):
        # Origen: main.py (ver, actualizar, eliminar) y MatriculaController (validar, crear, eliminar).
        # Destino: Retorna la instancia de Materia coincidente o None.
        for materia in self.lista:
            if materia.id == id_materia:
                return materia
        return None

    def buscar(self, texto):
        # Origen: main.py -> Invocado por buscar_materia().
        # Destino: main.py -> Retorna una lista filtrada de objetos Materia según coincidencias con nombre o código.
        texto = texto.strip().lower()
        if not texto:
            return []

        encontrados = []
        for m in self.lista:
            if texto in m.nombre.lower() or texto in m.codigo.lower():
                encontrados.append(m)
        return encontrados

    def siguiente(self):
        # Origen: views.py -> Invocado internamente por crear().
        # Destino: Retorna un entero correspondiente al siguiente ID correlativo.
        mayor = 0
        for m in self.lista:
            if m.id > mayor:
                mayor = m.id
        return mayor + 1

    def crear(self, datos):
        # Origen: main.py -> Invocado por crear_materia() con los datos leídos de consola.
        # Destino: views.py (validar, siguiente), models.py (Materia), shared/json_manager.py (guardar) -> Retorna (bool, mensaje) a main.py.
        error = self.validar(datos)
        if error:
            return False, error

        creditos = int(datos.get("creditos", 3))
        cupos = int(datos.get("cupos", Materia.CUPOS_MAXIMOS))

        materia = Materia(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["codigo"]).strip().upper(),
            creditos,
            cupos
        )
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        # Origen: main.py -> Invocado por actualizar_materia().
        # Destino: views.py (obtener, validar, guardar) -> Muta el objeto Materia y retorna (bool, mensaje) a main.py.
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe la materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "codigo", "creditos", "cupos"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            materia.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        # Origen: main.py -> Invocado por eliminar_materia().
        # Destino: views.py (obtener, guardar) -> Remueve la materia de self.lista y retorna (bool, mensaje) a main.py.
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe la materia con id {id_materia}"

        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    def materias_sin_cupo(self):
        # Origen: main.py -> Invocado por resumen().
        # Destino: models.py -> Consulta m.hay_cupo() y retorna a main.py la lista de materias agotadas.
        return [m for m in self.lista if not m.hay_cupo()]


class MatriculaController(CrudBase):
    # Origen: views.py -> Implementa CrudBase. Instanciado en main.py recibiendo referencias de estudiantes y materias.
    # Destino: EstudianteController, MateriaController, models.py (Matricula), shared/json_manager.py y main.py.

    def __init__(self, estudiantes, materias, archivo="data/matriculas.json"):
        # Origen: main.py -> Invocado al inicio inyectando los controladores dependientes.
        # Destino: shared/json_manager.py -> Inicializa GestorJSON y puebla self.lista llamando a Matricula.desde_diccionario().
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        # Origen: views.py -> Invocado por crear(), eliminar() y registrar_nota().
        # Destino: shared/json_manager.py -> Serializa los objetos de self.lista mediante a_diccionario() y los guarda en disco.
        datos = [m.a_diccionario() for m in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos):
        # Origen: views.py -> Invocado internamente por crear().
        # Destino: EstudianteController (obtener), MateriaController (obtener) y models.py (hay_cupo). Valida integridad y duplicados; retorna error o None.
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
            periodo = str(datos.get("periodo", "")).strip()
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser números enteros"

        if not periodo:
            return "El periodo es obligatorio (ej. 2026-1)"

        if self.estudiantes.obtener(estudiante_id) is None:
            return f"No existe el estudiante con id {estudiante_id}"

        materia = self.materias.obtener(materia_id)
        if materia is None:
            return f"No existe la materia con id {materia_id}"

        if not materia.hay_cupo():
            return f"Sin cupos disponibles para {materia.nombre}"

        for mat in self.lista:
            if (mat.estudiante_id == estudiante_id and
                    mat.materia_id == materia_id and
                    mat.periodo.upper() == periodo.upper()):
                return f"El estudiante ya está matriculado en {materia.nombre} para el periodo {periodo}"

        return None

    def leer(self):
        # Origen: main.py -> Invocado por listar_matriculas() y resumen().
        # Destino: main.py -> Retorna la lista en memoria self.lista.
        return self.lista

    def obtener(self, id_matricula):
        # Origen: views.py -> Invocado por eliminar(), registrar_nota() y certificado().
        # Destino: Retorna la instancia de Matricula coincidente o None.
        for m in self.lista:
            if m.id == id_matricula:
                return m
        return None

    def buscar(self, texto):
        # Origen: main.py -> Invocado para filtrar matrículas.
        # Destino: main.py -> Retorna coincidencias por periodo o fecha.
        texto = texto.strip().lower()
        if not texto:
            return []

        encontradas = []
        for m in self.lista:
            if texto in m.periodo.lower() or texto in m.fecha:
                encontradas.append(m)
        return encontradas

    def siguiente(self):
        # Origen: views.py -> Invocado internamente por crear().
        # Destino: Retorna un entero con el siguiente ID correlativo para la matrícula.
        mayor = 0
        for m in self.lista:
            if m.id > mayor:
                mayor = m.id
        return mayor + 1

    def crear(self, datos):
        # Origen: main.py -> Invocado por matricular().
        # Destino: views.py (validar), MateriaController (obtener, guardar), models.py (ocupar_cupo, Matricula), shared/json_manager.py (guardar) -> Retorna (bool, mensaje) a main.py.
        error = self.validar(datos)
        if error:
            return False, error

        materia = self.materias.obtener(int(datos["materia_id"]))
        matricula = Matricula(
            self.siguiente(),
            int(datos["estudiante_id"]),
            materia.id,
            str(datos["periodo"]).strip(),
            nota=float(datos.get("nota", 0.0))
        )

        materia.ocupar_cupo()
        self.materias.guardar()
        self.lista.append(matricula)
        self.guardar()
        return True, f"Matrícula {matricula.id} registrada exitosamente"

    def actualizar(self, id_matricula, datos):
        # Origen: main.py -> Invocado si se intentase edición genérica.
        # Destino: main.py -> Retorna False con mensaje indicando usar métodos dedicados.
        return False, "Las matrículas no se modifican directamente: use 'Registrar nota' o 'Retirar matrícula'"

    def eliminar(self, id_matricula):
        # Origen: main.py -> Invocado por retirar_matricula().
        # Destino: views.py (obtener), MateriaController (obtener, guardar), models.py (liberar_cupo), shared/json_manager.py (guardar) -> Retorna (bool, mensaje) a main.py.
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matrícula {id_matricula} retirada y cupo liberado"

    def registrar_nota(self, id_matricula, nota):
        # Origen: main.py -> Invocado por registrar_nota().
        # Destino: views.py (obtener, guardar), models.py (Materia.es_nota_valida, estado) -> Muta la nota y retorna (bool, mensaje) a main.py.
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        if not Materia.es_nota_valida(nota):
            return False, f"Nota inválida: '{nota}' (debe ser de 0 a 20)"

        matricula.nota = float(nota)
        self.guardar()
        return True, f"Nota actualizada: {matricula.nota:.1f} ({matricula.estado()})"

    def certificado(self, id_matricula):
        # Origen: main.py -> Invocado por ver_certificado().
        # Destino: EstudianteController (leer), MateriaController (leer), models.py (nombre_completo, estado) -> Genera texto formateado y lo retorna a main.py.
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return None

        mapa_estudiantes = {e.id: e for e in self.estudiantes.leer()}
        mapa_materias = {m.id: m for m in self.materias.leer()}

        estudiante = mapa_estudiantes.get(matricula.estudiante_id)
        materia = mapa_materias.get(matricula.materia_id)

        est_txt = f"{estudiante.nombre_completo()} ({estudiante.carnet})" if estudiante else "Estudiante no registrado"
        mat_txt = f"{materia.nombre} ({materia.codigo}) · {materia.creditos} créditos" if materia else "Materia no registrada"

        texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
        texto += f"Estudiante: {est_txt}\n"
        texto += f"Materia   : {mat_txt}\n"
        texto += "-" * 42 + "\n"
        texto += f"Nota      : {matricula.nota:.1f}\n"
        texto += f"Estado    : {matricula.estado()}"
        return texto

    def matriculas_por_estudiante(self):
        # Origen: views.py / main.py -> Invocado para agrupar cargas por alumno.
        # Destino: Retorna un diccionario donde las claves son estudiante_id y los valores listas de matrículas.
        agrupadas = {}
        for mat in self.lista:
            agrupadas.setdefault(mat.estudiante_id, []).append(mat)
        return agrupadas

    def promedio_de_estudiante(self, id_estudiante):
        # Origen: main.py -> Invocado por ver_estudiante().
        # Destino: main.py -> Itera sobre self.lista y retorna el promedio aritmético redondeado a dos decimales.
        mats = [m for m in self.lista if m.estudiante_id == id_estudiante]
        if not mats:
            return 0.0
        return round(sum(m.nota for m in mats) / len(mats), 2)