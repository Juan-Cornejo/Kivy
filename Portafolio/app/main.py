from kivy.core.window import Window
from plyer import filechooser
from kivy.uix.scrollview import ScrollView
from kivy.factory import Factory
from pathlib import Path
from kivy.lang import Builder
from os.path import expanduser
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.fitimage import FitImage
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.utils import get_color_from_hex, platform
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.textfield import MDTextField
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.app import App
from kivy.lang import Builder
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.label import MDIcon
from kivy.graphics import Color, Ellipse
from kivymd.uix.button import MDFloatingActionButton
from app import gestor  # gestor.py maneja SQLite (conexión y CRUD)

# "python -m app.main" en consola para ejecutar proyecto

# Desktop testing window size
if platform in ("win", "linux", "macosx"):
    Window.size = (360, 640)


class FlatCircularFAB(MDFloatingActionButton):
    """Botón circular plano, sin elevación ni ripple."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (225/255, 225/255, 225/255, 1)  # gris claro
        self.icon_color = (0, 0, 0, 1)
        self.size_hint = (None, None)
        self.size = (dp(70), dp(70))

        # Eliminar cualquier animación de elevación
        self._anim_raised = False
        self.elevation = 0  # sin sombra

        # Desactivar el efecto ripple / cambio de color al presionar
        self._no_ripple_effect = True


class NoRippleListItem(OneLineIconListItem):
    icon = StringProperty()
    ripple_behavior = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_behavior = False

    def on_kv_post(self, base_widget):
        if not hasattr(self, '_icon_added'):
            self.ids._left_container.clear_widgets()
            self.ids._left_container.add_widget(IconLeftWidget(icon=self.icon))
            self._icon_added = True

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dispatch('on_release')
            return True
        return super().on_touch_down(touch)


class SilentIconButton(ButtonBehavior, MDIcon):
    """ Icono que actúa como botón, sin ripple, sin fondo ni círculo gris. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0, 0, 0, 1)  # color del icono
        self.disabled = kwargs.get("disabled", False)
        self.opacity = kwargs.get("opacity", 1)

    def on_touch_down(self, touch):
        if self.disabled or self.opacity == 0:
            return False
        if self.collide_point(*touch.pos):
            self.dispatch("on_release")
            return True
        return super().on_touch_down(touch)


