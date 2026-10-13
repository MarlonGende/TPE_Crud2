from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import EstudianteController, MateriaController, MatriculaController


# Notas de input/ouput generadas con ayuda de IA, por cuestiones de legibilidad. 

# Origen: main.py -> Inicializa la capa de Controladores al importar el módulo.
# Destino: views.py -> Instancia EstudianteController, MateriaController y MatriculaController.
estudiantes = EstudianteController()
materias = MateriaController()
matriculas = MatriculaController(estudiantes, materias)


def pausa():
    # Origen: main.py -> Invocado al final de cada flujo de menú.
    # Destino: Consola -> Bloquea la ejecución hasta pulsar Enter.
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    # Origen: main.py -> Invocado en funciones de consulta y edición por ID.
    # Destino: Consola -> Captura la entrada del usuario y retorna un entero o None.
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    # Origen: main.py -> Invocado tras recibir la tupla de respuesta desde los controladores.
    # Destino: shared/herramientas.py -> Despacha la salida a imprimir_exito() o imprimir_error().
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    # Origen: main.py -> Invocado por listar_*, matricular() y buscar_*.
    # Destino: models.py -> Llama polimórficamente a __str__() sobre cada objeto de la colección y lo imprime en consola.
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    # Origen: main.py -> Invocado por ver_estudiante() y ver_materia().
    # Destino: models.py -> Invoca a_diccionario() e imprime cada clave y valor tabulados.
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


def crear_estudiante():
    # Origen: main.py -> Invocado por MENU_ESTUDIANTES ("1").
    # Destino: views.py -> Solicita inputs y envía el diccionario a EstudianteController.crear().
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet (ej. EST2026001): "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*estudiantes.crear(datos))
    pausa()


def listar_estudiantes():
    # Origen: main.py -> Invocado por MENU_ESTUDIANTES ("2").
    # Destino: views.py -> Llama a EstudianteController.leer() y despacha los objetos a mostrar_lista().
    imprimir_titulo("ESTUDIANTES")
    mostrar_lista(estudiantes.leer(), "Todavía no hay estudiantes registrados.")
    pausa()


def buscar_estudiante():
    # Origen: main.py -> Invocado por MENU_ESTUDIANTES ("3").
    # Destino: views.py -> Envía el término a EstudianteController.buscar() y despacha resultados a mostrar_lista().
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, carnet, email o carrera: ")
    encontrados = estudiantes.buscar(termino)
    mostrar_lista(encontrados, f"Ningún estudiante coincide con '{termino}'.")
    pausa()


def ver_estudiante():
    # Origen: main.py -> Invocado por MENU_ESTUDIANTES ("4").
    # Destino: views.py -> Consulta EstudianteController.obtener(), MatriculaController.promedio_de_estudiante() y llama a mostrar_detalle().
    imprimir_titulo("VER ESTUDIANTE POR ID")
    estudiante = estudiantes.obtener(pedir_entero("Id: "))
    if estudiante is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(estudiante)
        prom = matriculas.promedio_de_estudiante(estudiante.id)
        imprimir_info(f"Promedio general: {prom:.2f}")
    pausa()


def actualizar_estudiante():
    # Origen: main.py -> Invocado por MENU_ESTUDIANTES ("5").
    # Destino: views.py -> Lee los campos modificados y los envía a EstudianteController.actualizar().
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_est = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_est)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {estudiante.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*estudiantes.actualizar(id_est, cambios))
    pausa()


def eliminar_estudiante():
    # Origen: main.py -> Invocado por MENU_ESTUDIANTES ("6").
    # Destino: shared/herramientas.py (confirmar) y views.py (EstudianteController.eliminar).
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_est = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_est)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminará: {estudiante.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*estudiantes.eliminar(id_est))
    else:
        imprimir_info("Operación cancelada")
    pausa()


def crear_materia():
    # Origen: main.py -> Invocado por MENU_MATERIAS ("1").
    # Destino: views.py -> Solicita inputs de la materia y los envía a MateriaController.crear().
    imprimir_titulo("CREAR MATERIA")
    datos = {
        "nombre": input("Nombre: "),
        "codigo": input("Código (ej. MAT101): "),
        "creditos": input("Créditos (1 a 10): "),
        "cupos": input("Cupos (0 a 30): "),
    }
    mostrar_resultado(*materias.crear(datos))
    pausa()


