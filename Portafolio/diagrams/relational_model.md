# Modelo Relacional

Este archivo describe el modelo relacional para la base de datos del proyecto. Incluye las tablas, sus columnas, tipos de datos, claves primarias (PK), claves foráneas (FK), restricciones y cardinalidades.

## Tablas

### **1. Tabla: `usuario`**

| Columna           | Tipo de dato | Restricciones              | Comentarios                              |
| ----------------- | ------------ | -------------------------- | ---------------------------------------- |
| `id_usuario`      | INTEGER      | PRIMARY KEY, AUTOINCREMENT | Identificador único del usuario.         |
| `nombre_completo` | TEXT         | NOT NULL                   | Nombre completo del usuario.             |
| `profesion`       | TEXT         | NOT NULL                   | Profesión del usuario.                   |
| `github_url`      | TEXT         | NOT NULL                   | URL de GitHub del usuario.               |
| `foto_perfil`     | TEXT         | NOT NULL                   | Ruta de la imagen de perfil del usuario. |
| `introduccion`    | TEXT         | NOT NULL                   | Introducción breve sobre el usuario.     |
| `descripcion`     | TEXT         | NOT NULL                   | Descripción detallada sobre el usuario.  |

**Cardinalidad**: Un usuario puede tener solo un conjunto de datos, por lo que la relación con las tablas `proyectos` y `habilidades` es **1:1**.

---

### **2. Tabla: `proyectos`**

| Columna           | Tipo de dato | Restricciones              | Comentarios                                       |
| ----------------- | ------------ | -------------------------- | ------------------------------------------------- |
| `id_proyecto`     | INTEGER      | PRIMARY KEY, AUTOINCREMENT | Identificador único del proyecto.                 |
| `id_usuario`      | INTEGER      | FOREIGN KEY                | Referencia al `id_usuario` de la tabla `usuario`. |
| `nombre`          | TEXT         | NOT NULL                   | Nombre del proyecto.                              |
| `descripcion`     | TEXT         | NOT NULL                   | Descripción del proyecto.                         |
| `url_repositorio` | TEXT         | NOT NULL                   | URL del repositorio del proyecto.                 |
| `imagen`          | TEXT         | NOT NULL                   | Ruta de la imagen asociada al proyecto.           |

**Cardinalidad**: Un usuario puede tener varios proyectos, por lo que la relación con la tabla `usuario` es **1:N** (uno a muchos).

---

### **3. Tabla: `habilidades`**

| Columna        | Tipo de dato | Restricciones              | Comentarios                                         |
| -------------- | ------------ | -------------------------- | --------------------------------------------------- |
| `id_habilidad` | INTEGER      | PRIMARY KEY, AUTOINCREMENT | Identificador único de la habilidad.                |
| `id_usuario`   | INTEGER      | FOREIGN KEY                | Referencia al `id_usuario` de la tabla `usuario`.   |
| `nombre`       | TEXT         | NOT NULL                   | Nombre de la habilidad (por ejemplo, "JavaScript"). |
| `nivel`        | TEXT         | NOT NULL                   | Nivel de la habilidad (por ejemplo, "Avanzado").    |
| `descripcion`  | TEXT         | NOT NULL                   | Descripción detallada sobre la habilidad.           |
| `imagen`       | TEXT         | NOT NULL                   | Ruta de la imagen asociada a la habilidad.          |

**Cardinalidad**: Un usuario puede tener varias habilidades, por lo que la relación con la tabla `usuario` es **1:N** (uno a muchos).

---

## Relación entre las tablas

1. **Usuario - Proyectos**: La relación es de **1:N**. Un usuario puede tener múltiples proyectos registrados en la tabla `proyectos`.

2. **Usuario - Habilidades**: La relación es de **1:N**. Un usuario puede tener múltiples habilidades en la tabla `habilidades`.

---

## Decisiones de diseño

- Se utilizó `TEXT` para almacenar cadenas de texto, como nombres, descripciones y URLs, ya que se espera que sean datos de longitud variable.
- Las claves foráneas (`id_usuario`) aseguran la integridad referencial entre las tablas. Esto significa que no pueden existir registros en las tablas `proyectos` y `habilidades` sin un usuario válido en la tabla `usuario`.
- Los identificadores de las tablas están definidos como `INTEGER PRIMARY KEY AUTOINCREMENT`, lo que significa que serán generados automáticamente por SQLite.
