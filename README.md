# Flask example app

Esta es una aplicación de ejemplo en **Python + Flask**, lista para producción con Docker, que incluye:

- Logging estructurado (JSON en producción, legible en desarrollo)
- Request ID único por request para trazabilidad
- Medición de **latencia / duration** por request
- Configuración separada por entorno (dev/prod)
- Compatible con Gunicorn y Docker
- Preparada para centralización de logs y trazabilidad

## Estructura del proyecto

```
app/
├── main.py # Fábrica de aplicación Flask (create_app)
├── static # Archivos estáticos que no cambian dinámicamente
├── templates # Plantillas HTML dinámicas usando Jinja2
├── config.py # Configuración de producción/desarrollo
├── logging_config.py # Configuración de logging (dev/prod)
├── logging_filters.py # Filtro RequestIdFilter
wsgi.py # Entrada WSGI para Gunicorn
Dockerfile
requirements.txt # librerías que utiliza la aplicación

```

## Funcionalidades implementadas


1. Fábrica de aplicaciones (create_app)
    - Permite instanciar Flask para desarrollo o producción
    - Compatible con WSGI/Gunicorn
2. Logging centralizado
    - logging_config.py con soporte dev/prod
    - Filtro RequestIdFilter para incluir request_id en logs de Flask
    - DefaultingFormatter previene errores de KeyError
3. Middleware Flask
    - before_request: genera request_id y marca tiempo de inicio
    - after_request: calcula duración y logea información estructurada
4. Rutas de ejemplo
    - / → Hola, mundo!
    - /ping → {"status": "ok"}


## Ejecución con docker

```
docker build -t flask-prod .
```

### Desarrollo

```
docker run -it --rm \
        -p 80:8000 \
        -e FLASK_ENV=development \
        -e SECRET_KEY=dev-secret-key \
        flask-prod
```

### Producción

```
docker run -it --rm \
        -p 80:8000 \
        -e FLASK_ENV=producction \
        -e SECRET_KEY=dev-secret-key \
        flask-prod
```

