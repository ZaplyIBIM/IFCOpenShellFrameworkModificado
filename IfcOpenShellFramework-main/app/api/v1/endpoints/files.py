"""

Código que crea el BluePrint con los EndPoints que se encargan del tratado de archivos

"""

#Imports

#Importamos FLask
from flask import Blueprint, request, make_response, jsonify
#Import de la instancia estática de la librería
from app.api.v1.controller import ifcOpenShellExtObj

#Creamos el BluePrint
endpoints_files = Blueprint('files', __name__)

#EndPoint que abre IFC's (POST)
@endpoints_files.route('/openifcs', methods=['POST'])
def openIfcs():
  data = request.get_json();  
  guidsOpenModels = ifcOpenShellExtObj.open(data);

  return make_response(str(guidsOpenModels),200);

#EndPoint que cierra IFC's (GET)
@endpoints_files.route('/closeifcs/<guidmodels>', methods=['GET'])
def closeIfcs(guidmodels):
  ifcOpenShellExtObj.close(guidmodels);
  return make_response(jsonify(True), 200); 
"""   return json.dumps(True); """