class SilentFlatButton(MDFlatButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_effect = False  # desactiva efecto ripple
        self.md_bg_color = (0.8, 0.8, 0.8, 1)  # gris medio
        self.text_color = (0, 0, 0, 1)  # texto negro para contraste
        self.elevation = 0  # sin sombra
        self.theme_bg_color = "Custom"

    def on_touch_down(self, touch):
        # Si el botón está deshabilitado o invisible, ignorar el toque
        if self.disabled or getattr(self, "opacity", 1) == 0:
            return super().on_touch_down(touch)

        if self.collide_point(*touch.pos):
            self.dispatch("on_release")
            return True
        return super().on_touch_down(touch)


class SilentRaisedButton(MDRaisedButton):
    """Botón MDRaisedButton gris claro sin efecto ripple al presionar."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Forzar uso de color custom
        self.theme_bg_color = "Custom"
        # Gris claro RGBA
        self.md_bg_color = (225/255, 225/255, 225/255, 1)
        # Texto negro
        self.text_color = (0, 0, 0, 1)
        # Sin sombra
        self.elevation = 0
        # Desactivar efecto ripple
        self.ripple_behavior = False

        self.padding = [dp(20), dp(10)]

    def on_touch_down(self, touch):
        # Si el botón está deshabilitado o invisible, ignorar el toque
        if self.disabled or getattr(self, "opacity", 1) == 0:
            return super().on_touch_down(touch)

        if self.collide_point(*touch.pos):
            self.dispatch("on_release")
            return True
        return super().on_touch_down(touch)


class SilentDialogButton(MDFlatButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_effect = False   # quita efecto blanco
        self.md_bg_color = (225/255, 225/255, 225/255, 1)  # gris suave
        self.text_color = (0, 0, 0, 1)
        self.theme_bg_color = "Custom"
        self.elevation = 0

# si usas AnimatedButton en otro lado, mantenla (aquí por completitud)


class AnimatedButton(MDFlatButton):
    scale = NumericProperty(1)


class LoginScreen(Screen):
    dialog = None  # guardamos la instancia para no crear varias

    def login(self):
        email = self.ids.email_input.text.strip()
        clave = self.ids.clave_input.text.strip()

        if not email or not clave:
            self.show_error_dialog("Por favor ingrese correo y contraseña.")
            return

        usuario = gestor.verificar_login(
            email, clave)  # tu función de verificación
        if usuario:
            MDApp.get_running_app().usuario_actual = usuario
            self.ids.email_input.text = ""
            self.ids.clave_input.text = ""
            self.manager.current = "home"
            try:
                home_screen = self.manager.get_screen("home")
                home_screen.mostrar_mensaje_inicio_sesion()
            except Exception as e:
                print("No se pudo mostrar el mensaje de inicio de sesión:", e)
        else:
            self.show_error_dialog("Correo o contraseña incorrectos.")

    def show_error_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Error de inicio de sesión",
                text=message,
                size_hint=(0.85, None),
                buttons=[
                    SilentDialogButton(
                        text="OK",
                        on_release=lambda btn: self._dismiss_dialog()
                    )
                ],
            )
        else:
            self.dialog.text = message
        self.dialog.open()

    def _dismiss_dialog(self):
        if self.dialog:
            self.dialog.dismiss()

    def mostrar_mensaje_cierre_sesion(self, mensaje="Cierre de sesión exitoso, ¡Hasta luego!"):
        """Muestra un banner de cierre de sesión idéntico al de inicio de sesión."""
        try:
            msg_card = self.ids.logout_message
            msg_label = self.ids.logout_message_label
        except Exception as e:
            print("IDs del mensaje de logout no encontrados:", e)
            return

        # Actualizar texto
        msg_label.text = mensaje

        # Cancelar animaciones previas
        Animation.cancel_all(msg_card)

        # Hacer visible y deslizar hacia abajo
        msg_card.opacity = 1
        anim_entrada = Animation(
            pos_hint={"center_x": 0.5, "top": 0.95}, d=0.38, t="out_back")
        anim_entrada.start(msg_card)

        # Programar ocultado después de 5 segundos
        Clock.schedule_once(
            lambda dt: self.ocultar_mensaje_cierre_sesion(), 5.0)

    def ocultar_mensaje_cierre_sesion(self):
        """Oculta el banner de cierre de sesión con animación idéntica al inicio de sesión."""
        try:
            msg_card = self.ids.logout_message
        except Exception as e:
            print("IDs del mensaje de logout no encontrados (ocultar):", e)
            return

        Animation.cancel_all(msg_card)
        anim_salida = Animation(
            pos_hint={"center_x": 0.5, "top": 1.12}, opacity=0, d=0.32, t="in_back")
        anim_salida.start(msg_card)


class FondoWidget(Screen):
    # props enlazadas al .kv
    nombre_text = StringProperty("")
    profesion_text = StringProperty("")
    intro_text = StringProperty("")
    github_url = StringProperty("")
    foto_source = StringProperty("../assets/img/perfil.jpg")

    edit_mode = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("✅ FondoWidget inicializado:", self, "desde", __file__)

    def mostrar_mensaje_campo_actualizado(self, mensaje="Campo actualizado."):
        """Muestra un banner superior idéntico al de cierre de sesión."""
        try:
            msg_card = self.ids.campo_message
            msg_label = self.ids.campo_message_label
        except Exception as e:
            print("IDs del mensaje de campo no encontrados:", e)
            return

        # Actualizar texto
        msg_label.text = mensaje

        # Cancelar animaciones previas
        Animation.cancel_all(msg_card)

        # Hacer visible y deslizar hacia abajo
        msg_card.opacity = 1
        anim_entrada = Animation(
            pos_hint={"center_x": 0.5, "top": 0.95}, d=0.38, t="out_back")
        anim_entrada.start(msg_card)

        # Programar ocultado después de 5 segundos
        Clock.schedule_once(
            lambda dt: self.ocultar_mensaje_campo_actualizado(), 3.0)

    def ocultar_mensaje_campo_actualizado(self):
        """Oculta el banner con animación."""
        try:
            msg_card = self.ids.campo_message
        except Exception as e:
            print("IDs del mensaje de campo no encontrados (ocultar):", e)
            return

        Animation.cancel_all(msg_card)
        anim_salida = Animation(
            pos_hint={"center_x": 0.5, "top": 1.12}, opacity=0, d=0.32, t="in_back")
        anim_salida.start(msg_card)

    # Llamar a esta función desde el MDTextField al presionar Enter
    def campo_editado(self):
        self.mostrar_mensaje_campo_actualizado()

    def mostrar_mensaje_inicio_sesion(self, mensaje="Inicio de sesión exitoso, ¡Bienvenido!"):
        """Muestra un banner superior con animación, lo mantiene 5s y luego lo oculta."""
        try:
            msg_card = self.ids.login_message
            msg_label = self.ids.login_message_label
        except Exception as e:
            print("IDs del mensaje no encontrados:", e)
            return

        # Actualizar texto
        msg_label.text = mensaje

        # Cancelar animaciones previas
        Animation.cancel_all(msg_card)

        # Hacer visible y deslizar hacia abajo
        msg_card.opacity = 1
        # animamos la posición: bajamos a top 0.95 en 0.38s con curva 'out_back'
        anim_entrada = Animation(
            pos_hint={"center_x": 0.5, "top": 0.95}, d=0.38, t="out_back")
        anim_entrada.start(msg_card)

        # Programar ocultado después de 5s
        Clock.schedule_once(
            lambda dt: self.ocultar_mensaje_inicio_sesion(), 5.0)

    def ocultar_mensaje_inicio_sesion(self):
        """Oculta el banner con animación."""
        try:
            msg_card = self.ids.login_message
        except Exception as e:
            print("IDs del mensaje no encontrados (ocultar):", e)
            return

        Animation.cancel_all(msg_card)
        anim_salida = Animation(
            pos_hint={"center_x": 0.5, "top": 1.12}, opacity=0, d=0.32, t="in_back")
        anim_salida.start(msg_card)

    def on_kv_post(self, instance):
        # Deshabilita los botones de edición al cargar la pantalla
        for edit_btn in [
            self.ids.edit_foto,
            self.ids.edit_nombre,
            self.ids.edit_profesion,
            self.ids.edit_github,
            self.ids.edit_intro,
        ]:
            edit_btn.disabled = True

    def show_name_edit_field(self):
        field = self.ids.edit_name_field
        label = self.ids.lbl_nombre

        Animation.cancel_all(field, label)
        if field.opacity == 0:  # Mostrar
            field.text = self.nombre_text
            field.disabled = False
            Animation(opacity=1, d=0.18).start(field)
            Animation(opacity=0, d=0.18).start(label)
        else:  # Ocultar
            Animation(opacity=0, d=0.18).start(field)
            Animation(opacity=1, d=0.18).start(label)
            Clock.schedule_once(lambda dt: setattr(
                field, "disabled", True), 0.18)

    def show_profession_edit_field(self):
        field = self.ids.edit_profession_field
        label = self.ids.lbl_profesion

        Animation.cancel_all(field, label)
        if field.opacity == 0:  # Mostrar
            field.text = self.profesion_text
            field.disabled = False
            Animation(opacity=1, d=0.18).start(field)
            Animation(opacity=0, d=0.18).start(label)
        else:  # Ocultar
            Animation(opacity=0, d=0.18).start(field)
            Animation(opacity=1, d=0.18).start(label)
            Clock.schedule_once(lambda dt: setattr(
                field, "disabled", True), 0.18)

    def show_github_edit_field(self):
        field = self.ids.edit_github_field
        Animation.cancel_all(field)

        if field.opacity == 0:
            field.text = self.github_url
            field.disabled = False
            Animation(opacity=1, d=0.18).start(field)
        else:
            Animation(opacity=0, d=0.18).start(field)
            Clock.schedule_once(lambda dt: setattr(
                field, "disabled", True), 0.18)

    def show_intro_edit_field(self):
        field = self.ids.edit_intro_field
        Animation.cancel_all(field)

        if field.opacity == 0:
            field.text = self.intro_text
            field.disabled = False
            Animation(opacity=1, d=0.18).start(field)
        else:
            Animation(opacity=0, d=0.18).start(field)
            Clock.schedule_once(lambda dt: setattr(
                field, "disabled", True), 0.18)

    def update_name_from_input(self):
        """Actualiza el nombre cuando presionamos 'Enter' y lo guarda en la base de datos."""
        new_name = self.ids.edit_name_field.text
        print("Nuevo nombre:", new_name)

        if new_name:  # Si hay texto
            # Actualizamos el nombre en la UI
            self.nombre_text = new_name
            self.ids.lbl_nombre.text = new_name  # Actualizamos el label con el nuevo nombre
            self.ids.lbl_nombre.height = self.ids.lbl_nombre.texture_size[1] + dp(
                10)

            # Guardamos el nuevo nombre en la base de datos
            self.update_user_name(new_name)

            # Ocultamos el campo de texto y mostramos el label nuevamente
            self.ids.edit_name_field.opacity = 0
            self.ids.lbl_nombre.opacity = 1

    def update_profession_from_input(self):
        """Actualiza la profesión cuando presionamos 'Enter' y lo guarda en la base de datos."""
        new_profession = self.ids.edit_profession_field.text
        print("Nueva profesión:", new_profession)

        if new_profession:  # Si hay texto
            # Actualizamos la profesión en la UI
            self.profesion_text = new_profession
            # Actualizamos el label con la nueva profesión
            self.ids.lbl_profesion.text = new_profession
            self.ids.lbl_profesion.height = self.ids.lbl_profesion.texture_size[1] + dp(
                10)

            # Guardamos la nueva profesión en la base de datos
            self.update_user_profession(new_profession)

            # Ocultamos el campo de texto y mostramos el label nuevamente
            self.ids.edit_profession_field.opacity = 0
            self.ids.lbl_profesion.opacity = 1

    def update_github_from_input(self):
        """Actualiza la URL de GitHub al presionar Enter"""
        new_url = self.ids.edit_github_field.text.strip()
        if new_url:
            self.github_url = new_url
            print("Nueva URL de GitHub:", new_url)
        try:
            gestor.upsert_usuario(github_url=new_url)  # guardamos en DB
        except Exception as e:
            print("Error al actualizar GitHub en la base de datos:", e)

        # Ocultar el campo
        self.ids.edit_github_field.opacity = 0
        self.ids.edit_github_field.focus = False

    def update_intro_from_input(self):
        """Actualiza el mensaje de bienvenida al presionar Enter"""
        new_intro = self.ids.edit_intro_field.text.strip()
        if new_intro:
            self.intro_text = new_intro
            self.ids.lbl_intro.text = new_intro
            self.ids.lbl_intro.height = self.ids.lbl_intro.texture_size[1] + dp(
                10)
        try:
            gestor.upsert_usuario(mensaje_bienvenida=new_intro)
            print("Mensaje de bienvenida actualizado:", new_intro)
        except Exception as e:
            print("Error al actualizar mensaje de bienvenida:", e)

    # Ocultar el campo después de presionar Enter
        self.ids.edit_intro_field.opacity = 0
        self.ids.edit_intro_field.focus = False

    def update_user_name(self, new_name):
        """Actualiza el nombre del usuario en la base de datos"""
        try:
            # Suponiendo que tienes un método para actualizar el nombre en la base de datos
            gestor.upsert_usuario(nombre_completo=new_name)
            print("Nombre actualizado en la base de datos")
        except Exception as e:
            print("Error al actualizar el nombre en la base de datos:", e)

    def update_user_profession(self, new_profession):
        """Actualiza la profesión del usuario en la base de datos"""
        try:
            gestor.upsert_usuario(profesion=new_profession)
            print("Profesión actualizada en la base de datos")
        except Exception as e:
            print("Error al actualizar la profesión en la base de datos:", e)

    def on_pre_enter(self, *args):
        print("✅ on_pre_enter de FondoWidget")
        # Llama en el siguiente frame (evita choques de carga con el kv)
        Clock.schedule_once(lambda *_: self.cargar_usuario(), 0)

    def cargar_usuario(self, *args):
        print("✅ cargar_usuario existe y fue llamada")
        try:
            data = gestor.get_usuario()  # debe devolver dict con las claves de BD
            print("DBG usuario:", data)
        except Exception as e:
            print("❌ Error cargando usuario:", e)
            data = None

        if not data:
            self.nombre_text = "Nombre Apellido"
            self.profesion_text = "Desarrollador | Programador"
            self.intro_text = "Bienvenido a mi portafolio"
            self.github_url = ""
            self.foto_source = "../assets/img/perfil.jpg"
            return

        # 🔧 Ajustado a schema.sql
        self.nombre_text = data.get("nombre_completo") or "Nombre Apellido"
        self.profesion_text = data.get(
            "profesion") or "Desarrollador | Programador"
        self.intro_text = data.get(
            "mensaje_bienvenida") or "Bienvenido a mi portafolio"
        self.github_url = data.get("github_url") or ""
        self.foto_source = data.get(
            "foto_perfil") or "../assets/img/perfil.jpg"

    def abrir_github(self):
        import webbrowser
        if self.github_url:
            webbrowser.open(self.github_url)

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        # Verifica si el estado cambia
        print("Modo de edición activado:", self.edit_mode)
        for edit_btn in [
            self.ids.edit_foto,
            self.ids.edit_nombre,
            self.ids.edit_profesion,
            self.ids.edit_github,
            self.ids.edit_intro,
        ]:
            Animation.cancel_all(edit_btn)
            if self.edit_mode:
                edit_btn.disabled = False
                edit_btn.opacity = 0  # Asegura que empiece invisible
                Animation(opacity=1, d=0.3).start(edit_btn)
            else:
                edit_btn.disabled = True
                edit_btn.state = "normal"
                edit_btn.focus = False
                edit_btn.md_bg_color = (0, 0, 0, 0)
                Animation(opacity=0, d=0.3).start(edit_btn)
                # desactivar un pelín después de la animación
                Clock.schedule_once(
                    lambda dt, btn=edit_btn: setattr(
                        btn, "disabled", True), 0.3
                )
        if not self.edit_mode:
            for field_name in [
                "edit_name_field",
                "edit_profession_field",
                "edit_github_field",
                "edit_intro_field",
            ]:
                if field_name in self.ids:
                    field = self.ids[field_name]
                    if field.opacity == 1:
                        Animation.cancel_all(field)
                        Animation(opacity=0, d=0.2).start(field)
                        field.focus = False
        # -------------------------------
    # Funcionalidad para cambiar foto de perfil
    # -------------------------------

    def open_filechooser(self):
        """Abre un popup con FileChooser y botones Cancelar / Seleccionar."""
        print("🟢 open_filechooser llamado")

        # FileChooser
        self.filechooser = FileChooserIconView()
        self.filechooser.filters = ['*.png', '*.jpg', '*.jpeg']

        # Path inicial: carpeta assets/img del proyecto
        base_dir = Path(__file__).parent.parent   # .../Portafolio/
        img_dir = base_dir / "assets" / "img"
        self.filechooser.path = str(img_dir)
        print("📁 FileChooser path inicial:", self.filechooser.path)

        # Layout del popup: FileChooser arriba, botones abajo
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button

        content = BoxLayout(orientation="vertical", spacing=5)
        content.add_widget(self.filechooser)

        botones = BoxLayout(size_hint_y=None, height=dp(48),
                            spacing=5, padding=[5, 5, 5, 5])

        btn_cancelar = Button(text="Cancelar")
        btn_cancelar.bind(on_release=lambda *args: self._cerrar_popup())

        btn_seleccionar = Button(text="Seleccionar")
        btn_seleccionar.bind(on_release=self.confirm_image_selection)

        botones.add_widget(btn_cancelar)
        botones.add_widget(btn_seleccionar)

        content.add_widget(botones)

        # Creamos y abrimos el popup
        self.popup = Popup(
            title="Selecciona una imagen",
            content=content,
            size_hint=(0.9, 0.9)
        )
        self.popup.open()

    def _cerrar_popup(self, *args):
        if hasattr(self, "popup") and self.popup:
            self.popup.dismiss()

    def confirm_image_selection(self, *args):
        """Lee la selección actual del FileChooser al pulsar 'Seleccionar'."""
        if not hasattr(self, "filechooser"):
            print("⚠️ No hay filechooser activo")
            self._cerrar_popup()
            return

        selection = self.filechooser.selection
        print("🟡 confirm_image_selection, selection:", selection)

        if selection:
            image_path = selection[0]
            print("✅ Imagen elegida:", image_path)
            self.update_profile_image(image_path)
        else:
            print("❌ No se seleccionó ningún archivo")

        self._cerrar_popup()

    def update_profile_image(self, image_path):
        """Actualiza la imagen de perfil en la interfaz y en la base de datos."""
        print("🔄 update_profile_image con ruta:", image_path)

        # Actualiza la propiedad que usa el KV
        self.foto_source = image_path
        print("🎨 foto_source ahora es:", self.foto_source)

        # Por si acaso, también actualizamos directo el Image
        if "foto_perfil" in self.ids:
            self.ids.foto_perfil.source = image_path

        # Guardar en BD
        self.update_user_profile_image(image_path)

    def update_user_profile_image(self, new_image_path):
        """Actualiza la ruta de la imagen de perfil en la base de datos."""
        print("💾 Guardando nueva imagen en BD:", new_image_path)
        try:
            gestor.upsert_usuario(foto_perfil=new_image_path)
            print("✅ Ruta de la imagen actualizada en la base de datos")
        except Exception as e:
            print("⚠️ Error al actualizar la imagen en la base de datos:", e)

    def load_profile_image(self):
        """Carga la imagen de perfil desde la base de datos (si la quieres usar)."""
        data = gestor.get_usuario()
        if data and data.get('foto_perfil'):
            path = data['foto_perfil']
            print("📥 Cargando imagen de perfil desde BD:", path)
            self.foto_source = path
            if "foto_perfil" in self.ids:
                self.ids.foto_perfil.source = path
        else:
            default = "../assets/img/perfil.jpg"
            print("📥 Usando imagen de perfil por defecto:", default)
            self.foto_source = default
            if "foto_perfil" in self.ids:
                self.ids.foto_perfil.source = default

    # -------------------------------
    # Funcionalidad para cambiar foto de perfil
    # -------------------------------


class SobreMiScreen(MDScreen):
    introduccion_text = StringProperty("")
    descripcion_text = StringProperty("")
    edit_mode = BooleanProperty(False)
    campos_visibles = BooleanProperty(False)

    def on_pre_enter(self, *args):
        """Carga datos desde la BD al entrar (si aún no están)."""
        try:
            usuario = gestor.get_usuario()
            if usuario:
                self.introduccion_text = usuario.get("introduccion", "") or ""
                self.descripcion_text = usuario.get("descripcion", "") or ""
        except Exception as e:
            print("Error cargando usuario en SobreMiScreen:", e)

    def mostrar_mensaje_campo_actualizado(self, mensaje="Campo actualizado."):
        """Muestra un banner superior en SobreMiScreen al editar un campo."""
        try:
            msg_card = self.ids.field_update_message
            msg_label = self.ids.field_update_message_label
        except Exception as e:
            print("IDs del mensaje no encontrados:", e)
            return

        msg_label.text = mensaje

        # Cancelar animaciones previas
        Animation.cancel_all(msg_card)

        # Mostrar y animar hacia abajo
        msg_card.opacity = 1
        anim_entrada = Animation(
            pos_hint={"center_x": 0.5, "top": 0.95}, d=0.38, t="out_back")
        anim_entrada.start(msg_card)

        # Ocultar después de 5s
        Clock.schedule_once(
            lambda dt: self.ocultar_mensaje_campo_actualizado(), 3.0)

    def ocultar_mensaje_campo_actualizado(self):
        """Oculta el banner con animación."""
        try:
            msg_card = self.ids.field_update_message
        except Exception as e:
            print("IDs del mensaje no encontrados (ocultar):", e)
            return

        Animation.cancel_all(msg_card)
        anim_salida = Animation(
            pos_hint={"center_x": 0.5, "top": 1.12}, opacity=0, d=0.32, t="in_back")
        anim_salida.start(msg_card)

    def toggle_edit_mode(self):
        """Mantiene tu lógica original para mostrar/ocultar el botón lápiz."""
        self.edit_mode = not self.edit_mode
        edit_btn = self.ids.edit_texto

        Animation.cancel_all(edit_btn)

        if self.edit_mode:
            edit_btn.disabled = False
            Animation(opacity=1, d=0.25).start(edit_btn)
        else:
            edit_btn.state = "normal"
            edit_btn.focus = False
            edit_btn.md_bg_color = (0, 0, 0, 0)
            Animation(opacity=0, d=0.25).start(edit_btn)
            Clock.schedule_once(lambda dt: setattr(
                edit_btn, "disabled", True), 0.25)
            # Si se sale del modo edición ocultamos campos sin guardar
            if self.campos_visibles:
                self.ocultar_campos_edicion(save=False)

    def editar_texto_sobremi(self):
        """Toggle: si los campos están ocultos los mostramos; si están visibles, los ocultamos sin guardar."""
        if not self.campos_visibles:
            self.mostrar_campos_edicion()
        else:
            # Al presionar lápiz otra vez -> ocultar SIN guardar (comportamiento solicitado)
            self.ocultar_campos_edicion(save=False)

    def mostrar_campos_edicion(self):
        """Muestra los MDTextField (copia texto actual y pone foco)."""
        try:
            intro_field = self.ids.edit_introduccion_field
            desc_field = self.ids.edit_descripcion_field
            lbl_intro = self.ids.lbl_introduccion
            lbl_desc = self.ids.lbl_descripcion
        except Exception as e:
            print("IDs faltantes en kv para mostrar_campos_edicion:", e)
            return

        # Rellenar campos con texto actual
        intro_field.text = lbl_intro.text or ""
        desc_field.text = lbl_desc.text or ""

        Animation.cancel_all(intro_field)
        Animation.cancel_all(desc_field)
        Animation(opacity=1, d=0.18).start(intro_field)
        Animation(opacity=1, d=0.18).start(desc_field)

        lbl_intro.opacity = 0
        lbl_desc.opacity = 0

        self.campos_visibles = True

    def ocultar_campos_edicion(self, save: bool = True):
        """
        Oculta los MDTextField.
        Si save=True guarda en BD via gestor.upsert_usuario(introduccion=..., descripcion=...).
        Si save=False restaura labels con los textos previos (no guarda).
        """
        try:
            intro_field = self.ids.edit_introduccion_field
            desc_field = self.ids.edit_descripcion_field
            lbl_intro = self.ids.lbl_introduccion
            lbl_desc = self.ids.lbl_descripcion
        except Exception as e:
            print("IDs faltantes en kv para ocultar_campos_edicion:", e)
            return

        # Si no guardamos, restauramos labels al valor en las propiedades
        if not save:
            lbl_intro.text = self.introduccion_text or lbl_intro.text
            lbl_desc.text = self.descripcion_text or lbl_desc.text
        else:
            # Guardar en BD solo si el texto cambió
            nuevo_intro = intro_field.text.strip()
            nueva_desc = desc_field.text.strip()

            # Actualizar labels en UI
            lbl_intro.text = nuevo_intro
            lbl_desc.text = nueva_desc

            # Persistencia
            try:
                gestor.upsert_usuario(
                    introduccion=nuevo_intro, descripcion=nueva_desc)
                # Actualizar las props locales
                self.introduccion_text = nuevo_intro
                self.descripcion_text = nueva_desc
                print("SobreMi: cambios guardados en BD.")
            except Exception as e:
                print("Error guardando SobreMi en BD:", e)

        # Ocultar campos y restaurar labels visibles
        Animation.cancel_all(intro_field)
        Animation.cancel_all(desc_field)
        Animation(opacity=0, d=0.18).start(intro_field)
        Animation(opacity=0, d=0.18).start(desc_field)

        lbl_intro.opacity = 1
        lbl_desc.opacity = 1

        intro_field.focus = False
        desc_field.focus = False
        self.campos_visibles = False

    def update_introduccion_from_input(self):
        """Se llama con on_text_validate (Enter) desde el MDTextField de introducción -> guarda."""
        # Guardar y ocultar (save=True)
        self.ocultar_campos_edicion(save=True)

    def update_descripcion_from_input(self):
        """Se llama con on_text_validate (Enter) desde el MDTextField de descripción -> guarda."""
        self.ocultar_campos_edicion(save=True)


class CardListScreen(Screen):
    grid_id = ""
    card_radius = [15]
    card_bg_color = (225 / 255, 225 / 255, 225 / 255, 1)
    card_padding = (dp(16), dp(16), dp(16), dp(16))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._refresh_trigger = Clock.create_trigger(self._populate_cards, 0)
        Window.bind(size=self._on_window_resize)

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        self._refresh_trigger()

    def on_enter(self):
        super().on_enter()
        self._refresh_trigger()

    def _on_window_resize(self, *args):
        if self.manager and self.manager.current == self.name:
            self._refresh_trigger()

    def _populate_cards(self, *args):
        grid = self.ids.get(self.grid_id)
        if not grid:
            return

        grid.clear_widgets()
        card_height, image_height = self._compute_card_metrics()

        for item in self._card_data():
            grid.add_widget(self._build_card(item, card_height, image_height))

        # 👇 AÑADIDO: después de repoblar, vuelve a poner el botón "+"
        if hasattr(self, "agregar_boton_mas"):
            try:
                self.agregar_boton_mas()
            except Exception as e:
                print("Error al agregar botón '+':", e)
        if grid.parent and hasattr(grid.parent, 'scroll_y'):
            grid.parent.scroll_y = 1  # Ir al tope

    def _compute_card_metrics(self):
        available_width = self.width or Window.width
        usable_width = max(dp(280), min(available_width - dp(32), dp(420)))
        card_height = max(dp(220), usable_width * 0.55)
        image_height = max(dp(100), card_height * 0.55)
        return card_height, image_height

    def _make_label(self, text, font_style=None, theme_text_color=None, wrap=False):
        label = MDLabel(
            text=text,
            halign="center",
            size_hint_y=None,
        )
        if font_style:
            label.font_style = font_style
        if theme_text_color:
            label.theme_text_color = theme_text_color
        label.bind(texture_size=lambda instance,
                   value: instance.setter("height")(instance, value[1]))
        if wrap:
            label.bind(width=lambda instance, value: instance.setter(
                "text_size")(instance, (value, None)))
        return label

    def _make_image(self, source, image_height):
        return FitImage(
            source=source,
            size_hint=(1, None),
            height=image_height,
            radius=[dp(12), dp(12), dp(12), dp(12)],
        )

    def _bind_card_height(self, card, content_box, baseline_height):
        def _resolve_padding(padding_value):
            if isinstance(padding_value, (list, tuple)):
                if len(padding_value) == 4:
                    return padding_value[1] + padding_value[3]
                if len(padding_value) == 2:
                    return padding_value[1] * 2
                if len(padding_value) == 1:
                    return padding_value[0] * 2
                return padding_value[0] * 2
            return padding_value * 2

        def update_height(instance, value):
            top_bottom = _resolve_padding(
                card.padding) if hasattr(card, "padding") else 0
            card.height = max(baseline_height, value + top_bottom)

        content_box.bind(minimum_height=update_height)
        update_height(content_box, content_box.minimum_height)

    def _card_data(self):
        raise NotImplementedError

    def _build_card(self, item, card_height, image_height):
        raise NotImplementedError

# imagen por defecto si no hay en BD


def _img_or_default(src: str, default="../assets/img/luna.jpg"):
    return src if src else default

# ---ProyectosScreen ahora lee desde SQLite con gestor.py ---


class ProyectosScreen(CardListScreen):
    grid_id = "proyectos_grid"

    # ──────────────────────────────── GENERAL ────────────────────────────────
    def abrir_enlace(self, url):
        import webbrowser
        webbrowser.open(url)

    def volver_home(self):
        self.manager.current = "home"

    def _card_data(self):
        filas = gestor.listar_proyectos()
        data = []
        for r in filas:
            data.append({
                "id": r.get("id"),
                "titulo": r.get("titulo", "(Sin título)"),
                "descripcion": r.get("descripcion", ""),
                "imagen": _img_or_default(r.get("imagen")),
                "link": r.get("link", ""),
            })
        if not data:
            data = [{
                "id": None,
                "titulo": "Aún no hay proyectos",
                "descripcion": "Agrega un proyecto para verlo aquí.",
                "imagen": "../assets/img/luna.jpg",
                "link": "",
            }]
        return data

    def _build_card(self, data, card_height, image_height):
        card = MDCard(
            size_hint=(1, None),
            height=card_height,
            radius=self.card_radius,
            padding=self.card_padding,
            md_bg_color=self.card_bg_color,
        )

        box = MDBoxLayout(orientation="vertical", spacing=dp(12))
        box.size_hint_y = None
        box.bind(minimum_height=box.setter("height"))

        img = self._make_image(data["imagen"], image_height)
        title = self._make_label(data["titulo"], font_style="H6")
        desc = self._make_label(
            data["descripcion"], theme_text_color="Secondary", wrap=True)

        bottom = RelativeLayout(size_hint_y=None, height=dp(50))

        # Botón eliminar
        btn_del = SilentIconButton(
            icon="trash-can", size_hint=(None, None),
            size=(dp(36), dp(36)), pos_hint={"x": 0, "center_y": 0.5})
        btn_del.bind(on_release=lambda *_: self.confirmar_eliminar(data))
        bottom.add_widget(btn_del)

        # Botón ver más
        btn_more = SilentFlatButton(
            text="Ver más", size_hint=(None, None),
            width=dp(120), height=dp(42),
            pos_hint={"center_x": 0.5, "center_y": 0.5})
        if data.get("link"):
            btn_more.bind(
                on_release=lambda *_: self.abrir_enlace(data["link"]))
        else:
            btn_more.disabled = True
        bottom.add_widget(btn_more)

        # Botón editar
        btn_edit = SilentIconButton(
            icon="pencil", size_hint=(None, None),
            size=(dp(36), dp(36)), pos_hint={"right": 1, "center_y": 0.5})
        btn_edit.bind(on_release=lambda *_: self.editar_proyecto(data))
        bottom.add_widget(btn_edit)

        for w in (img, title, desc, bottom):
            box.add_widget(w)
        card.add_widget(box)
        self._bind_card_height(card, box, card_height)
        return card

    def on_enter(self):
        self.agregar_boton_mas()

    def agregar_boton_mas(self):
        grid = self.ids.get(self.grid_id)
        if not grid:
            return
        for w in grid.children:
            if hasattr(w, "is_add_button") and w.is_add_button:
                return
        container = AnchorLayout(anchor_x="center", anchor_y="center",
                                 size_hint_y=None, height=dp(90))
        btn_add = FlatCircularFAB(icon="plus")
        btn_add.bind(on_release=self.nuevo_proyecto)
        btn_add.is_add_button = True
        container.add_widget(btn_add)
        container.is_add_button = True
        grid.add_widget(container)

    # ──────────────────────────────── NUEVO PROYECTO ────────────────────────────────
    def nuevo_proyecto(self, *args):
        content = MDBoxLayout(
            orientation="vertical", spacing=dp(10),
            padding=[dp(20), dp(5), dp(20), dp(15)], adaptive_height=True)

        titulo_field = MDTextField(hint_text="Título del proyecto",
                                   size_hint_y=None, height=dp(56))
        desc_field = MDTextField(hint_text="Descripción",
                                 size_hint_y=None, height=dp(56))
        link_field = MDTextField(hint_text="URL (opcional)",
                                 size_hint_y=None, height=dp(56))
        imagen_field = MDTextField(
            hint_text="Ruta imagen (opcional)",
            text="../assets/img/luna.jpg", size_hint_y=None, height=dp(56))
        btn_img = SilentRaisedButton(
            text="Seleccionar imagen", size_hint_y=None, height=dp(40))
        btn_img.bind(
            on_release=lambda *_: self.abrir_filechooser(imagen_field))

        for w in (titulo_field, desc_field, link_field, imagen_field, btn_img):
            content.add_widget(w)

        btn_cancelar = SilentDialogButton(text="Cancelar")
        btn_guardar = SilentDialogButton(text="Guardar")

        dialog = MDDialog(
            title="Nuevo proyecto", type="custom",
            content_cls=content, buttons=[btn_cancelar, btn_guardar])

        def confirmar_agregar(dlg):
            confirm = MDDialog(
                title="Confirmar acción",
                text="¿Seguro que quieres agregar este proyecto?",
                buttons=[
                    SilentDialogButton(
                        text="No", on_release=lambda *_: confirm.dismiss()),
                    SilentDialogButton(
                        text="Sí",
                        on_release=lambda *_: (
                            self.guardar_nuevo_proyecto(
                                dlg, titulo_field, desc_field, link_field, imagen_field),
                            confirm.dismiss(),
                            self.mostrar_mensaje_global(
                                "Proyecto agregado con éxito")
                        )
                    )
                ]
            )
            confirm.open()

        btn_cancelar.bind(on_release=lambda *_: dialog.dismiss())
        btn_guardar.bind(on_release=lambda *_: confirmar_agregar(dialog))
        dialog.open()

    def guardar_nuevo_proyecto(self, dlg, titulo_field, desc_field, link_field, imagen_field):
        titulo = titulo_field.text.strip()
        descripcion = desc_field.text.strip()
        link = link_field.text.strip()
        imagen = imagen_field.text.strip() or None
        if not titulo:
            self.mostrar_mensaje_global("⚠️ El título es obligatorio")
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        usuario = getattr(app, "usuario_actual", None)
        if not usuario:
            dlg.dismiss()
            return
        id_usuario = usuario.get("id_usuario")
        gestor.crear_proyecto(titulo, descripcion, imagen, link, id_usuario)
        dlg.dismiss()
        self._refresh_trigger()

    # ──────────────────────────────── EDITAR PROYECTO ────────────────────────────────
    def editar_proyecto(self, data):
        pid = data.get("id")
        if not pid:
            return

        scroll = ScrollView(size_hint=(1, None), size=(Window.width, dp(400)))
        content = MDBoxLayout(
            orientation="vertical", spacing=dp(10),
            padding=[dp(20), dp(5), dp(20), dp(15)], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)

        titulo_field = MDTextField(hint_text="Título", text=data.get(
            "titulo", ""), size_hint_y=None, height=dp(56))
        desc_field = MDTextField(hint_text="Descripción", text=data.get(
            "descripcion", ""), size_hint_y=None, height=dp(56))
        link_field = MDTextField(hint_text="URL", text=data.get(
            "link", ""), size_hint_y=None, height=dp(56))
        imagen_field = MDTextField(hint_text="Ruta imagen", text=data.get(
            "imagen", ""), size_hint_y=None, height=dp(56))
        btn_img = SilentRaisedButton(
            text="Seleccionar nueva imagen", size_hint_y=None, height=dp(40))
        btn_img.bind(
            on_release=lambda *_: self.abrir_filechooser(imagen_field))

        for w in (titulo_field, desc_field, link_field, imagen_field, btn_img):
            content.add_widget(w)

        btn_cancelar = SilentDialogButton(text="Cancelar")
        btn_guardar = SilentDialogButton(text="Guardar")

        dialog = MDDialog(
            title="Editar proyecto", type="custom",
            content_cls=scroll, buttons=[btn_cancelar, btn_guardar])

        def confirmar_guardado(dlg):
            confirm = MDDialog(
                title="Confirmar acción",
                text="¿Estás seguro que quieres guardar los cambios?",
                buttons=[
                    SilentDialogButton(
                        text="No", on_release=lambda *_: confirm.dismiss()),
                    SilentDialogButton(
                        text="Sí",
                        on_release=lambda *_: (
                            self.guardar_cambios_proyecto(
                                pid, titulo_field, desc_field, link_field, imagen_field),
                            dlg.dismiss(),
                            confirm.dismiss(),
                            self.mostrar_mensaje_global(
                                "Cambios guardados con éxito")
                        )
                    )
                ]
            )
            confirm.open()

        btn_cancelar.bind(on_release=lambda *_: dialog.dismiss())
        btn_guardar.bind(on_release=lambda *_: confirmar_guardado(dialog))
        dialog.open()

    def guardar_cambios_proyecto(self, pid, titulo_field, desc_field, link_field, imagen_field):
        gestor.actualizar_proyecto(pid,
                                   titulo=titulo_field.text.strip(),
                                   descripcion=desc_field.text.strip(),
                                   link=link_field.text.strip(),
                                   imagen=imagen_field.text.strip())
        self._refresh_trigger()

    # ──────────────────────────────── ELIMINAR PROYECTO ────────────────────────────────
    def confirmar_eliminar(self, data):
        pid = data.get("id")
        if not pid:
            return
        dialog = MDDialog(
            title="Confirmar eliminación",
            text="¿Estás seguro que quieres eliminar este proyecto?",
            buttons=[
                SilentDialogButton(
                    text="No", on_release=lambda *_: dialog.dismiss()),
                SilentDialogButton(
                    text="Sí",
                    on_release=lambda *_: (
                        self.eliminar_proyecto(pid),
                        dialog.dismiss(),
                        self.mostrar_mensaje_global(
                            "Proyecto eliminado con éxito")
                    )
                )
            ]
        )
        dialog.open()

    def eliminar_proyecto(self, pid):
        gestor.eliminar_proyecto(pid)
        self._refresh_trigger()

    # ──────────────────────────────── MENSAJE GLOBAL (ÚNICO) ────────────────────────────────
    def mostrar_mensaje_global(self, mensaje="✅ Acción completada"):
        """Muestra un banner superior flotante (uniforme para todas las acciones)."""
        try:
            msg_card = self.ids.proyectos_message
            msg_label = self.ids.proyectos_message_label
        except Exception as e:
            print("⚠️ No se encontraron los IDs del mensaje global:", e)
            return

        msg_label.text = mensaje
        Animation.cancel_all(msg_card)
        msg_card.opacity = 1

        anim_entrada = Animation(
            pos_hint={"center_x": 0.5, "top": 0.97}, d=0.38, t="out_back")
        anim_entrada.start(msg_card)
        Clock.schedule_once(lambda dt: self.ocultar_mensaje_global(), 3.2)

    def ocultar_mensaje_global(self):
        """Oculta el banner animado."""
        try:
            msg_card = self.ids.proyectos_message
        except Exception as e:
            print("⚠️ No se encontraron los IDs del mensaje global (ocultar):", e)
            return

        Animation.cancel_all(msg_card)
        anim_salida = Animation(
            pos_hint={"center_x": 0.5, "top": 1.12},
            opacity=0, d=0.32, t="in_back")
        anim_salida.start(msg_card)

    # ──────────────────────────────── FILECHOOSER ────────────────────────────────
    def abrir_filechooser(self, imagen_field, *_):
        from kivy.utils import platform
        from kivy.uix.popup import Popup
        from kivy.uix.filechooser import FileChooserIconView
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from pathlib import Path
        print("📁 Abriendo selector de imagen...")
        if platform == "android":
            try:
                from plyer import filechooser
                file_path = filechooser.open_file(
                    title="Selecciona una imagen",
                    filters=[("Imágenes", "*.jpg;*.jpeg;*.png;*.webp")])
                if file_path:
                    ruta = file_path[0]
                    imagen_field.text = ruta
                    print(f"✅ Imagen seleccionada (Android): {ruta}")
            except Exception as e:
                print("⚠️ Error al abrir filechooser Android:", e)
            return

        chooser = FileChooserIconView(
            filters=["*.png", "*.jpg", "*.jpeg", "*.webp"],
            show_hidden=True, dirselect=False)
        chooser.multiselect = False
        chooser.path = str(Path.home())

        layout = BoxLayout(orientation="vertical", spacing=5)
        layout.add_widget(chooser)

        botones = BoxLayout(size_hint_y=None, height=dp(48), spacing=5)
        btn_cancelar_fc = Button(text="Cancelar")
        btn_aceptar_fc = Button(text="Seleccionar")
        botones.add_widget(btn_cancelar_fc)
        botones.add_widget(btn_aceptar_fc)
        layout.add_widget(botones)

        popup = Popup(
            title="Selecciona una imagen",
            content=layout, size_hint=(0.9, 0.9))

        def confirmar_seleccion(*_):
            if chooser.selection:
                ruta = chooser.selection[0]
                imagen_field.text = ruta
                print(f"✅ Imagen seleccionada (PC): {ruta}")
            popup.dismiss()

        btn_cancelar_fc.bind(on_release=lambda *_: popup.dismiss())
        btn_aceptar_fc.bind(on_release=confirmar_seleccion)
        popup.open()


class HabilidadesScreen(CardListScreen):
    grid_id = "habilidades_grid"

    # ──────────────────────────────── DATOS ────────────────────────────────
    def _card_data(self):
        filas = gestor.listar_habilidades()
        data = []
        for r in filas:
            data.append({
                "id": r.get("id"),
                "titulo": r.get("nombre", "(Sin nombre)"),
                "nivel": f"Nivel: {r.get('nivel', 1)}",
                "nivel_valor": r.get("nivel", 1),
                "descripcion": r.get("descripcion", ""),
                "imagen": _img_or_default(r.get("imagen") or "../assets/img/python.jpg"),
            })

        if not data:
            data = [
                {
                    "id": None,
                    "titulo": "Aún no hay habilidades",
                    "nivel": "Nivel: Intermedio",
                    "descripcion": "Agrega una habilidad para verla aquí.",
                    "imagen": "../assets/img/python.jpg",
                },
                {
                    "id": None,
                    "titulo": "Aún no hay habilidades",
                    "nivel": "Nivel: Avanzado",
                    "descripcion": "Agrega una habilidad para verla aquí.",
                    "imagen": "../assets/img/html.jpg",
                },
            ]
        return data

    # ──────────────────────────────── CONSTRUCCIÓN DE CARD ────────────────────────────────
    def _build_card(self, data, card_height, image_height):
        card = MDCard(
            size_hint=(1, None),
            height=card_height,
            radius=self.card_radius,
            padding=self.card_padding,
            md_bg_color=self.card_bg_color,
        )

        box = MDBoxLayout(orientation="vertical", spacing=dp(12))
        box.size_hint_y = None
        box.bind(minimum_height=box.setter("height"))

        img = self._make_image(data["imagen"], image_height)
        title = self._make_label(data["titulo"], font_style="H6")
        level = self._make_label(data["nivel"], theme_text_color="Secondary")
        desc = self._make_label(
            data["descripcion"], theme_text_color="Secondary", wrap=True)

        bottom_area = RelativeLayout(size_hint_y=None, height=dp(50))

        # 🗑 Eliminar
        delete_btn = SilentIconButton(
            icon="trash-can",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            pos_hint={"x": 0, "center_y": 0.5},
        )
        delete_btn.bind(on_release=lambda *_: self.confirmar_eliminar(data))
        bottom_area.add_widget(delete_btn)

        # ✏️ Editar
        edit_btn = SilentIconButton(
            icon="pencil",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            pos_hint={"right": 1, "center_y": 0.5},
        )
        edit_btn.bind(on_release=lambda *_: self.editar_habilidad(data))
        bottom_area.add_widget(edit_btn)

        box.add_widget(img)
        box.add_widget(title)
        box.add_widget(level)
        box.add_widget(desc)
        box.add_widget(bottom_area)

        card.add_widget(box)
        self._bind_card_height(card, box, card_height)
        return card

    # ──────────────────────────────── BOTÓN AÑADIR ────────────────────────────────
    def on_enter(self):
        self.agregar_boton_mas()

    def agregar_boton_mas(self):
        grid = self.ids.get(self.grid_id)
        if not grid:
            return
        for w in grid.children:
            if hasattr(w, "is_add_button") and w.is_add_button:
                return

        add_container = AnchorLayout(
            anchor_x="center", anchor_y="center",
            size_hint_y=None, height=dp(90), padding=(0, dp(1), 0, 0)
        )

        add_button = FlatCircularFAB(icon="plus")
        add_button.bind(on_release=self.nueva_habilidad)
        add_button.is_add_button = True
        add_container.add_widget(add_button)
        add_container.is_add_button = True
        grid.add_widget(add_container)

    # ──────────────────────────────── NUEVA HABILIDAD ────────────────────────────────
    def nueva_habilidad(self, *args):
        content = MDBoxLayout(
            orientation="vertical", spacing=dp(10),
            padding=[dp(20), dp(5), dp(20), dp(15)], adaptive_height=True)

        nombre_field = MDTextField(
            hint_text="Nombre de la habilidad", size_hint_y=None, height=dp(56))
        nivel_field = MDTextField(
            hint_text="Nivel (Básico, Intermedio, Avanzado)", size_hint_y=None, height=dp(56))
        descripcion_field = MDTextField(
            hint_text="Descripción", size_hint_y=None, height=dp(56))
        imagen_field = MDTextField(
            hint_text="Ruta de imagen (opcional)",
            text="../assets/img/python.jpg", size_hint_y=None, height=dp(56))
        btn_img = SilentRaisedButton(
            text="Seleccionar imagen", size_hint_y=None, height=dp(40))
        btn_img.bind(
            on_release=lambda *_: self.abrir_filechooser(imagen_field))

        for w in (nombre_field, nivel_field, descripcion_field, imagen_field, btn_img):
            content.add_widget(w)

        btn_cancelar = SilentDialogButton(text="Cancelar")
        btn_guardar = SilentDialogButton(text="Guardar")

        dialog = MDDialog(title="Nueva habilidad", type="custom",
                          content_cls=content, buttons=[btn_cancelar, btn_guardar])

        def confirmar_guardado(dlg):
            confirm = MDDialog(
                title="Confirmar acción",
                text="¿Deseas agregar esta habilidad?",
                buttons=[
                    SilentDialogButton(
                        text="No", on_release=lambda *_: confirm.dismiss()),
                    SilentDialogButton(
                        text="Sí",
                        on_release=lambda *_: (
                            self.guardar_habilidad(
                                dlg, nombre_field, nivel_field, descripcion_field, imagen_field),
                            confirm.dismiss(),
                            self.mostrar_mensaje_global(
                                "Habilidad agregada con éxito")
                        )
                    )
                ]
            )
            confirm.open()

        btn_cancelar.bind(on_release=lambda *_: dialog.dismiss())
        btn_guardar.bind(on_release=lambda *_: confirmar_guardado(dialog))
        dialog.open()

    def guardar_habilidad(self, dlg, nombre_field, nivel_field, descripcion_field, imagen_field):
        nombre = nombre_field.text.strip()
        nivel = nivel_field.text.strip()
        descripcion = descripcion_field.text.strip()
        imagen = imagen_field.text.strip() or None

        if not nombre:
            self.mostrar_mensaje_global("⚠️ El nombre es obligatorio")
            return

        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        usuario = getattr(app, "usuario_actual", None)
        if not usuario:
            dlg.dismiss()
            return

        id_usuario = usuario.get("id_usuario")
        gestor.crear_habilidad(nombre, nivel, descripcion, imagen, id_usuario)
        dlg.dismiss()
        self._refresh_trigger()

    # ──────────────────────────────── EDITAR ────────────────────────────────
    def editar_habilidad(self, data):
        hid = data.get("id")
        if not hid:
            self.mostrar_mensaje_global("No puedes editar ejemplos")
            return

        scroll = ScrollView(size_hint=(1, None), size=(Window.width, dp(400)))
        content = MDBoxLayout(
            orientation="vertical", spacing=dp(10),
            padding=[dp(20), dp(5), dp(20), dp(15)], size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)

        nombre_field = MDTextField(hint_text="Nombre", text=data.get("titulo", ""),
                                   size_hint_y=None, height=dp(56))
        nivel_field = MDTextField(hint_text="Nivel", text=str(data.get("nivel_valor", "")),
                                  size_hint_y=None, height=dp(56))
        descripcion_field = MDTextField(hint_text="Descripción", text=data.get("descripcion", ""),
                                        size_hint_y=None, height=dp(56))
        imagen_field = MDTextField(hint_text="Ruta de imagen", text=data.get("imagen", ""),
                                   size_hint_y=None, height=dp(56))
        btn_img = SilentRaisedButton(text="Seleccionar nueva imagen",
                                     size_hint_y=None, height=dp(40))
        btn_img.bind(
            on_release=lambda *_: self.abrir_filechooser(imagen_field))

        for w in (nombre_field, nivel_field, descripcion_field, imagen_field, btn_img):
            content.add_widget(w)

        btn_cancelar = SilentDialogButton(text="Cancelar")
        btn_guardar = SilentDialogButton(text="Guardar")

        dialog = MDDialog(title="Editar habilidad", type="custom",
                          content_cls=scroll, buttons=[btn_cancelar, btn_guardar])

        def confirmar_guardado(dlg):
            confirm = MDDialog(
                title="Confirmar acción",
                text="¿Guardar los cambios realizados?",
                buttons=[
                    SilentDialogButton(
                        text="No", on_release=lambda *_: confirm.dismiss()),
                    SilentDialogButton(
                        text="Sí",
                        on_release=lambda *_: (
                            self.guardar_cambios(
                                hid, nombre_field, nivel_field, descripcion_field, imagen_field),
                            dlg.dismiss(),
                            confirm.dismiss(),
                            self.mostrar_mensaje_global(
                                "Cambios guardados con éxito")
                        )
                    )
                ]
            )
            confirm.open()

        btn_cancelar.bind(on_release=lambda *_: dialog.dismiss())
        btn_guardar.bind(on_release=lambda *_: confirmar_guardado(dialog))
        dialog.open()

    def guardar_cambios(self, hid, nombre_field, nivel_field, descripcion_field, imagen_field):
        gestor.actualizar_habilidad(
            hid,
            nombre=nombre_field.text.strip(),
            nivel=nivel_field.text.strip(),
            descripcion=descripcion_field.text.strip(),
            imagen=imagen_field.text.strip()
        )
        self._refresh_trigger()

    # ──────────────────────────────── ELIMINAR ────────────────────────────────
    def confirmar_eliminar(self, data):
        hid = data.get("id")
        if not hid:
            self.mostrar_mensaje_global("No puedes eliminar ejemplos")
            return

        dialog = MDDialog(
            title="Confirmar eliminación",
            text="¿Seguro que deseas eliminar esta habilidad?",
            buttons=[
                SilentDialogButton(
                    text="No", on_release=lambda *_: dialog.dismiss()),
                SilentDialogButton(
                    text="Sí",
                    on_release=lambda *_: (
                        self.eliminar_habilidad(hid),
                        dialog.dismiss(),
                        self.mostrar_mensaje_global(
                            "Habilidad eliminada con éxito")
                    )
                )
            ]
        )
        dialog.open()

    def eliminar_habilidad(self, hid):
        gestor.eliminar_habilidad(hid)
        self._refresh_trigger()

    # ──────────────────────────────── MENSAJE GLOBAL ────────────────────────────────
    def mostrar_mensaje_global(self, mensaje="✅ Acción completada"):
        """Muestra un banner flotante sobre el título 'Habilidades'."""
        try:
            msg_card = self.ids.habilidades_message
            msg_label = self.ids.habilidades_message_label
        except Exception as e:
            print("⚠️ No se encontraron los IDs del mensaje global:", e)
            return

        msg_label.text = mensaje
        Animation.cancel_all(msg_card)
        msg_card.opacity = 1

        anim_entrada = Animation(
            pos_hint={"center_x": 0.5, "top": 0.97}, d=0.38, t="out_back")
        anim_entrada.start(msg_card)
        Clock.schedule_once(lambda dt: self.ocultar_mensaje_global(), 3.2)

    def ocultar_mensaje_global(self):
        """Oculta el banner animado."""
        try:
            msg_card = self.ids.habilidades_message
        except Exception as e:
            print("⚠️ No se encontraron los IDs del mensaje global (ocultar):", e)
            return

        Animation.cancel_all(msg_card)
        anim_salida = Animation(
            pos_hint={"center_x": 0.5, "top": 1.12},
            opacity=0, d=0.32, t="in_back")
        anim_salida.start(msg_card)
        
    # ──────────────────────────────── FILECHOOSER ────────────────────────────────
    def abrir_filechooser(self, imagen_field, *_):
        from kivy.utils import platform
        from kivy.uix.popup import Popup
        from kivy.uix.filechooser import FileChooserIconView
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from pathlib import Path
        print("📁 Abriendo selector de imagen...")
        if platform == "android":
            try:
                from plyer import filechooser
                file_path = filechooser.open_file(
                    title="Selecciona una imagen",
                    filters=[("Imágenes", "*.jpg;*.jpeg;*.png;*.webp")])
                if file_path:
                    ruta = file_path[0]
                    imagen_field.text = ruta
                    print(f"✅ Imagen seleccionada (Android): {ruta}")
            except Exception as e:
                print("⚠️ Error al abrir filechooser Android:", e)
            return

        chooser = FileChooserIconView(
            filters=["*.png", "*.jpg", "*.jpeg", "*.webp"],
            show_hidden=True, dirselect=False)
        chooser.multiselect = False
        chooser.path = str(Path.home())

        layout = BoxLayout(orientation="vertical", spacing=5)
        layout.add_widget(chooser)

        botones = BoxLayout(size_hint_y=None, height=dp(48), spacing=5)
        btn_cancelar_fc = Button(text="Cancelar")
        btn_aceptar_fc = Button(text="Seleccionar")
        botones.add_widget(btn_cancelar_fc)
        botones.add_widget(btn_aceptar_fc)
        layout.add_widget(botones)

        popup = Popup(
            title="Selecciona una imagen",
            content=layout, size_hint=(0.9, 0.9))

        def confirmar_seleccion(*_):
            if chooser.selection:
                ruta = chooser.selection[0]
                imagen_field.text = ruta
                print(f"✅ Imagen seleccionada (PC): {ruta}")
            popup.dismiss()

        btn_cancelar_fc.bind(on_release=lambda *_: popup.dismiss())
        btn_aceptar_fc.bind(on_release=confirmar_seleccion)
        popup.open()


class PortafolioApp(MDApp):
    def build(self):
        # Inicializa la base de datos usando el schema.sql si existe
        gestor.init_db(use_schema=True)

        # Crea el usuario por defecto si no hay ninguno
        gestor.crear_usuario_defecto()

        # Carga la interfaz principal desde el archivo KV
        return Builder.load_file("portafolio.kv")

    def on_start(self):
        self.root.ids.screen_manager.current = "login"
        self.usuario_actual = None  # aún no hay usuario logueado

        # Bind al ScreenManager para detectar cambios de pantalla
        self.root.ids.screen_manager.bind(current=self.on_screen_change)

        # Actualiza visibilidad inicial del botón hamburger
        self.update_hamburger_visibility()

    def on_screen_change(self, instance, value):
        self.update_hamburger_visibility()

    def update_hamburger_visibility(self):
        # Usar get para no romperse si el id no existe
        hamburger = self.root.ids.get("hamburger_button")
        if hamburger:
            current_screen = self.root.ids.screen_manager.current
            if current_screen == "login":
                hamburger.opacity = 0
                hamburger.disabled = True
            else:
                hamburger.opacity = 1
                hamburger.disabled = False

    def toggle_nav_drawer(self):
        nav_drawer = self.root.ids.get("nav_drawer")
        if nav_drawer:
            if nav_drawer.state == "open":
                nav_drawer.set_state("close")
            else:
                nav_drawer.set_state("open")

    def set_usuario_actual(self, usuario_data: dict):
        self.usuario_actual = usuario_data

    def cerrar_sesion(self):
        self.usuario_actual = None
        self.root.ids.screen_manager.current = "login"

    def login(self, email: str, clave: str):
        usuario = gestor.verificar_login(email, clave)
        if usuario:
            self.set_usuario_actual(usuario)
            self.root.ids.screen_manager.current = "home"


# --- 🔄 FIN CAMBIO build() ---
if __name__ == "__main__":
    PortafolioApp().run()
