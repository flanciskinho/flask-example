import os
import time
import uuid
import logging
from flask import Flask, g, request, render_template, jsonify
from .logging_config import setup_logging
from .config import DevConfig, ProdConfig
from werkzeug.exceptions import HTTPException



def create_app(env: str = None) -> Flask:
    """
    Fábrica de aplicaciones Flask.
    Configura logging, middlewares y rutas.
    """
    env = env or os.getenv("FLASK_ENV", "production").lower()


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
        g.correlation_id = request.headers.get("X-Correlation-ID") or g.request_id  # mismo para todo el flujo
        g.start_time = time.perf_counter()

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
        response.headers["X-Request-ID"] = getattr(g, "request_id", "-")
        response.headers["X-Correlation-ID"] = getattr(g, "correlation_id", "-")

        duration = int((time.perf_counter() - g.start_time) * 1000)
        duration_ms = int(duration * 1000)

        log_data = {
            "request_id": response.headers["X-Request-ID"],
            "correlation_id": response.headers["X-Correlation-ID"],
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

    # ──────────────── ERRORES ────────────────
    @app.errorhandler(Exception)
    def handle_exception(e):
        """
        Manejador global de excepciones:
        - Logea el error en JSONL con request_id y correlation_id
        - Devuelve respuesta JSON controlada al cliente
        """
        # Determinar código HTTP
        code = getattr(e, "code", 500)  # Si la excepción tiene código HTTP, usarlo
        message = getattr(e, "description", str(e))

        # para evitar mostrar errores internos
        if isinstance(e, HTTPException): 
            code = e.code
            message = e.description
        else:
            code = 500
            message = "Internal server error"

        # Log estructurado
        logger.exception(
            "Unhandled exception occurred",
            extra={
                "request_id": getattr(g, "request_id", "-"),
                "correlation_id": getattr(g, "correlation_id", "-"),
                "path": request.path,
                "method": request.method,
                "status": code,
            }
        )

        # Respuesta JSON para el cliente
        response = {
            "status": "error",
            "message": message,
            "request_id": getattr(g, "request_id", "-"),
            "correlation_id": getattr(g, "correlation_id", "-")
        }

        return jsonify(response), code    

    return app

# ──────────────── EJECUCIÓN LOCAL ────────────────

if __name__ == "__main__":
    app = create_app(env="development")
    app.run(host="0.0.0.0", port=5000, debug=True)
