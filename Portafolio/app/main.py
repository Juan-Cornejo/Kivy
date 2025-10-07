from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.utils import get_color_from_hex, platform
from kivy.metrics import dp
from kivy.clock import Clock

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


class SilentRectangleFlatButton(MDRectangleFlatButton):
    ripple_behavior = False  # Desactiva el ripple
    text_color = (0, 0, 0, 1)  # Negro
    md_bg_color = get_color_from_hex("#B4B4B4")
    line_color = (1, 1, 1, 0)  # Elimina linea azul del boton

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = self.text

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dispatch('on_release')
            return True
        return super().on_touch_down(touch)


class SilentIconButton(MDIconButton):
    ripple_behavior = False
    theme_text_color = "Custom"
    text_color = (1, 1, 1, 1)
    md_bg_color = (0, 0, 0, 0)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dispatch('on_release')
            return True
        return super().on_touch_down(touch)


class AnimatedButton(MDFlatButton):
    scale = NumericProperty(1)


class FondoWidget(Screen):
    # props enlazadas al .kv
    nombre_text = StringProperty("")
    profesion_text = StringProperty("")
    intro_text = StringProperty("")
    github_url = StringProperty("")
    foto_source = StringProperty("../assets/img/perfil.jpg")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("✅ FondoWidget inicializado:", self, "desde", __file__)

    def on_pre_enter(self, *args):
        print("✅ on_pre_enter de FondoWidget")
        # Llama en el siguiente frame (evita choques de carga con el kv)
        Clock.schedule_once(lambda *_: self.cargar_usuario(), 0)

    def cargar_usuario(self, *args):
        print("✅ cargar_usuario existe y fue llamada")
        try:
            data = gestor.get_usuario()
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

        self.nombre_text = data.get("nombre_completo") or "Nombre Apellido"
        self.profesion_text = data.get(
            "profesion") or "Desarrollador | Programador"
        self.intro_text = data.get(
            "introduccion") or "Bienvenido a mi portafolio"
        self.github_url = data.get("github_url") or ""
        self.foto_source = data.get(
            "foto_perfil") or "../assets/img/perfil.jpg"

    def abrir_github(self):
        import webbrowser
        if self.github_url:
            webbrowser.open(self.github_url)


def cargar_usuario(self):
    try:
        data = gestor.get_usuario()  # debe devolver dict con las claves de BD
    except Exception as e:
        print("Error cargando usuario:", e)
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
    self.intro_text = data.get("introduccion") or "Bienvenido a mi portafolio"
    self.github_url = data.get("github_url") or ""
    self.foto_source = data.get("foto_perfil") or "../assets/img/perfil.jpg"

    def abrir_github(self):
        import webbrowser
        if self.github_url:
            webbrowser.open(self.github_url)


class SobreMiScreen(Screen):
    pass


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
        image_height = max(dp(100), card_height * 0.45)
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
        # dicts: titulo, descripcion, imagen, link, ...
        filas = gestor.listar_proyectos()
        data = []
        for r in filas:
            data.append({
                "titulo": r.get("titulo", "(Sin título)"),
                "descripcion": r.get("descripcion", ""),
                "imagen": _img_or_default(r.get("imagen")),
                "link": r.get("link", ""),
            })
        if not data:
            data = [{
                "titulo": "Aún no hay proyectos",
                "descripcion": "Agrega un proyecto para verlo aquí.",
                "imagen": "../assets/img/luna.jpg",
                "link": ""
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

        button = MDFlatButton(
            text="Ver más",
            size_hint=(1, None),
            height=dp(42),
        )
        if data.get("link"):
            button.bind(on_release=lambda i,
                        link=data["link"]: self.abrir_enlace(link))
        else:
            button.disabled = True

        box.add_widget(img)
        box.add_widget(title)
        box.add_widget(description)
        box.add_widget(button)

        card.add_widget(box)
        self._bind_card_height(card, box, card_height)
        return card
# --- 🔄 FIN CAMBIO ProyectosScreen ---


# --- 🔄 CAMBIADO: HabilidadesScreen ahora lee desde SQLite con gestor.py ---
class HabilidadesScreen(CardListScreen):
    grid_id = "habilidades_grid"

    def _card_data(self):
        filas = gestor.listar_habilidades()  # dicts: id, nombre, nivel, creado_en
        data = []
        for r in filas:
            data.append({
                "titulo": r.get("nombre", "(Sin nombre)"),
                "nivel": f"Nivel: {r.get('nivel', 1)}",
                # si no tienes esta col en BD, quedará vacío
                "descripcion": r.get("descripcion", ""),
                "imagen": "../assets/img/python.jpg",     # imagen genérica para skills
            })
        if not data:
            data = [{
                "titulo": "Aún no hay habilidades",
                "nivel": "Nivel: —",
                "descripcion": "Agrega habilidades para verlas aquí.",
                "imagen": "../assets/img/python.jpg",
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

        box.add_widget(img)
        box.add_widget(title)
        box.add_widget(level)
        box.add_widget(description)

        card.add_widget(box)
        self._bind_card_height(card, box, card_height)
        return card
# --- 🔄 FIN CAMBIO HabilidadesScreen ---


# --- 🔄 CAMBIADO: build() ahora inicializa la BD y no fuerza tema/colores ---
class PortafolioApp(MDApp):
    def build(self):
        # Inicializa la base de datos (usa data/schema.sql si existe)
        gestor.init_db(use_schema=True)
        # gestor.seed_demo()  # opcional para cargar datos de ejemplo

        # La UI y estilos los controlas en el archivo .kv
        return Builder.load_file("portafolio.kv")

    def toggle_nav_drawer(self):
        nav_drawer = self.root.ids.nav_drawer
        if nav_drawer.state == "open":
            nav_drawer.set_state("close")
        else:
            nav_drawer.set_state("open")
# --- 🔄 FIN CAMBIO build() ---


if __name__ == "__main__":
    PortafolioApp().run()
