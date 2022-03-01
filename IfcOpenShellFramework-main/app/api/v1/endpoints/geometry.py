from flask import Blueprint, request, make_response, jsonify

from app.api.v1.controller import ifcOpenShellExtObj

endpoints_geometry = Blueprint('geometry', __name__)


@endpoints_geometry.route('/boundarygeominstance/<guidmodels>', methods=['POST'])
def boundarygeominstance(guidmodels):
  data = request.get_json();  
  results = ifcOpenShellExtObj.getBoundaryGeomInstance(guidmodels,data);
  return make_response(str(results),200);

@endpoints_geometry.route('/basicgeominstance/<guidmodels>', methods=['POST'])
def basicgeominstance(guidmodels):
  data = request.get_json();  
  results = ifcOpenShellExtObj.getBasicGeomInstance(guidmodels,data);
  return make_response(str(results),200);

@endpoints_geometry.route('/allfaces/<guidmodels>', methods=['POST'])
def getAllFaces(guidmodels):
  data = request.get_json();  
  results = ifcOpenShellExtObj.getAllFaces(guidmodels,data);
  return make_response(str(results),200);