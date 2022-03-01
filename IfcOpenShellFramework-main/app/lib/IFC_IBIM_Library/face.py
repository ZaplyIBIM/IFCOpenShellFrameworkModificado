import numpy as np
from geometer import *
import json

class Face:
  # ctor-initializer
  def __init__(self, tensor, vertices):
    self.tensor = tensor;
    self.vertices = vertices;
  
  @property
  def polygons(self):
    if(not hasattr(self,'_polygons')):
      self._polygons = [];
      for i in range(0,len(self.vertices),3):
        newPolygon = Polygon(self.vertices[i], self.vertices[i+1], self.vertices[i+2]);
        self._polygons.append(newPolygon);
    return self._polygons;

  @property
  def totalArea(self):
    if(not hasattr(self,'_totalArea')):
      self._totalArea = 0.0;
      for poly in self.polygons:
        self._totalArea += poly.area;
    return self._totalArea;

  def addVertices(self, newVertices):
    for vert in newVertices:
      """if(not vert in self.vertices): """
      self.vertices.append(vert);
  
  def toJson(self):
    return {
      "TotalArea" : self.totalArea,
      "Tensor": str(self.tensor)
    }
    """     return json.dumps(self, default= lambda thisObj: thisObj.__dict__) """