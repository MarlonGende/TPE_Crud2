from datetime import date


class ModeloBase:
    # Origen: Importado por models.py (clases hijas) y views.py (métodos de clase).
    # Destino: models.py -> Usado por Persona, Materia y Matricula como clase padre.

    def __init__(self, id_registro):
        # Origen: Invocado por super().__init__() desde Persona, Materia y Matricula.
        # Destino: models.py -> Asigna el atributo id a la instancia actual.
        self.id = int(id_registro)

    @classmethod
    def desde_diccionario(cls, datos):
        # Origen: views.py -> Invocado en los bucles de carga de EstudianteController, MateriaController y MatriculaController.
        # Destino: models.py -> Instancia la subclase correspondiente pasándole el id desempaquetado.
        datos = dict(datos)
        id_registro = datos.pop("id")
        return cls(id_registro, **datos)

    def a_diccionario(self):
        # Origen: Invocado por super().a_diccionario() desde subclases (Persona, Materia, Matricula) y por main.py (mostrar_detalle).
        # Destino: views.py / main.py -> Retorna un diccionario base con la clave "id".
        return {"id": self.id}

    def etiqueta(self):
        # Origen: Invocado internamente por __str__().
        # Destino: models.py -> Devuelve la representación genérica por defecto si no es sobreescrita.
        return f"registro {self.id}"

    def __str__(self):
        # Origen: main.py -> Invocado automáticamente al hacer print(objeto) en mostrar_lista().
        # Destino: models.py -> Llama a self.etiqueta() de la subclase correspondiente (despacho polimórfico).
        return f"[{self.id}] {self.etiqueta()}"


class Persona(ModeloBase):
    # Origen: models.py -> Hereda de ModeloBase.
    # Destino: models.py -> Usada como clase base por Estudiante.

    def __init__(self, id_registro, nombre, apellido, email):
        # Origen: models.py -> Invocado por super().__init__() desde Estudiante.
        # Destino: models.py -> Llama a ModeloBase.__init__() y asigna nombre, apellido y email.
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self):
        # Origen: views.py (certificado) y models.py (etiqueta).
        # Destino: Retorna una cadena con el nombre y apellido concatenados.
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        # Origen: models.py -> Invocado por super().a_diccionario() desde Estudiante.
        # Destino: Retorna el diccionario con datos de persona hacia la subclase.
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self):
        # Origen: models.py -> Invocado por super().etiqueta() desde Estudiante o por __str__().
        # Destino: models.py -> Llama a self.nombre_completo() y retorna la cadena.
        return self.nombre_completo()


class Estudiante(Persona):
    # Origen: models.py -> Hereda de Persona.
    # Destino: views.py (EstudianteController) y main.py (consumido como entidad).

    def __init__(self, id_registro, nombre, apellido, email, carnet="", carrera=""):
        # Origen: views.py -> Invocado por EstudianteController.crear() o ModeloBase.desde_diccionario().
        # Destino: models.py -> Llama a Persona.__init__() y asigna carnet y carrera.
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self):
        # Origen: views.py -> Invocado por EstudianteController.guardar() y main.py (mostrar_detalle).
        # Destino: shared/json_manager.py -> Provee el diccionario completo para persistir en disco.
        datos = super().a_diccionario()
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        # Origen: models.py -> Invocado por ModeloBase.__str__() y main.py (actualizar_estudiante, eliminar_estudiante).
        # Destino: main.py -> Retorna la cadena representativa formateada para la interfaz de consola.
        carrera_txt = self.carrera or "sin carrera"
        return f"{super().etiqueta()} · {self.carnet} · {carrera_txt}"


