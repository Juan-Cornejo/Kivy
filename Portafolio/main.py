from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.utils import get_color_from_hex

# Tamaño de ventana (para pruebas en escritorio)
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
    line_color = (1, 1, 1, 0) # Elimina linea azul del boton
      
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
    def abrir_github(self):
        import webbrowser
        webbrowser.open("https://github.com/tuusuario")

class ProyectosScreen(Screen):
    def abrir_enlace(self, url):
        import webbrowser
        webbrowser.open(url)

    def volver_home(self):
        self.manager.current = "home"

class SobreMiScreen(Screen):
    pass

class HabilidadesScreen(Screen):
    pass

class PortafolioApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        MDRectangleFlatButton.uppercase = False
        
        return Builder.load_file("portafolio.kv")

    def toggle_nav_drawer(self):
        nav_drawer = self.root.ids.nav_drawer
        if nav_drawer.state == "open":
            nav_drawer.set_state("close")
        else:
            nav_drawer.set_state("open")
    

if __name__ == "__main__":
    PortafolioApp().run()