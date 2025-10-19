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
        return str(Path(App.get_running_app().user_data_dir) / "portafolio.db")
    else:
        # Usa .../Portafolio/data/portafolio.db
        return str(Path(__file__).parent.parent / "data" / "portafolio.db")


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
    """Inicializa la base. Si use_schema=True y existe data/schema.sql, lo ejecuta."""
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
def get_usuario() -> Optional[Dict]:
    """Devuelve el primer usuario registrado."""
    with connect() as con:
        row = con.execute("""
            SELECT 
                id_usuario, email, clave, nombre_completo, profesion,
                github_url, foto_perfil, mensaje_bienvenida,
                introduccion, descripcion
            FROM usuario
            ORDER BY id_usuario
            LIMIT 1
        """).fetchone()
    return dict(row) if row else None


def upsert_usuario(**campos) -> int:
    """
    Crea o actualiza el único usuario.
    Campos esperados:
        email, clave, nombre_completo, profesion, github_url,
        foto_perfil, mensaje_bienvenida, introduccion, descripcion
    """
    actual = get_usuario()
    with connect() as con:
        if actual:
            # update
            sets = ", ".join([f"{k}=?" for k in campos.keys()])
            vals = list(campos.values()) + [actual["id_usuario"]]
            con.execute(f"UPDATE usuario SET {sets} WHERE id_usuario=?", vals)
            return actual["id_usuario"]
        else:
            # insert
            cols = ", ".join(campos.keys())
            qs = ", ".join(["?"] * len(campos))
            cur = con.execute(
                f"INSERT INTO usuario ({cols}) VALUES ({qs})",
                list(campos.values())
            )
            return cur.lastrowid
# -----------------------------
# Proyectos
# -----------------------------
def listar_proyectos() -> List[Dict]:
    with connect() as con:
        rows = con.execute("""
            SELECT 
                id_proyecto AS id,
                nombre AS titulo,
                descripcion,
                imagen,
                url_repositorio AS link,
                id_usuario
            FROM proyectos
            ORDER BY id_proyecto DESC
        """).fetchall()
        return _to_dicts(rows)


def obtener_proyecto(pid: int) -> Optional[Dict]:
    with connect() as con:
        row = con.execute("""
            SELECT 
                id_proyecto AS id,
                nombre AS titulo,
                descripcion,
                imagen,
                url_repositorio AS link,
                id_usuario
            FROM proyectos
            WHERE id_proyecto=?
        """, (pid,)).fetchone()
        return dict(row) if row else None


def crear_proyecto(titulo: str, descripcion: str, imagen: str, link: str, id_usuario: int) -> int:
    with connect() as con:
        cur = con.execute("""
            INSERT INTO proyectos (id_usuario, nombre, descripcion, url_repositorio, imagen)
            VALUES (?,?,?,?,?)
        """, (id_usuario, titulo, descripcion, link, imagen))
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
        rows = con.execute("""
            SELECT
                id_habilidad AS id,
                nombre,
                nivel,
                descripcion,
                imagen,
                id_usuario
            FROM habilidades
            ORDER BY id_habilidad DESC, nombre ASC
        """).fetchall()
        return _to_dicts(rows)


def crear_habilidad(nombre: str, nivel: str, descripcion: str, imagen: str, id_usuario: int) -> int:
    with connect() as con:
        cur = con.execute("""
            INSERT INTO habilidades (id_usuario, nombre, nivel, descripcion, imagen)
            VALUES (?,?,?,?,?)
        """, (id_usuario, nombre, nivel, descripcion, imagen))
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
        cur = con.execute("DELETE FROM habilidades WHERE id_habilidad=?", (hid,))
        return cur.rowcount

def verificar_login(email: str, clave: str) -> Optional[Dict]:
    """Verifica si el usuario existe y la clave coincide."""
    with connect() as con:
        row = con.execute("""
            SELECT *
            FROM usuario
            WHERE email = ? AND clave = ?
        """, (email, clave)).fetchone()
        return dict(row) if row else None

def crear_usuario_defecto() -> int:
    """Crea un usuario por defecto si no existe ninguno."""
    if get_usuario():
        return get_usuario()["id_usuario"]

    return upsert_usuario(
        email="admin@gmail.com",
        clave="1234",
        nombre_completo="Admin Test",
        profesion="Programador",
        github_url="https://www.google.com",
        foto_perfil="../assets/img/perfil.jpg",
        mensaje_bienvenida="Bienvenido a mi portafolio",
        introduccion="Mi nombre es Admin Test",
        descripcion="Soy un programador con mucho camino por delante, me gusta Kivy y el desarrollo móvil."
    )