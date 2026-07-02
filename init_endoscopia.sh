#!/bin/bash

echo "======================================"
echo "  CREANDO SISTEMA ENDOSCOPIA DJANGO"
echo "======================================"

PROJECT="endoscopia_system"

# 1. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Actualizar pip
pip install --upgrade pip

# 3. Instalar dependencias base
pip install django
pip install djangorestframework
pip install python-dotenv
pip install pillow
pip install django-filter
pip install django-crispy-forms
pip install crispy-bootstrap5
pip install weasyprint
pip install psycopg2-binary

# 4. Guardar requirements
pip freeze > requirements.txt

# 5. Crear proyecto Django
django-admin startproject config .

# 6. Crear apps modulares
python manage.py startapp authentication
python manage.py startapp users
python manage.py startapp pacientes
python manage.py startapp personal
python manage.py startapp procedimientos
python manage.py startapp eda
python manage.py startapp colonoscopia
python manage.py startapp imagenes
python manage.py startapp reportes
python manage.py startapp auditoria
python manage.py startapp dashboard

# 7. Crear estructura base tipo arquitectura limpia
mkdir -p core/domain
mkdir -p core/application
mkdir -p core/infrastructure

mkdir -p templates
mkdir -p static
mkdir -p media
mkdir -p logs
mkdir -p config/settings

# 8. Crear archivo .env
cat <<EOF > .env
DEBUG=True
SECRET_KEY=change-me
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# PostgreSQL (listo para migración)
POSTGRES_DB=endoscopia
POSTGRES_USER=endoscopia_user
POSTGRES_PASSWORD=123456
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
EOF

# 9. Crear settings base para multi-db
cat <<EOF > config/db.py
import os
from dotenv import load_dotenv

load_dotenv()

def get_database():
    engine = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")

    if "postgresql" in engine:
        return {
            "default": {
                "ENGINE": engine,
                "NAME": os.getenv("POSTGRES_DB"),
                "USER": os.getenv("POSTGRES_USER"),
                "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
                "HOST": os.getenv("POSTGRES_HOST"),
                "PORT": os.getenv("POSTGRES_PORT"),
            }
        }

    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.getenv("DB_NAME", "db.sqlite3"),
        }
    }
EOF

# 10. Modificar settings.py automáticamente
cat <<EOF > config/settings_extra.py
from .db import get_database
DATABASES = get_database()
EOF

# 11. Mensaje final
echo "======================================"
echo "PROYECTO CREADO EXITOSAMENTE"
echo "======================================"
echo "Activa entorno con: source venv/bin/activate"
echo "Ejecuta migraciones: python manage.py migrate"
echo "Run server: python manage.py runserver"
