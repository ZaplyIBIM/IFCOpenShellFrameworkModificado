
"""

Clase geometry que se encarga del tratado de geometría básica

"""

from .ifcfiles import ifcfiles
import json


class Geometry:
  def get_boundary_geom_instance(self,guid_models, body_json):
    results = [];
    for model in body_json:
      file_name = model['ifc'];
      guids = model['guids'];

      file_search = ifcfiles.get_specific_file(guid_models, file_name);
      for guid in guids: 
        results.append(file_search.get_boundary_points_for_specific_instance(guid));
    return results;

  def get_basic_geom_instance(self,guid_models, body_json):
    file_name = body_json['model'];
    guid = body_json['guid'];

    file_search = ifcfiles.get_specific_file(guid_models, file_name);
    return json.dumps(file_search.get_geom_of_specific_ifcelement(guid));
  
  def get_all_faces(self,guid_models, body_json):
    results = [];
    for model in body_json:
      file_name = model['ifc'];
      guids = model['guids'];

      file_search = ifcfiles.getSpecificFile(guid_models, file_name);
      if(file_search != None):
        for guid in guids:
          results.append(file_search.get_all_faces(guid));
    return json.dumps(results);