class Materia(ModeloBase):
    # Origen: models.py -> Hereda de ModeloBase.
    # Destino: views.py (MateriaController, MatriculaController) y main.py.

    CUPOS_MAXIMOS = 30
    NOTA_APROBACION = 14

    def __init__(self, id_registro, nombre, codigo, creditos=0, cupos=0):
        # Origen: views.py -> Invocado por MateriaController.crear() o ModeloBase.desde_diccionario().
        # Destino: models.py -> Llama a ModeloBase.__init__() y asigna propiedades académicas.
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo.upper()
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    @staticmethod
    def es_nota_valida(valor):
        # Origen: views.py -> Invocado por MatriculaController.registrar_nota().
        # Destino: Retorna un booleano indicando si el valor cae en el rango [0, 20].
        try:
            val = float(valor)
            return 0.0 <= val <= 20.0
        except (TypeError, ValueError):
            return False

    def hay_cupo(self):
        # Origen: views.py -> Invocado por MatriculaController.validar() y MateriaController.materias_sin_cupo().
        # Destino: Retorna un booleano evaluando si self.cupos es mayor que cero.
        return self.cupos > 0

    def ocupar_cupo(self):
        # Origen: views.py -> Invocado por MatriculaController.crear().
        # Destino: models.py -> Decrementa en 1 la propiedad self.cupos de la instancia.
        if self.hay_cupo():
            self.cupos -= 1

    def liberar_cupo(self):
        # Origen: views.py -> Invocado por MatriculaController.eliminar().
        # Destino: models.py -> Incrementa en 1 la propiedad self.cupos si no supera CUPOS_MAXIMOS.
        if self.cupos < Materia.CUPOS_MAXIMOS:
            self.cupos += 1

    def a_diccionario(self):
        # Origen: views.py -> Invocado por MateriaController.guardar() y main.py (mostrar_detalle).
        # Destino: shared/json_manager.py -> Provee el diccionario completo para persistir en materias.json.
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["codigo"] = self.codigo
        datos["creditos"] = self.creditos
        datos["cupos"] = self.cupos
        return datos

    def etiqueta(self):
        # Origen: models.py -> Invocado por ModeloBase.__str__() y main.py.
        # Destino: main.py -> Retorna los datos de la materia con advertencia si cupos == 0.
        alerta = " ⚠ sin cupo" if not self.hay_cupo() else ""
        return f"{self.nombre} ({self.codigo}) · {self.creditos} créd. · cupos: {self.cupos}{alerta}"


class Matricula(ModeloBase):
    # Origen: models.py -> Hereda de ModeloBase.
    # Destino: views.py (MatriculaController) y main.py.

    def __init__(self, id_registro, estudiante_id, materia_id, periodo, nota=0.0, fecha=""):
        # Origen: views.py -> Invocado por MatriculaController.crear() o ModeloBase.desde_diccionario().
        # Destino: models.py -> Llama a ModeloBase.__init__() y guarda referencias por id, periodo y nota.
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = periodo
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self):
        # Origen: models.py -> Invocado internamente por self.estado() y por main.py (resumen).
        # Destino: Retorna un booleano comparando la nota contra Materia.NOTA_APROBACION.
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        # Origen: models.py -> Invocado por self.etiqueta() y views.py (certificado, registrar_nota).
        # Destino: Retorna 'Aprobado' o 'Reprobado' de forma calculada en tiempo real.
        return "Aprobado" if self.esta_aprobada() else "Reprobado"

    def a_diccionario(self):
        # Origen: views.py -> Invocado por MatriculaController.guardar() y main.py (mostrar_detalle).
        # Destino: shared/json_manager.py -> Provee el diccionario para persistir en matriculas.json.
        datos = super().a_diccionario()
        datos["estudiante_id"] = self.estudiante_id
        datos["materia_id"] = self.materia_id
        datos["periodo"] = self.periodo
        datos["nota"] = self.nota
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self):
        # Origen: models.py -> Invocado por ModeloBase.__str__() y main.py.
        # Destino: main.py -> Retorna la cadena formateada con estudiante, materia, nota y estado.
        return (f"{self.fecha} · est. {self.estudiante_id} · "
                f"mat. {self.materia_id} ({self.periodo}) · Nota: {self.nota:.1f} ({self.estado()})")