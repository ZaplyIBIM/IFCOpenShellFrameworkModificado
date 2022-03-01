from flask import Blueprint, request, make_response, jsonify

from app.api.v1.controller import ifcOpenShellExtObj

endpoints_files = Blueprint('files', __name__)


@endpoints_files.route('/openifcs', methods=['POST'])
def openIfcs():
  data = request.get_json();  
  guidsOpenModels = ifcOpenShellExtObj.open(data);

  return make_response(str(guidsOpenModels),200);

@endpoints_files.route('/closeifcs/<guidmodels>', methods=['GET'])
def closeIfcs(guidmodels):
  ifcOpenShellExtObj.close(guidmodels);
  return make_response(jsonify(True), 200); 
"""   return json.dumps(True); """