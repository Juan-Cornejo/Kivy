📋 Plan de Implementación - Aplicación Portafolio Móvil (Kivy / KivyMD)

📅 Última actualización: 09/10/2025
✍️ Formato: Markdown (compatible con GitHub, Notion o cualquier visor .md)

🧩 Fase 1: Preparación

Tareas:

Crear estructura base de main.py
Responsable: Juan Cornejo
Duración: 2 horas
Estado: ✅ Completado
Entregable: Proyecto base ejecutable

Configurar entorno y dependencias (KivyMD)
Responsable: Juan Cornejo
Duración: 1 hora
Estado: ✅ Completado
Entregable: Entorno de desarrollo funcional

🗄️ Fase 2: Base de datos y persistencia

Tareas:

Crear base de datos SQLite y las tablas principales
Responsable: Sarita Marinao
Duración: 3 horas
Estado: 🔄 En progreso
Entregable: Archivo proyectos.db con estructura completa

Implementar funciones CRUD para todas las entidades
Responsable: Sarita Marinao
Duración: 4 horas
Estado: ⏳ Pendiente
Entregable: Operaciones CRUD funcionales

🔄 Mapeo: ERD → Tablas → Tareas de implementación

Tabla: usuario

Columnas: id_usuario, nombre_completo, profesion, github_url, foto_perfil, mensaje_bienvenida, introduccion, descripcion
Restricciones: id_usuario como PK
Relación: 1:N con proyectos y habilidades

Tareas:

Crear tabla en SQLite
Insertar datos de usuario por defecto
Función para leer/actualizar el perfil del usuario

Tabla: proyectos

Columnas: id_proyecto, id_usuario, nombre, descripcion, url_repositorio, imagen
Relación: FK id_usuario → usuario

Tareas:

Crear tabla con clave foránea
Implementar CRUD de proyectos
Mostrar en interfaz con scroll e imágenes

Tabla: habilidades

Columnas: id_habilidad, id_usuario, nombre, nivel, descripcion, imagen
Relación: FK id_usuario → usuario

Tareas:

Crear tabla con clave foránea
Implementar CRUD de habilidades
Mostrar en sección de habilidades en interfaz

🎨 Fase 3: Interfaz y navegación

Tareas:

Diseñar pantalla de inicio y menú de navegación
Responsable: Juan Cornejo
Duración: 4 horas
Estado: ✅ Completado
Entregable: Navegación inicial entre secciones

Conectar botones del menú con cada pantalla
Responsable: Juan Cornejo
Duración: 3 horas
Estado: ✅ Completado
Entregable: Enlaces funcionales a "Inicio", "Proyectos"…

🧠 Fase 4: Funcionalidades de contenido

Tareas:

Listar proyectos desde la base de datos
Responsable: Sarita Marinao
Duración: 5 horas
Estado: ⏳ Pendiente
Entregable: Visualización con scroll e imágenes

Crear / Editar proyectos (formulario)
Responsable: Sarita Marinao
Duración: 5 horas
Estado: ⏳ Pendiente
Entregable: Formulario con persistencia en SQLite

Mostrar lista de habilidades
Responsable: Ambos
Duración: 3 horas
Estado: ✅ Completado
Entregable: Sección de habilidades funcional

✅ Fase 5: Pruebas y documentación

Tareas:

Pruebas funcionales y corrección de errores
Responsable: Ambos
Duración: 4 horas
Estado: ⏳ Pendiente
Entregable: Aplicación estable

Redacción de documentación final del proyecto
Responsable: Ambos
Duración: 3 horas
Estado: ✅ Completado
Entregable: README, roles, plan de implementación

📌 Notas Finales

La conexión con SQLite y las funciones CRUD permitirán modificar contenido sin alterar el código fuente.
Se sigue el modelo 1:N desde usuario hacia proyectos y habilidades, asegurando integridad referencial con claves foráneas.
Cada integrante participó en distintas áreas, pero con enfoque colaborativo y revisión cruzada de tareas.
