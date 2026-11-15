"""Extensões do Flask, criadas aqui e ligadas à aplicação em create_app()."""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Entre na sua conta para continuar."
login_manager.login_message_category = "aviso"
