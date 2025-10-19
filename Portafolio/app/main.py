from kivy.core.window import Window
from kivy.lang import Builder
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
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import BooleanProperty
from kivy.app import App
from kivy.metrics import dp
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

# --- YA ESTABA, PERO ES IMPORTANTE ---
import gestor  # gestor.py maneja SQLite (conexión y CRUD)

# Desktop testing window size
if platform in ("win", "linux", "macosx"):
    Window.size = (360, 640)

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
    """
    Icono que actúa como botón, sin ripple, sin fondo ni círculo gris.
    """
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

class CircularAddButton(SilentIconButton):
    """Botón circular gris claro, sin ripple, para 'Agregar proyecto'."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon = "plus"
        self.md_bg_color = (225/255, 225/255, 225/255, 1)
        self.text_color = (0, 0, 0, 1)
        self.size_hint = (None, None)
        self.size = (dp(64), dp(64))
        self.pos_hint = {"center_x": 0.5}
        self.elevation = 3  # leve sombra para resaltar

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

        usuario = gestor.verificar_login(email, clave)  # tu función de verificación
        if usuario:
            MDApp.get_running_app().usuario_actual = usuario
            self.ids.email_input.text = ""
            self.ids.clave_input.text = ""
            self.manager.current = "home"
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
        """Alterna la visibilidad del campo de texto para editar el nombre."""
        field = self.ids.edit_name_field
        label = self.ids.lbl_nombre

        if field.opacity == 0:  # Si está oculto, mostrar
            field.opacity = 1
            field.focus = False
            label.opacity = 0
            
        else:  # Si ya está visible, ocultar
            field.opacity = 0
            label.opacity = 1

    def show_profession_edit_field(self):
        """Alterna la visibilidad del campo de texto para editar la profesión."""
        field = self.ids.edit_profession_field
        label = self.ids.lbl_profesion

        if field.opacity == 0:  # Si está oculto, mostrar
            field.opacity = 1
            field.focus = False
            label.opacity = 0
        else:  # Si ya está visible, ocultar
            field.opacity = 0
            label.opacity = 1
    
    def show_github_edit_field(self):
        """Muestra u oculta el campo de edición de GitHub al presionar el lápiz."""
        github_field = self.ids.edit_github_field

        if github_field.opacity == 0:
            github_field.text = self.github_url  # Cargar la URL actual
            github_field.opacity = 1
            github_field.focus = False
        else:
            github_field.opacity = 0
            github_field.focus = False
            
    def show_intro_edit_field(self):
        """Toggle para mostrar u ocultar el campo de edición de intro"""
        field = self.ids.edit_intro_field
        if field.opacity == 0:
            field.opacity = 1
            field.focus = False
        else:
            field.opacity = 0
            field.focus = False
    
    def update_name_from_input(self):
        """Actualiza el nombre cuando presionamos 'Enter' y lo guarda en la base de datos."""
        new_name = self.ids.edit_name_field.text
        print("Nuevo nombre:", new_name)

        if new_name:  # Si hay texto
            # Actualizamos el nombre en la UI
            self.nombre_text = new_name
            self.ids.lbl_nombre.text = new_name  # Actualizamos el label con el nuevo nombre
            self.ids.lbl_nombre.height = self.ids.lbl_nombre.texture_size[1] + dp(10)

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
            self.ids.lbl_profesion.text = new_profession  # Actualizamos el label con la nueva profesión
            self.ids.lbl_profesion.height = self.ids.lbl_profesion.texture_size[1] + dp(10)

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
            self.ids.lbl_intro.height = self.ids.lbl_intro.texture_size[1] + dp(10)
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
        self.profesion_text = data.get("profesion") or "Desarrollador | Programador"
        self.intro_text = data.get("mensaje_bienvenida") or "Bienvenido a mi portafolio"
        self.github_url = data.get("github_url") or ""
        self.foto_source = data.get("foto_perfil") or "../assets/img/perfil.jpg"

    def abrir_github(self):
        import webbrowser
        if self.github_url:
            webbrowser.open(self.github_url)

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        print("Modo de edición activado:", self.edit_mode)  # Verifica si el estado cambia
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
                edit_btn.opacity = 1
                Animation(opacity=1, d=0.3).start(edit_btn)
            else:
                edit_btn.disabled = True
                edit_btn.state = "normal"
                edit_btn.focus = False
                edit_btn.md_bg_color = (0, 0, 0, 0)
                Animation(opacity=0, d=0.3).start(edit_btn)
                # desactivar un pelín después de la animación
                Clock.schedule_once(
                    lambda dt, btn=edit_btn: setattr(btn, "disabled", True), 0.3
                )
    # -------------------------------
    # Funcionalidad para cambiar foto de perfil
    # -------------------------------   
    def open_filechooser(self):
        """Abre el FileChooser para seleccionar una nueva imagen de perfil"""
        print("Abriendo el FileChooser...")
        filechooser = FileChooserIconView()
        filechooser.filters = ['*.png', '*.jpg', '*.jpeg']  # Solo imágenes
        filechooser.bind(on_selection=lambda instance, selection: self.on_image_selected(instance, selection))
        
        # Crear un Popup para mostrar el FileChooser
        popup = Popup(title="Selecciona una imagen", content=filechooser, size_hint=(0.8, 0.8))
        popup.open()

    def on_image_selected(self, filechooser, selection):
        """Se llama cuando el usuario selecciona una imagen del FileChooser"""
        if selection:
            image_path = selection[0]
            print("Imagen seleccionada:", image_path)  # Para debug
            self.update_profile_image(image_path)
            self.popup.dismiss()
        else:
            print("❌ No se ha seleccionado ninguna imagen")
    
    def update_profile_image(self, image_path):
        """Actualiza la imagen de perfil en la interfaz y en la base de datos"""
        self.ids.foto_perfil.source = image_path  # Actualiza la imagen en la interfaz
        
        # Ahora actualizamos la imagen en la base de datos
        self.update_user_profile_image(image_path)
    
    def update_user_profile_image(self, new_image_path):
        """Actualiza la ruta de la imagen de perfil en la base de datos"""
        try:
            gestor.upsert_usuario(foto_perfil=new_image_path)
            print("Ruta de la imagen actualizada en la base de datos")
        except Exception as e:
            print("Error al actualizar la imagen en la base de datos:", e)

    def load_profile_image(self):
        """Carga la imagen de perfil desde la base de datos"""
        data = gestor.get_usuario()
        if data and data.get('foto_perfil'):
            self.ids.foto_perfil.source = data['foto_perfil']  # Carga la imagen desde la base de datos
        else:
            self.ids.foto_perfil.source = '../assets/img/perfil.jpg'  # Si no hay imagen, mostramos una por defecto
            
class SobreMiScreen(MDScreen):
    edit_mode = False

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        edit_btn = self.ids.edit_texto

        Animation.cancel_all(edit_btn)

        if self.edit_mode:
            edit_btn.disabled = False
            Animation(opacity=1, d=0.25).start(edit_btn)
        else:
            # Evita el parpadeo gris
            edit_btn.state = "normal"
            edit_btn.focus = False
            edit_btn.md_bg_color = (0, 0, 0, 0)
            Animation(opacity=0, d=0.25).start(edit_btn)
            Clock.schedule_once(lambda dt: setattr(edit_btn, "disabled", True), 0.25)

    def editar_texto_sobremi(self):
        # Aquí luego agregarás la lógica para abrir un popup o campo editable
        print("Editar texto 'Sobre mí' clicado")

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

    def abrir_enlace(self, url):
        import webbrowser
        webbrowser.open(url)

    def volver_home(self):
        self.manager.current = "home"

    def _card_data(self):
        # Lee proyectos desde la BD
        filas = gestor.listar_proyectos()
        data = []
        for r in filas:
            data.append({
                "titulo": r.get("titulo", "(Sin título)"),
                "descripcion": r.get("descripcion", ""),
                "imagen": _img_or_default(r.get("imagen")),
                "link": r.get("link", ""),
            })

        # ✅ Si no hay proyectos, muestra dos tarjetas de ejemplo
        if not data:
            data = [
                {
                    "titulo": "Aún no hay proyectos",
                    "descripcion": "Agrega un proyecto para verlo aquí.",
                    "imagen": "../assets/img/luna.jpg",
                    "link": "https://www.google.com",
                },
                {
                    "titulo": "Aún no hay proyectos",
                    "descripcion": "Agrega un proyecto para verlo aquí.",
                    "imagen": "../assets/img/luna.jpg",
                    "link": "https://www.google.com",
                },
            ]
        return data

    def _build_card(self, data, card_height, image_height):
        card = MDCard(
            size_hint=(1, None),
            height=card_height,
            radius=self.card_radius,
            padding=self.card_padding,
            md_bg_color=self.card_bg_color,
        )

        # --- Contenedor principal ---
        box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
        )
        box.size_hint_y = None
        box.bind(minimum_height=box.setter("height"))

        img = self._make_image(data["imagen"], image_height)
        title = self._make_label(data["titulo"], font_style="H6")
        description = self._make_label(
            data["descripcion"],
            theme_text_color="Secondary",
            wrap=True,
        )

        bottom_area = RelativeLayout(size_hint_y=None, height=dp(50))

        # 1️⃣ Botón de basurero (izquierda)
        delete_btn = SilentIconButton(
            icon="trash-can" if "trash-can" in self._available_icons() else "close",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            pos_hint={"x": 0, "center_y": 0.5},
        )
        delete_btn.bind(on_release=lambda i, d=data: self.eliminar_proyecto(d))
        bottom_area.add_widget(delete_btn)

        # 2️⃣ Botón "Ver más" (centrado)
        button = SilentFlatButton(
            text="Ver más",
            size_hint=(None, None),
            width=dp(120),
            height=dp(42),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        if data.get("link"):
            button.bind(on_release=lambda i, link=data["link"]: self.abrir_enlace(link))
        else:
            button.disabled = True
        bottom_area.add_widget(button)

        # 3️⃣ Botón lápiz (derecha)
        edit_btn = SilentIconButton(
            icon="pencil",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            pos_hint={"right": 1, "center_y": 0.5},
        )
        edit_btn.bind(on_release=lambda i, d=data: self.editar_proyecto(d))
        bottom_area.add_widget(edit_btn)

        # Agregar elementos
        box.add_widget(img)
        box.add_widget(title)
        box.add_widget(description)
        box.add_widget(bottom_area)

        card.add_widget(box)
        self._bind_card_height(card, box, card_height)
        return card

    def on_enter(self):
        """Sobrescribe el evento para agregar el botón '+' al final del ScrollView."""
        self.agregar_boton_mas()

    def agregar_boton_mas(self):
        grid = self.ids.get(self.grid_id)
        if not grid:
            return

        # Evitar duplicados
        for w in grid.children:
            if hasattr(w, "is_add_button") and w.is_add_button:
                return

        # 🔹 Contenedor centrado y un poco más arriba del fondo
        add_container = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_y=None,
            height=dp(90),  # un poco menos alto para acercarlo al final de las cards
            padding=(0, dp(1), 0, 0),
        )

        # 🔹 Botón circular gris claro
        add_button = SilentIconButton(
            icon="plus",
            size_hint=(None, None),
            size=(dp(70), dp(70)),
        )
        add_button.is_add_button = True
        add_button.md_bg_color = (225/255, 225/255, 225/255, 1)
        add_button.text_color = (0, 0, 0, 1)
        add_button.elevation = 3  # leve sombra
        add_button.bind(on_release=self.nuevo_proyecto)
        add_container.add_widget(add_button)
        add_container.is_add_button = True

        grid.add_widget(add_container)

    def nuevo_proyecto(self, *args):
        print("➕ Nuevo proyecto")

    def editar_proyecto(self, data):
        print(f"🖋 Editar proyecto: {data.get('titulo')}")

    def eliminar_proyecto(self, data):
        print(f"🗑 Eliminar proyecto: {data.get('titulo')}")

    def _available_icons(self):
        try:
            from kivymd.icon_definitions import md_icons
            return md_icons.keys()
        except Exception:
            return []

# --- 🔄 CAMBIADO: HabilidadesScreen ahora lee desde SQLite con gestor.py ---
class HabilidadesScreen(CardListScreen):
    grid_id = "habilidades_grid"

    def _card_data(self):
        filas = gestor.listar_habilidades()
        data = []
        for r in filas:
            data.append({
                "titulo": r.get("nombre", "(Sin nombre)"),
                "nivel": f"Nivel: {r.get('nivel', 1)}",
                "descripcion": r.get("descripcion", ""),
                "imagen": "../assets/img/python.jpg",
            })

        # ✅ Tarjetas por defecto si no hay habilidades
        if not data:
            data = [
                {
                    "titulo": "Python",
                    "nivel": "Nivel: Avanzado",
                    "descripcion": "Lenguaje principal para desarrollo backend y automatización.",
                    "imagen": "../assets/img/python.jpg",
                },
                {
                    "titulo": "HTML",
                    "nivel": "Nivel: Intermedio",
                    "descripcion": "Lenguaje de marcado para estructurar páginas web.",
                    "imagen": "../assets/img/html.jpg",
                },
            ]
        return data

    def _build_card(self, data, card_height, image_height):
        card = MDCard(
            size_hint=(1, None),
            height=card_height,
            radius=self.card_radius,
            padding=self.card_padding,
            md_bg_color=self.card_bg_color,
        )

        box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
        )
        box.size_hint_y = None
        box.bind(minimum_height=box.setter("height"))

        img = self._make_image(data["imagen"], image_height)
        title = self._make_label(data["titulo"], font_style="H6")
        level = self._make_label(data["nivel"], theme_text_color="Secondary")
        description = self._make_label(
            data["descripcion"],
            theme_text_color="Secondary",
            wrap=True,
        )

        # 🔹 Área inferior con botones editar/eliminar
        bottom_area = RelativeLayout(size_hint_y=None, height=dp(50))

        # 🗑 Botón eliminar
        delete_btn = SilentIconButton(
            icon="trash-can" if "trash-can" in self._available_icons() else "close",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            pos_hint={"x": 0, "center_y": 0.5},
        )
        delete_btn.bind(on_release=lambda i, d=data: self.eliminar_habilidad(d))
        bottom_area.add_widget(delete_btn)

        # ✏️ Botón editar
        edit_btn = SilentIconButton(
            icon="pencil",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            pos_hint={"right": 1, "center_y": 0.5},
        )
        edit_btn.bind(on_release=lambda i, d=data: self.editar_habilidad(d))
        bottom_area.add_widget(edit_btn)

        box.add_widget(img)
        box.add_widget(title)
        box.add_widget(level)
        box.add_widget(description)
        box.add_widget(bottom_area)

        card.add_widget(box)
        self._bind_card_height(card, box, card_height)
        return card

    def on_enter(self):
        """Agrega el botón '+' al final del ScrollView."""
        self.agregar_boton_mas()

    def agregar_boton_mas(self):
        grid = self.ids.get(self.grid_id)
        if not grid:
            return

        # Evitar duplicados
        for w in grid.children:
            if hasattr(w, "is_add_button") and w.is_add_button:
                return

        add_container = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_y=None,
            height=dp(90),
            padding=(0, dp(1), 0, 0),
        )

        add_button = SilentIconButton(
            icon="plus",
            size_hint=(None, None),
            size=(dp(70), dp(70)),
        )
        add_button.is_add_button = True
        add_button.md_bg_color = (225/255, 225/255, 225/255, 1)
        add_button.text_color = (0, 0, 0, 1)
        add_button.elevation = 3
        add_button.bind(on_release=self.nueva_habilidad)
        add_container.add_widget(add_button)
        add_container.is_add_button = True

        grid.add_widget(add_container)

    def nueva_habilidad(self, *args):
        print("➕ Nueva habilidad")

    def editar_habilidad(self, data):
        print(f"🖋 Editar habilidad: {data.get('titulo')}")

    def eliminar_habilidad(self, data):
        print(f"🗑 Eliminar habilidad: {data.get('titulo')}")

    def _available_icons(self):
        try:
            from kivymd.icon_definitions import md_icons
            return md_icons.keys()
        except Exception:
            return []

# --- 🔄 CAMBIADO: build() ahora inicializa la BD y no fuerza tema/colores ---
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
