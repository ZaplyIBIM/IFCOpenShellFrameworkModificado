
"""

Clase geometry que se encarga del tratado de geometría básica

"""

from .ifcFiles import IfcFiles
import json


class Geometry:
  def getBoundaryGeomInstance(self,guidModels, bodyJson):
    results = [];
    for model in bodyJson:
      fileName = model['ifc'];
      guids = model['guids'];

      fileSearch = IfcFiles.getSpecificFile(guidModels, fileName);
      for guid in guids:
        results.append(fileSearch.getBoundaryPointsForSpecificInstance(guid));
    return results;

  def getBasicGeomInstance(self,guidModels, bodyJson):
    fileName = bodyJson['model'];
    guid = bodyJson['guid'];

    fileSearch = IfcFiles.getSpecificFile(guidModels, fileName);
    return json.dumps(fileSearch.getGeomOfSpecificIfcElement(guid));
  
  def getAllFaces(self,guidModels, bodyJson):
    results = [];
    for model in bodyJson:
      fileName = model['ifc'];
      guids = model['guids'];

      fileSearch = IfcFiles.getSpecificFile(guidModels, fileName);
      if(fileSearch != None):
        for guid in guids:
          results.append(fileSearch.getAllFaces(guid));
    return json.dumps(results);