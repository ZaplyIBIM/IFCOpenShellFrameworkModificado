

from flask import Blueprint, request, make_response, jsonify

from app.api.v1.controller import ifcOpenShellExtObj

endpoints_converter = Blueprint('converter', __name__)



@endpoints_converter.route('/transformcivilifc/<guidmodels>', methods=['POST'])
def transformCivilIfc(guidmodels):
  data = request.get_json();  
  results = ifcOpenShellExtObj.transformCivilIfc(guidmodels,data);
  return make_response(results,200);