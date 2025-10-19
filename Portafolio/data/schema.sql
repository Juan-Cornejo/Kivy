-- Crear la tabla "usuario"
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    clave TEXT NOT NULL,
    nombre_completo TEXT NOT NULL,
    profesion TEXT NOT NULL,
    github_url TEXT NOT NULL,
    foto_perfil TEXT NOT NULL,
    mensaje_bienvenida TEXT NOT NULL,
    introduccion TEXT NOT NULL,
    descripcion TEXT NOT NULL
);

-- Crear la tabla "proyectos"
CREATE TABLE IF NOT EXISTS proyectos (
    id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    url_repositorio TEXT NOT NULL,
    imagen TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario) ON DELETE CASCADE
);

-- Crear la tabla "habilidades"
CREATE TABLE IF NOT EXISTS habilidades (
    id_habilidad INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    nivel TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    imagen TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario) ON DELETE CASCADE
);