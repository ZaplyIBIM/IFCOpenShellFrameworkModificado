"""
Configuración de la aplicación
"""

from flask import Flask, jsonify
from app.api.v1.endpoints import ifcOpenShellFramework

def create_app():
    app = Flask(__name__)

    #Aplicar ajustes

    #inicializar extensiones


    #Registrar Blueprints
    app.register_blueprint(ifcOpenShellFramework, url_prefix='/ifcopenshell')

    #Registrar manejadores de errores personalizados
    register_error_handlers(app)

    return app


def register_error_handlers(app):
   pass