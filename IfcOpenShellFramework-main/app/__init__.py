"""

Init que establece la configuración de la aplicación Flask

"""

#Imports
from flask import Flask, jsonify
from app.api.v1.endpoints import ifcOpenShellFramework

#Función que crea y devuelve la instancia Flask
def create_app():
    #Crea una instancia de Flask
    app = Flask(__name__)

    #Inicializar extensiones y su configuración

    #Registra el BluePrint principal
    app.register_blueprint(ifcOpenShellFramework, url_prefix='/ifcopenshell')

    #Registrar manejadores de errores personalizados (En desarrollo)
    register_error_handlers(app)

    #Devuelve la instancia del objeto Flask
    return app

#Función que se encarga de establecer los Handlers Errores (En desarrollo)
def register_error_handlers(app):
   pass