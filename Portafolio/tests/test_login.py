import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import gestor
from app.main import LoginScreen
from kivymd.app import MDApp

@pytest.fixture
def login_screen():
    """Crea instancia del login screen sin interfaz completa."""
    app = MDApp.get_running_app() or MDApp()
    screen = LoginScreen(name="login")
    return screen

def test_login_valido(login_screen, monkeypatch):
    monkeypatch.setattr(gestor, "verificar_login", lambda e, c: {"email": e})
    login_screen.manager = type("mgr", (), {"current": ""})()
    login_screen.ids = {"email_input": type("", (), {"text": "admin@gmail.com"})(),
                        "clave_input": type("", (), {"text": "1234"})()}
    login_screen.login()
    assert login_screen.manager.current == "home"

def test_login_invalido(login_screen, monkeypatch):
    monkeypatch.setattr(gestor, "verificar_login", lambda e, c: None)
    login_screen.ids = {"email_input": type("", (), {"text": "mal@correo.com"})(),
                        "clave_input": type("", (), {"text": "0000"})()}
    login_screen.dialog = None
    login_screen.login()
    assert login_screen.dialog.text == "Correo o contraseña incorrectos."

def test_login_campos_vacios(login_screen):
    login_screen.ids = {"email_input": type("", (), {"text": ""})(),
                        "clave_input": type("", (), {"text": ""})()}
    login_screen.dialog = None
    login_screen.login()
    assert "Por favor ingrese" in login_screen.dialog.text