def listar_materias():
    # Origen: main.py -> Invocado por MENU_MATERIAS ("2").
    # Destino: views.py -> Llama a MateriaController.leer() y despacha las materias a mostrar_lista().
    imprimir_titulo("MATERIAS")
    mostrar_lista(materias.leer(), "Todavía no hay materias.")
    pausa()


def buscar_materia():
    # Origen: main.py -> Invocado por MENU_MATERIAS ("3").
    # Destino: views.py -> Envía el término a MateriaController.buscar() y despacha resultados a mostrar_lista().
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o código: ")
    mostrar_lista(materias.buscar(termino), "Sin coincidencias.")
    pausa()


def ver_materia():
    # Origen: main.py -> Invocado por MENU_MATERIAS ("4").
    # Destino: views.py -> Consulta MateriaController.obtener() y despacha el objeto a mostrar_detalle().
    imprimir_titulo("VER MATERIA POR ID")
    materia = materias.obtener(pedir_entero("Id: "))
    if materia is None:
        imprimir_error("No encontrada")
    else:
        mostrar_detalle(materia)
    pausa()


def actualizar_materia():
    # Origen: main.py -> Invocado por MENU_MATERIAS ("5").
    # Destino: views.py -> Lee los cambios y los envía a MateriaController.actualizar().
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_mat = pedir_entero("Id: ")
    materia = materias.obtener(id_mat)
    if materia is None:
        imprimir_error("No encontrada")
        return pausa()

    imprimir_info(f"Editando: {materia.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "codigo", "creditos", "cupos"):
        actual = getattr(materia, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*materias.actualizar(id_mat, cambios))
    pausa()


def eliminar_materia():
    # Origen: main.py -> Invocado por MENU_MATERIAS ("6").
    # Destino: shared/herramientas.py (confirmar) y views.py (MateriaController.eliminar).
    imprimir_titulo("ELIMINAR MATERIA")
    id_mat = pedir_entero("Id: ")
    materia = materias.obtener(id_mat)
    if materia is None:
        imprimir_error("No encontrada")
        return pausa()

    imprimir_info(f"Se eliminará: {materia.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*materias.eliminar(id_mat))
    else:
        imprimir_info("Operación cancelada")
    pausa()


def matricular():
    # Origen: main.py -> Invocado por MENU_MATRICULAS ("1").
    # Destino: views.py -> Lista estudiantes/materias y envía los IDs con periodo a MatriculaController.crear().
    imprimir_titulo("REGISTRAR MATRÍCULA")
    imprimir_info("Estudiantes:")
    mostrar_lista(estudiantes.leer())
    imprimir_info("Materias:")
    mostrar_lista(materias.leer())

    datos = {
        "estudiante_id": pedir_entero("\nId del estudiante: "),
        "materia_id": pedir_entero("Id de la materia: "),
        "periodo": input("Periodo académico (ej. 2026-1): ").strip(),
    }
    if None in (datos["estudiante_id"], datos["materia_id"]):
        imprimir_error("Los IDs deben ser números enteros")
        return pausa()

    mostrar_resultado(*matriculas.crear(datos))
    pausa()


def listar_matriculas():
    # Origen: main.py -> Invocado por MENU_MATRICULAS ("2").
    # Destino: views.py -> Llama a MatriculaController.leer() y despacha las matrículas a mostrar_lista().
    imprimir_titulo("MATRÍCULAS")
    mostrar_lista(matriculas.leer(), "Todavía no hay matrículas.")
    pausa()


def registrar_nota():
    # Origen: main.py -> Invocado por MENU_MATRICULAS ("3").
    # Destino: views.py -> Solicita el ID y la nota y llama a MatriculaController.registrar_nota().
    imprimir_titulo("REGISTRAR NOTA")
    id_mat = pedir_entero("Id de la matrícula: ")
    if id_mat is None:
        imprimir_error("ID inválido")
        return pausa()

    nota = input("Nota obtenida (0 a 20): ")
    mostrar_resultado(*matriculas.registrar_nota(id_mat, nota))
    pausa()


def ver_certificado():
    # Origen: main.py -> Invocado por MENU_MATRICULAS ("4").
    # Destino: views.py -> Consulta MatriculaController.certificado() e imprime el texto resultante.
    imprimir_titulo("CERTIFICADO")
    id_mat = pedir_entero("Id de la matrícula: ")
    texto = matriculas.certificado(id_mat)
    if texto is None:
        imprimir_error("No existe esa matrícula")
    else:
        print(texto)
    pausa()


def retirar_matricula():
    # Origen: main.py -> Invocado por MENU_MATRICULAS ("5").
    # Destino: shared/herramientas.py (confirmar) y views.py (MatriculaController.eliminar).
    imprimir_titulo("RETIRAR MATRÍCULA")
    id_mat = pedir_entero("Id de la matrícula: ")
    if id_mat and confirmar("Se liberará el cupo en la materia. ¿Confirma?"):
        mostrar_resultado(*matriculas.eliminar(id_mat))
    else:
        imprimir_info("Operación cancelada")
    pausa()


def resumen():
    # Origen: main.py -> Invocado por main() ("4").
    # Destino: views.py (estudiantes, materias, matriculas) y models.py (esta_aprobada) -> Computa y muestra métricas globales en pantalla.
    imprimir_titulo("RESUMEN ACADÉMICO")
    print(f"  Estudiantes       : {len(estudiantes.leer())}")
    print(f"  Carreras          : {', '.join(estudiantes.carreras()) or '-'}")
    print(f"  Materias          : {len(materias.leer())}")
    sin_cupo = materias.materias_sin_cupo()
    print(f"  Materias sin cupo : {', '.join(m.nombre for m in sin_cupo) or 'ninguna'}")

    lista_mat = matriculas.leer()
    aprobadas = sum(1 for m in lista_mat if m.esta_aprobada())
    print(f"  Total matrículas  : {len(lista_mat)}")
    print(f"  Aprobadas         : {aprobadas}")
    pausa()


MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", crear_estudiante),
    "2": ("Ver todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por id", ver_estudiante),
    "5": ("Actualizar", actualizar_estudiante),
    "6": ("Eliminar", eliminar_estudiante),
    "0": ("Volver", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Ver todas", listar_materias),
    "3": ("Buscar", buscar_materia),
    "4": ("Ver por id", ver_materia),
    "5": ("Actualizar", actualizar_materia),
    "6": ("Eliminar", eliminar_materia),
    "0": ("Volver", None),
}

MENU_MATRICULAS = {
    "1": ("Matricular", matricular),
    "2": ("Ver todas", listar_matriculas),
    "3": ("Registrar nota", registrar_nota),
    "4": ("Ver certificado", ver_certificado),
    "5": ("Retirar matrícula", retirar_matricula),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    # Origen: main.py -> Invocado por main() con cada submenú.
    # Destino: main.py -> Despacha la llamada a la función mapeada en el diccionario de opciones.
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Opción: ").strip()
        if tecla not in opciones:
            imprimir_error("Opción no válida")
            pausa()
            continue

        _texto, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main():
    # Origen: Bloque principal de ejecución (__name__ == "__main__").
    # Destino: main.py -> Ejecuta el bucle principal y coordina la llamada a ejecutar_menu() o resumen().
    while True:
        imprimir_titulo("SISTEMA ACADÉMICO")
        print("  1. Estudiantes")
        print("  2. Materias")
        print("  3. Matrículas")
        print("  4. Resumen")
        print("  0. Salir\n")

        tecla = input("Opción: ").strip()
        if tecla == "1":
            ejecutar_menu("ESTUDIANTES", MENU_ESTUDIANTES)
        elif tecla == "2":
            ejecutar_menu("MATERIAS", MENU_MATERIAS)
        elif tecla == "3":
            ejecutar_menu("MATRÍCULAS", MENU_MATRICULAS)
        elif tecla == "4":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego! 👋")
            break
        else:
            imprimir_error("Opción no válida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")