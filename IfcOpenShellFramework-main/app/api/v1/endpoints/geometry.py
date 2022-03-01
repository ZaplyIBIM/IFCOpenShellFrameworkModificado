"""

Código que crea el BluePrint con los EndPoints que se encargan de los datos geométricos

"""

#Imports

#Importamos FLask
from flask import Blueprint, request, make_response
#Import de la instancia estática de la librería
from app.api.v1.controller import ifcOpenShellExtObj

#Creamos el BluePrint
endpoints_geometry = Blueprint('geometry', __name__)

#EndPoint del Perímetro geométrico del modelo pasado (POST)
@endpoints_geometry.route('/boundarygeominstance/<guidmodels>', methods=['POST'])
def boundarygeominstance(guidmodels):
  data = request.get_json();  
  results = ifcOpenShellExtObj.getBoundaryGeomInstance(guidmodels,data);
  return make_response(str(results),200);

#EndPoint de la geometría básica del modelo pasado (POST)
@endpoints_geometry.route('/basicgeominstance/<guidmodels>', methods=['POST'])
def basicgeominstance(guidmodels):
  data = request.get_json();  
  results = ifcOpenShellExtObj.getBasicGeomInstance(guidmodels,data);
  return make_response(str(results),200);

#EndPoint de las caras del modelo pasado (POST)
@endpoints_geometry.route('/allfaces/<guidmodels>', methods=['POST'])
def getAllFaces(guidmodels):
  data = request.get_json();  
  results = ifcOpenShellExtObj.getAllFaces(guidmodels,data);
  return make_response(str(results),200);