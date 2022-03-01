"""

Código que crea el BluePrint con los EndPoints que se encargan de la conversión

"""

#Imports

#Importamos FLask
from flask import Blueprint, request, make_response
#Import de la instancia estática de la librería
from app.api.v1.controller import ifcOpenShellExtObj

#Creamos el BluePrint
endpoints_converter = Blueprint('converter', __name__)


#EndPoint que transforma a civil (POST)
@endpoints_converter.route('/transformcivilifc/<guidmodels>', methods=['POST'])
def transformCivilIfc(guidmodels):
  data = request.get_json();  
  results = ifcOpenShellExtObj.transformCivilIfc(guidmodels,data);
  return make_response(results,200);