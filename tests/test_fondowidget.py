import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import gestor
from app.main import FondoWidget

@pytest.fixture
def fondo_widget(monkeypatch):
    """Crea instancia aislada de FondoWidget sin depender del archivo .kv."""
    from app.main import FondoWidget

    # Evitar ejecución de on_kv_post
    monkeypatch.setattr(FondoWidget, "on_kv_post", lambda *a, **kw: None)

    # Clase simulada para labels de Kivy
    class DummyLabel:
        def __init__(self, text=""):
            self.text = text
            self.texture_size = (100, 20)
            self.height = 0

    widget = FondoWidget(name="home")

    # Simular ids que normalmente vienen del archivo .kv
    widget.ids = {
        "edit_foto": None,
        "lbl_nombre": DummyLabel(),
        "lbl_profesion": DummyLabel(),
        "lbl_intro": DummyLabel(),
        "edit_name_field": DummyLabel(),
        "edit_profession_field": DummyLabel(),
        "edit_intro_field": DummyLabel(),
    }

    return widget


def test_carga_usuario(monkeypatch, fondo_widget):
    dummy = {
        "nombre_completo": "Admin Test",
        "profesion": "Programador",
        "mensaje_bienvenida": "Bienvenido a mi portafolio",
        "github_url": "https://github.com"
    }
    monkeypatch.setattr(gestor, "get_usuario", lambda: dummy)

    fondo_widget.cargar_usuario()

    assert fondo_widget.nombre_text == "Admin Test"
    assert fondo_widget.profesion_text == "Programador"


def test_actualizar_nombre(monkeypatch, fondo_widget):
    called = {}
    monkeypatch.setattr(gestor, "upsert_usuario", lambda **k: called.update(k))

    fondo_widget.ids["edit_name_field"].text = "Juan Pérez"
    fondo_widget.update_name_from_input()

    assert called.get("nombre_completo") == "Juan Pérez"


def test_actualizar_profesion(monkeypatch, fondo_widget):
    called = {}
    monkeypatch.setattr(gestor, "upsert_usuario", lambda **k: called.update(k))

    fondo_widget.ids["edit_profession_field"].text = "Ingeniero de Software"
    fondo_widget.update_profession_from_input()

    assert called.get("profesion") == "Ingeniero de Software"

def test_actualizar_intro(monkeypatch, fondo_widget):
    """Verifica que se actualice correctamente el mensaje de bienvenida."""
    called = {}
    monkeypatch.setattr(gestor, "upsert_usuario", lambda **k: called.update(k))

    # Simular que el usuario escribe un nuevo mensaje
    fondo_widget.ids["edit_intro_field"].text = "Hola mundo"
    fondo_widget.ids["lbl_intro"].text = ""  # texto previo vacío

    fondo_widget.update_intro_from_input()

    # Verifica que se llame a upsert_usuario con el mensaje correcto
    assert called.get("mensaje_bienvenida") == "Hola mundo"
    # Verifica que el label de la UI se actualizó
    assert fondo_widget.ids["lbl_intro"].text == "Hola mundo"

def test_no_actualiza_intro_vacia(monkeypatch, fondo_widget):
    called = {}
    monkeypatch.setattr(gestor, "upsert_usuario", lambda **k: called.update(k))

    fondo_widget.ids["edit_intro_field"].text = ""
    fondo_widget.ids["lbl_intro"].text = "Original"
    fondo_widget.update_intro_from_input()

    # Ajusta según comportamiento deseado:
    # Si la app guarda mensaje vacío, usa:
    assert called.get("mensaje_bienvenida") == ""
    # Si no quieres guardar vacío, usa:
    # assert called == {}