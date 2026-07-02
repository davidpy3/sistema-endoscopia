# Sistema de Endoscopia

Guía paso a paso para levantar el backend Django y el frontend Angular en desarrollo.

## Requisitos

- Python 3
- Node.js y npm
- Entorno virtual de Python en la raíz del proyecto: `.venv`

## Opción rápida: un solo comando

Si quieres levantar todo de una vez, haz esto desde la raíz del proyecto:

1. Abre una terminal en la carpeta principal del repositorio.
2. Dale permisos de ejecución al script si hace falta:

```bash
chmod +x start_all.sh
```

3. Ejecuta el script:

```bash
./start_all.sh
```

Ese script hace lo siguiente:

1. Crea `.venv` si no existe.
2. Activa el entorno virtual.
3. Instala las dependencias de Python.
4. Instala las dependencias de Angular si faltan.
5. Aplica migraciones de Django.
6. Levanta el backend en `http://127.0.0.1:8000/`.
7. Levanta el frontend en `http://localhost:4200/`.

## Opción manual: paso a paso

### 1. Crear el entorno virtual de Django

Si el entorno virtual no existe, créalo primero desde la raíz del proyecto:

```bash
python3 -m venv .venv
```

### 2. Activar el entorno virtual

Actívalo desde la raíz del proyecto:

```bash
source .venv/bin/activate
```

Si todo quedó bien, el prompt debe mostrar algo como `(.venv)` al inicio.

### 3. Instalar dependencias de Python

Con el entorno virtual activo, instala los paquetes del backend:

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

Antes de arrancar Django, crea o actualiza la base de datos:

```bash
python manage.py migrate
```

### 5. Levantar el backend Django

Desde la raíz del proyecto ejecuta:

```bash
python manage.py runserver
```

Si quieres exponerlo en red local:

```bash
python manage.py runserver 0.0.0.0:8000
```

El backend quedará disponible en:

```text
http://127.0.0.1:8000/
```

### 6. Entrar al frontend Angular

Abre una segunda terminal y entra a la carpeta `frontend`:

```bash
cd frontend
```

### 7. Instalar dependencias del frontend

Si es la primera vez o cambiaste paquetes, instala dependencias:

```bash
npm install
```

### 8. Levantar Angular

Levanta el frontend con el proxy configurado:

```bash
npm run start
```

Eso ejecuta `ng serve --proxy-config proxy.conf.json` y deja el frontend en:

```text
http://localhost:4200/
```

## Flujo recomendado para desarrollo

1. Activa `.venv`.
2. Instala dependencias de Python.
3. Aplica migraciones.
4. Levanta el backend con `python manage.py runserver`.
5. En otra terminal, entra a `frontend/`.
6. Instala dependencias del frontend si hace falta.
7. Levanta Angular con `npm run start`.
8. Abre `http://localhost:4200/` en el navegador.

## Datos demo

Si necesitas cargar datos de prueba:

```bash
python seed_demo_data.py
```

## Observaciones

- El backend usa SQLite en desarrollo.
- El frontend usa proxy hacia Django para las llamadas a la API.
- Si cambias dependencias de Python, vuelve a ejecutar `pip install -r requirements.txt`.
- Si cambias dependencias de Angular, vuelve a ejecutar `npm install` dentro de `frontend/`.
