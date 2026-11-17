# Sistema de inventario de zapatos

## Información

- **Estudiante:** Diego Barros
- **Descripción:** aplicación de consola para administrar el inventario de una tienda de zapatos. Usa SQLAlchemy ORM para registrar, consultar, buscar, actualizar y eliminar zapatos en una base SQLite local.
- **Tecnologías:** Python 3.10 o posterior, SQLAlchemy 2.x y SQLite.

## Archivos

```text
tienda_zapatos/
├── main.py
├── datos.py
├── requirements.txt
├── README.md
├── zapateria.db       # se crea al ejecutar, no se distribuye
└── evidencias/        # capturas de las pruebas
```

`main.py` contiene el menú original y delega las operaciones a `datos.py`. Este último configura el engine y el modelo ORM, crea la tabla y contiene las cinco operaciones CRUD. `requirements.txt` declara SQLAlchemy. SQLite forma parte de Python; no requiere instalar un servidor aparte.

## Instalación y ejecución

Desde esta carpeta, con Python instalado:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

En la primera ejecución se crea `zapateria.db` al lado de `datos.py`. El menú permite elegir las opciones 1 a 6. La ruta está basada en `__file__`, por lo que iniciar el programa desde otra carpeta no crea accidentalmente otra base de datos.

## Implementación y respuestas técnicas

### 1. Modelo, tabla y columnas

La clase `Zapato` en `datos.py` hereda de `Base`, que hereda de `DeclarativeBase`. SQLAlchemy registra el modelo en `Base.metadata`. El atributo `__tablename__ = "zapatos"` fija el nombre de la tabla. Las anotaciones `Mapped[...]` y `mapped_column(...)` describen las columnas: `id` es entero, clave primaria y autoincremental; `modelo` es texto; `talla` es entero; `precio` es real (`Float`). Los campos de datos no permiten `NULL`.

### 2. Primera ejecución y creación de la base

Al entrar en `main()`, se llama `datos.inicializar_bd()`. Esta función usa `Base.metadata.create_all(engine)`. El engine se configuró con una URL `sqlite:///.../zapateria.db`; cuando SQLite abre por primera vez ese archivo, lo crea. `create_all` crea las tablas declaradas que aún no existan, entre ellas `zapatos`. En ejecuciones siguientes conserva el archivo y sus registros.

### 3. Recorrido del registro

La opción 1 de `main.py` lee modelo, talla y precio, convierte talla a `int` y precio a `float`, y rechaza datos no válidos. Luego llama `datos.crear_zapato(modelo, talla, precio)`. Esa función construye un objeto `Zapato`, abre una `Session(engine)`, lo incorpora con `sesion.add(...)` y confirma la transacción con `sesion.commit()`. Al finalizar correctamente devuelve `True` y el menú informa que el registro se realizó. SQLAlchemy asigna el ID al insertar.

### 4. Sesiones y confirmación

Una sesión representa la unidad de trabajo con la base: mantiene los objetos gestionados y agrupa cambios para consultarlos o confirmarlos dentro de una transacción. El código usa `with Session(engine) as sesion` para cerrar la sesión al terminar. Si se agrega o modifica un objeto sin `commit()`, el cambio no queda confirmado y, al cerrar la sesión, se revierte; no se debe esperar que sobreviva a una nueva sesión o ejecución. Por eso las funciones de escritura llaman explícitamente a `commit()`.

### 5. Búsqueda por ID

`buscar_zapato(id_zapato)` abre una sesión y usa `sesion.get(Zapato, id_zapato)`, que busca por la clave primaria. Devuelve el objeto `Zapato` encontrado o `None`. En el menú, `None` produce el mensaje “Zapato no encontrado”; cuando hay objeto, `mostrar_zapato` presenta sus campos. La instancia conserva los valores consultados y se puede leer después del cierre de la sesión.

### 6. Actualizar precio

`actualizar_precio(id_zapato, nuevo_precio)` obtiene el objeto con `sesion.get`. Si no existe, devuelve `False`. Si existe, asigna `zapato.precio = nuevo_precio` y hace `sesion.commit()`. SQLAlchemy detecta el atributo modificado y persiste el cambio. Devuelve `True`, tras lo cual el menú informa “Precio actualizado”. Se puede verificar con la opción de búsqueda o listado.

### 7. Eliminar

`eliminar_zapato(id_zapato)` recupera primero el objeto. Si no lo encuentra devuelve `False`; si existe, llama `sesion.delete(zapato)` y `sesion.commit()`, y devuelve `True`. Para comprobar la eliminación se vuelve a listar o buscar el mismo ID: ya no aparece en el listado y la búsqueda devuelve `None`.

### 8. Persistencia al reiniciar

Los registros permanecen al cerrar el programa porque `zapateria.db` es un archivo en disco y cada alta, actualización o eliminación confirma sus cambios con `commit()`. Al volver a ejecutar, el engine apunta al mismo archivo y la consulta reconstruye objetos desde esos datos. En una prueba de persistencia, registra los modelos, elige salir, inicia de nuevo y lista el inventario; documenta en las capturas qué IDs permanecieron.


Secuencia sugerida para una única base limpia:

1. Registra `Deportivo urbano`, talla `40`, precio `189900`; registra `Bota clásica`, talla `42`, precio `259900`.
2. Lista ambos productos; busca el ID `1`.
3. Cambia el precio del ID `1` a `199900` y vuelve a buscarlo para mostrar el nuevo valor.
4. Elimina el ID `2`, lista y/o busca el ID `2` para confirmar que ya no existe.
5. Busca, actualiza y elimina el ID `999999`; cada operación debe indicar que no se encontró.
6. Sal del programa, ejecútalo de nuevo y lista el inventario; el ID `1` debe conservar el precio `199900`.


### Resultado esperado para IDs inexistentes

| Operación | Resultado en el programa |
|---|---|
| Buscar ID inexistente | `buscar_zapato` devuelve `None`; se imprime “Zapato no encontrado.” |
| Actualizar ID inexistente | `actualizar_precio` devuelve `False`; se imprime “Zapato no encontrado.” |
| Eliminar ID inexistente | `eliminar_zapato` devuelve `False`; se imprime “Zapato no encontrado.” |
