## 🧠 Descripción General

Esta es una aplicación móvil desarrollada con **Python**, utilizando los frameworks **Kivy** y **KivyMD**, cuyo propósito es servir como un **portafolio personal interactivo**.

El usuario puede visualizar información personal, proyectos realizados, habilidades, imágenes y enlaces externos, todo con navegación fluida y diseño responsivo.

La aplicación implementa **persistencia de datos con SQLite3**, permitiendo almacenar y cargar información sin necesidad de modificar el código fuente.

---

## ✨ Características Principales

- 🚪 **Inicio de sesión** ingresando correo y contraseña. (correo: admin@gmail.com, clave: 1234)
- 🏠 **Pantalla de inicio** con información personal y presentación del usuario.
- 📋 **Menú hamburguesa (Drawer Navigation)** para moverse entre secciones:
  - Inicio
  - Sobre mí
  - Proyectos
  - Habilidades
  - Cerrar sesión
- 💡 **Visualización dinámica de proyectos** con imágenes, descripciones y enlaces a repositorios (por ejemplo, GitHub).
- 🧭 **Scroll** vertical para explorar múltiples proyectos o habilidades.
- 🎨 **Diseño responsivo y minimalista** gracias a los componentes de KivyMD.
- 💾 **Persistencia de datos mediante SQLite3** para mantener los registros de proyectos y habilidades de forma permanente.
- ⚙️ **Edición** mediante un boton de tuerca que activa los lapices para editar los campos de la pantalla principal y sobre mí.

---

## 🛠️ Herramientas Necesarias

Antes de comenzar con la instalación, asegúrate de tener las siguientes **herramientas instaladas** en tu equipo:

- **Python**
- **Git**
- **Visual Studio Code**

---

## 🔨 Instalación del Proyecto

Para instalar y ejecutar el proyecto, sigue los pasos indicados a continuación:

1. **Clonar el repositorio** utilizando Visual Studio Code
2. En la terminal, **ejecuta los siguientes comandos** para preparar el entorno virtual e instalar las dependencias necesarias:

   1. **python -m pip install --upgrade pip setuptools virtualenv**
   2. **python -m venv kivy_venv** (crea el entorno virtual)
   3. Terminal Bash: **source kivy_venv/Scripts/activate** (activa el entorno virtual)

3. Una vez instalado el entorno y las dependencias ahora tienes que instalar kivy con el siguiente comando: **python -m pip install "kivy[full]"**
4. Despues de que kivy ya este instalado navega a la carpeta del proyecto desde la terminal con el comando **cd Portafolio**
5. Finalmente, ejecuta el proyecto con el comando **python -m app.main**

---

## 📱 Flujo de Uso

1. El usuario accede al login. (correo: admin@gmail.com, clave: 1234)
2. Si las credenciales son correctas, se muestra la pantalla principal.
3. Desde el menú lateral puede acceder a:

- Inicio
- Sobre mí
- Proyectos
- Habilidades

4. Los proyectos y habilidades se cargan dinámicamente desde la base de datos.
5. El usuario puede cerrar sesión desde el drawer.

---

# 👥 Roles del Equipo

## 🧩 Distribución de Roles

| Rol                                   | Integrante(s) | Responsabilidades                                                                                                          |
| ------------------------------------- | ------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Líder / Coordinador**               | Ambos         | Planificación del proyecto, organización de tareas, coordinación general y control de avances.                             |
| **Analista de datos / Modelador ER**  | Juan Cornejo  | Diseño del modelo entidad–relación, definición de la estructura de la base de datos SQLite3 y validación de relaciones.    |
| **Implementador Kivy / Persistencia** | Ambos         | Desarrollo de la interfaz con Kivy/KivyMD, implementación de la lógica de negocio y conexión con la base de datos SQLite3. |
| **Redactor de documentación / QA**    | Ambos         | Creación del README y documentación técnica, revisión del código, pruebas de funcionamiento y control de calidad.          |
| **Presentadores**                     | Ambos         | Exposición del proyecto, explicación del diseño, desarrollo y resultados obtenidos.                                        |

---

## 🧠 Notas Generales

- Ambos integrantes participaron activamente en todas las etapas del desarrollo: análisis, diseño, codificación, pruebas y documentación.
- El trabajo fue distribuido equitativamente, fomentando la colaboración, la revisión mutua del código y la toma conjunta de decisiones.
- Cada integrante asumió múltiples funciones para garantizar la finalización del proyecto dentro de los plazos establecidos.

---
