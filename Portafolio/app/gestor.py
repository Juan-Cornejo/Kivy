# gestor.py
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Iterable
from kivy.app import App
from kivy.utils import platform

# -----------------------------
# Rutas y conexión
# -----------------------------


def get_db_path() -> str:
    """Devuelve la ruta del archivo SQLite según el entorno."""
    if platform == "android":
        return str(Path(App.get_running_app().user_data_dir) / "proyectos.db")
    else:
        # Usa .../Portafolio/data/proyectos.db
        return str(Path(__file__).parent.parent / "data" / "proyectos.db")


def get_schema_path() -> str:
    return str(Path(__file__).parent.parent / "data" / "schema.sql")


def connect() -> sqlite3.Connection:
    """Crea conexión a SQLite con Row factory y foreign_keys ON."""
    db_path = Path(get_db_path())
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con


# -----------------------------
# Inicialización
# -----------------------------
def init_db(use_schema: bool = True) -> None:
    """
    Inicializa la base.
    Si use_schema=True y existe data/schema.sql, lo ejecuta.
    """
    with connect() as con:
        if use_schema and Path(get_schema_path()).exists():
            with open(get_schema_path(), "r", encoding="utf-8") as f:
                con.executescript(f.read())


# -----------------------------
# Helpers genéricos
# -----------------------------
def _to_dicts(rows: Iterable[sqlite3.Row]) -> List[Dict]:
    return [dict(r) for r in rows]


# -----------------------------
# Usuario
# -----------------------------
def get_usuario():
    """Devuelve el primer usuario registrado en la base de datos."""
    with connect() as con:
        row = con.execute("""
            SELECT id_usuario, nombre_completo, profesion, github_url,
                   foto_perfil, introduccion, descripcion
            FROM usuario
            ORDER BY id_usuario
            LIMIT 1
        """).fetchone()
    return dict(row) if row else None


def upsert_usuario(**campos) -> int:
    """
    Crea o actualiza el único usuario.
    Claves esperadas (entrantes): nombre, profesion, github_url, foto, introduccion, descripcion.
    Se mapean a las columnas reales del schema.
    """
    # mapear nombres "amigables" a columnas reales
    mapping = {"nombre": "nombre_completo", "foto": "foto_perfil"}
    campos_sql = {mapping.get(k, k): v for k, v in campos.items()}

    actual = get_usuario()
    with connect() as con:
        if actual:
            # update
            sets = ", ".join([f"{k}=?" for k in campos_sql.keys()])
            vals = list(campos_sql.values()) + [actual["id_usuario"]]
            con.execute(f"UPDATE usuario SET {sets} WHERE id_usuario=?", vals)
            return actual["id_usuario"]
        else:
            # insert
            cols = ", ".join(campos_sql.keys())
            qs = ", ".join(["?"] * len(campos_sql))
            cur = con.execute(
                f"INSERT INTO usuario ({cols}) VALUES ({qs})",
                list(campos_sql.values()),
            )
            return cur.lastrowid


# -----------------------------
# Proyectos
# -----------------------------
def listar_proyectos() -> List[Dict]:
    with connect() as con:
        rows = con.execute(
            """
            SELECT 
                id_proyecto AS id,
                nombre AS titulo,
                descripcion,
                imagen,
                url_repositorio AS link
            FROM proyectos
            ORDER BY id_proyecto DESC
            """
        ).fetchall()
        return _to_dicts(rows)


def obtener_proyecto(pid: int) -> Optional[Dict]:
    with connect() as con:
        row = con.execute(
            """
            SELECT 
                id_proyecto AS id,
                nombre AS titulo,
                descripcion,
                imagen,
                url_repositorio AS link
            FROM proyectos
            WHERE id_proyecto=?
            """,
            (pid,),
        ).fetchone()
        return dict(row) if row else None


def crear_proyecto(titulo: str, descripcion: str = "", imagen: str = "", link: str = "", id_usuario: int | None = None) -> int:
    with connect() as con:
        cur = con.execute(
            """
            INSERT INTO proyectos (nombre, descripcion, imagen, url_repositorio, id_usuario)
            VALUES (?,?,?,?,?)
            """,
            (titulo, descripcion, imagen, link, id_usuario),
        )
        return cur.lastrowid


def actualizar_proyecto(pid: int, **campos) -> int:
    mapping = {"titulo": "nombre", "link": "url_repositorio"}
    campos_sql = {mapping.get(k, k): v for k, v in campos.items()}
    if not campos_sql:
        return 0
    with connect() as con:
        sets = ", ".join([f"{k}=?" for k in campos_sql.keys()])
        vals = list(campos_sql.values()) + [pid]
        cur = con.execute(
            f"UPDATE proyectos SET {sets} WHERE id_proyecto=?", vals)
        return cur.rowcount


def eliminar_proyecto(pid: int) -> int:
    with connect() as con:
        cur = con.execute("DELETE FROM proyectos WHERE id_proyecto=?", (pid,))
        return cur.rowcount


# -----------------------------
# Habilidades
# -----------------------------
def listar_habilidades() -> List[Dict]:
    with connect() as con:
        rows = con.execute(
            """
            SELECT
                id_habilidad AS id,
                nombre,
                nivel,
                descripcion,
                imagen
            FROM habilidades
            ORDER BY id_habilidad DESC, nombre ASC
            """
        ).fetchall()
        return _to_dicts(rows)


def crear_habilidad(nombre: str, nivel: str = "Básico", descripcion: str = "", imagen: str = "", id_usuario: int | None = None) -> int:
    with connect() as con:
        cur = con.execute(
            "INSERT INTO habilidades (nombre, nivel, descripcion, imagen, id_usuario) VALUES (?,?,?,?,?)",
            (nombre, nivel, descripcion, imagen, id_usuario),
        )
        return cur.lastrowid


def actualizar_habilidad(hid: int, **campos) -> int:
    with connect() as con:
        sets = ", ".join([f"{k}=?" for k in campos.keys()])
        vals = list(campos.values()) + [hid]
        cur = con.execute(
            f"UPDATE habilidades SET {sets} WHERE id_habilidad=?", vals)
        return cur.rowcount


def eliminar_habilidad(hid: int) -> int:
    with connect() as con:
        cur = con.execute(
            "DELETE FROM habilidades WHERE id_habilidad=?", (hid,))
        return cur.rowcount


# -----------------------------
# Datos de prueba (opcional)
# -----------------------------
# def seed_demo():
 #   """Carga datos de ejemplo si las tablas están vacías."""
  #  if not get_usuario():
   #     upsert_usuario(
    #        nombre="Juan Pérez",
     #       profesion="Desarrollador Kivy",
      #      github_url="https://github.com/demo",
       #     foto="../assets/img/luna.jpg",
        #    introduccion="Soy estudiante de ciberseguridad y desarrollo móvil.",
        #   descripcion="Este portafolio muestra mis proyectos y habilidades con Kivy/KivyMD.",
        # )

        # if not listar_proyectos():
        #   crear_proyecto(
        #      "Proyecto Demo",
        #     "Ejemplo de proyecto con persistencia SQLite.",
        #    "../assets/img/luna.jpg",
        #   "https://github.com/demo/proyecto",
        # )

        #  if not listar_habilidades():
        #     crear_habilidad(
        #        "Python", "Avanzado", "Desarrollo con Kivy y SQLite.", "../assets/img/python.jpg"
        # )
