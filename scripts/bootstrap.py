"""Ejecutar desde la raíz: python -m scripts.bootstrap"""
from src.database import make_session_factory
from src.services.bootstrap import bootstrap

if __name__ == "__main__":
    created = bootstrap(make_session_factory())
    print("Superusuario creado." if created else "El usuario ya existe; se conservó su registro.")
