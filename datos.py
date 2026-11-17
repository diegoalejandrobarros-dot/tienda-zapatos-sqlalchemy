"""Persistencia del inventario mediante SQLAlchemy ORM y SQLite."""

from pathlib import Path

from sqlalchemy import Float, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


# Se guarda junto a este archivo para que el resultado no dependa del
# directorio desde el que se invoque `python main.py`.
RUTA_BD = Path(__file__).resolve().with_name("zapateria.db")
engine = create_engine(f"sqlite:///{RUTA_BD}")


class Base(DeclarativeBase):
    """Clase base de los modelos declarativos."""


class Zapato(Base):
    """Modelo ORM que representa un registro de la tabla zapatos."""

    __tablename__ = "zapatos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    modelo: Mapped[str] = mapped_column(String(120), nullable=False)
    talla: Mapped[int] = mapped_column(Integer, nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)


def inicializar_bd():
    """Crea la base SQLite (si hace falta) y las tablas declaradas."""
    Base.metadata.create_all(engine)


def crear_zapato(modelo, talla, precio):
    """Inserta un zapato; devuelve False si falla la transacción."""
    try:
        with Session(engine) as sesion:
            sesion.add(Zapato(modelo=modelo, talla=talla, precio=precio))
            sesion.commit()
        return True
    except Exception:
        return False


def listar_zapatos():
    """Devuelve los zapatos como objetos ORM, ordenados por ID."""
    with Session(engine) as sesion:
        return list(sesion.scalars(select(Zapato).order_by(Zapato.id)))


def buscar_zapato(id_zapato):
    """Devuelve el zapato con ese ID o None si no existe."""
    with Session(engine) as sesion:
        return sesion.get(Zapato, id_zapato)


def actualizar_precio(id_zapato, nuevo_precio):
    """Actualiza el precio; devuelve False si el ID no está registrado."""
    with Session(engine) as sesion:
        zapato = sesion.get(Zapato, id_zapato)
        if zapato is None:
            return False
        zapato.precio = nuevo_precio
        sesion.commit()
        return True


def eliminar_zapato(id_zapato):
    """Elimina el zapato y devuelve False si no existe."""
    with Session(engine) as sesion:
        zapato = sesion.get(Zapato, id_zapato)
        if zapato is None:
            return False
        sesion.delete(zapato)
        sesion.commit()
        return True
