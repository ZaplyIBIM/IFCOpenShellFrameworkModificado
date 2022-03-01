

from flask import Blueprint, request, make_response, jsonify

endpoints_test = Blueprint('test', __name__)


@endpoints_test.route('/helloworld', methods=['GET'])
def helloWorld():
  return make_response("hello World", 200);