import os
import time
import uuid
import logging
from flask import Flask, g, request, render_template
from .logging_config import setup_logging
from .config import DevConfig, ProdConfig


def create_app(env: str = None) -> Flask:
    """
    Fábrica de aplicaciones Flask.
    Configura logging, middlewares y rutas.
    """
    env = os.getenv("FLASK_ENV", "production").lower()


    # Inicializa logging según entorno
    setup_logging(env=env)
    # Logger principal
    logger = logging.getLogger(__name__)

    # Crear la aplicación con perfil
    app = Flask(__name__)
    app.config.from_object(
        DevConfig if env == "development" else ProdConfig
    )

    # ──────────────── MIDDLEWARES ────────────────

    @app.before_request
    def start_request():
        """
        Al inicio de cada request:
        - Genera request_id único
        - Guarda timestamp de inicio
        """
        g.request_id = (
            request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )
        g.start_time = time.time()

        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.user_agent.string,
            },
        )

    @app.after_request
    def log_request(response):
        """
        Al finalizar request:
        - Calcula duración
        - Logea información estructurada
        """
        response.headers["X-Request-ID"] = getattr(g, "request_id", "-"),

        duration = time.time() - g.start_time
        duration_ms = int(duration * 1000)

        log_data = {
            "request_id": response.headers["X-Request-ID"],
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "remote_addr": request.remote_addr,
        }

        logger.info("request_completed", extra=log_data)

        return response

    # ──────────────── RUTAS ────────────────

    @app.route("/")
    def index():
        logger.info("acceso a home", extra={"request_id": g.request_id})
        return render_template(
            "index.html",
            mensaje=f"Entorno: {app.config['ENV']}"
        )

    @app.route("/ping")
    def ping():
        logger.info("acceso a ping", extra={"request_id": g.request_id})
        return {"status": "ok"}

    return app


# ──────────────── EJECUCIÓN LOCAL ────────────────

if __name__ == "__main__":
    app = create_app(env="development")
    app.run(host="0.0.0.0", port=5000, debug=True)



"""
import os
import uuid
import logging
from flask import Flask, render_template, request, g
from .config import DevConfig, ProdConfig
from .logging_config import setup_logging


def create_app():
    env = os.getenv("FLASK_ENV", "production").lower()

    setup_logging(env)
    logger = logging.getLogger(__name__)

    app = Flask(__name__)
    app.config.from_object(
        DevConfig if env == "development" else ProdConfig
    )

    @app.before_request
    def set_request_id():
        g.request_id = (
            request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )

    @app.after_request
    def add_request_id_header(response):
        response.headers["X-Request-ID"] = g.request_id
        return response

    @app.before_request
    def log_request():
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.user_agent.string,
            },
        )

    @app.route("/")
    def index():
        logger.info("acceso a home")
        return render_template(
            "index.html",
            mensaje=f"Entorno: {app.config['ENV']}"
        )

    return app

"""