"""

Clase general que se encarga de proporcionar acceso a los diferentes métodos de la librería

"""

from app.lib.IFC_IBIM_Library.geometry import Geometry
from .ifcFiles import IfcFiles


class IfcOpenShellGeneric(Geometry):
  # ctor
  def __init__(self):
    pass;

  # methods 
  def open(self, dataRequest): 
    ifcExtended = IfcFiles(dataRequest["pathOfFiles"], dataRequest["guidModels"]);
    return ifcExtended.guidFiles; 

  def close(self, guidModels): 
    IfcFiles.closeIfcs(guidModels);

  def transformCivilIfc(self,guidModels, bodyJson):
    modelNames = bodyJson['models'];
    for modelName in modelNames:
      fileSearch = IfcFiles.getSpecificFile(guidModels, modelName);
      if(fileSearch != None):
        fileSearch.transformCivilFile();          
    return 'Archivos procesados correctamente';
  
# explicit function       
def method(): 
  print("Explicit function");
