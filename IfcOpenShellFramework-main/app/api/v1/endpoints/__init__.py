from flask import Blueprint, request, make_response, jsonify

from .converter import endpoints_converter
from .files import endpoints_files
from .geometry import endpoints_geometry
from .test import endpoints_test

ifcOpenShellFramework = Blueprint('ifcOpenShell', __name__)

ifcOpenShellFramework.register_blueprint(endpoints_converter,  url_prefix='/converter')
ifcOpenShellFramework.register_blueprint(endpoints_files,  url_prefix='/files')
ifcOpenShellFramework.register_blueprint(endpoints_geometry,  url_prefix='/geometry')
ifcOpenShellFramework.register_blueprint(endpoints_test,  url_prefix='/test')

