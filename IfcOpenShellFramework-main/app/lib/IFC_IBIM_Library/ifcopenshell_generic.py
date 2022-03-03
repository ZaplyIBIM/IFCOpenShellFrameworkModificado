"""

Clase general que se encarga de proporcionar acceso a los diferentes métodos de la librería

"""

from app.lib.IFC_IBIM_Library.geometry import Geometry
from .ifcfiles import ifcfiles


class ifcopenshell_generic(Geometry):
  # ctor
  def __init__(self):
    pass;

  # methods 
  def open(self, data_request): 
    ifcextended = ifcfiles(data_request["pathOfFiles"], data_request["guidModels"]);
    return ifcextended.guid_files; 

  def close(self, guid_models): 
    ifcfiles.close_ifcs(guid_models);

  def transform_civil_ifc(self,guid_models, bodyJson):
    model_names = bodyJson['models'];
    for model_name in model_names:
      file_search = ifcfiles.get_specific_file(guid_models, model_name);
      if(file_search != None):
        file_search.transform_civil_file();          
    return 'Archivos procesados correctamente';
  
# explicit function       
def method(): 
  print("Explicit function");
