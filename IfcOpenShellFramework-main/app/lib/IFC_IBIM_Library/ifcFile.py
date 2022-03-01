
"""

Clase File que se encarga del tratado de archivos IFC

"""


import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util
import ifcopenshell.util.element
import ifcopenshell.util.placement
import os
from urllib.parse import urlparse
from shapely.ops import triangulate
import shapely.geometry
from geometer import *
import numpy as np
from .face import Face
import ifcopenshell.geom as geom
import ifcpatch
import ifcopenshell.template
import json


class IfcFile:
  # ctor
  def __init__(self, url):
    self.ifcFile = ifcopenshell.open(url);
    self.header = self.ifcFile.header;
    """ possibleName = self.header.file_name.name; """
    urlParsed = urlparse(url);
    self.fileName = os.path.basename(urlParsed.path);  
    self.fileNameWithoutExtension = os.path.splitext(self.fileName)[0];
    self.dirName = os.path.dirname(urlParsed.path);
    self.url = url;
    settings = geom.settings();
    settings.set(settings.USE_WORLD_COORDS,True);
    self.settingsGeom = settings;    
    pass;

  # methods
  def getGeomOfSpecificIfcElement(self, guidInstance):
    ifcInst = self.ifcFile.by_guid(guidInstance);
    if(ifcInst.Representation != None):
      shape = geom.create_shape(self.settingsGeom, ifcInst)
      # ios stands for IfcOpenShell
      ios_vertices = shape.geometry.verts
      ios_edges = shape.geometry.edges
      ios_faces = shape.geometry.faces

      # Let's parse it and prepare it
      vertices = [
          ios_vertices[i : i + 3] for i in range(0, len(ios_vertices), 3)
      ]
      edges = [ios_edges[i : i + 2] for i in range(0, len(ios_edges), 2)]
      faces = [tuple(ios_faces[i : i + 3]) for i in range(0, len(ios_faces), 3)]

      bbox = self.getBoundingBoxOfIfcElement(vertices);
      return {
        "Vertices": vertices,
        "Edges": edges,
        "Faces": faces,
        "BoundingBox": bbox,
        "GlobalId": guidInstance,
        "EntityLabel": ifcInst.id()
      }
  
  def getBoundaryPointsForSpecificInstance(self, guidInstance):
    geomInst = self.getGeomOfSpecificIfcElement(guidInstance);
    if(geomInst != None):
      p = shapely.geometry.Polygon(geomInst['Vertices']);
      """points = MultiPoint(geomInst['Vertices'])
      triangulating = triangulate(points); """
      geom = p.convex_hull;
      a, b = geom.exterior.coords.xy;
      points_tuple = tuple(list(zip(a,b)));

      return {
        "FileName": self.fileName,
        "GlobalId": guidInstance,
        "Points": points_tuple
        };

  def getAllFaces(self, guidInstance):
    geomInst = self.getGeomOfSpecificIfcElement(guidInstance);
    if(geomInst != None):
      faces = [];
      for face in geomInst['Faces']:
        try:
          pointOneStr = geomInst['Vertices'][face[0]];
          pointTwoStr = geomInst['Vertices'][face[1]];
          pointThreeStr = geomInst['Vertices'][face[2]];
          pointOne = Point(pointOneStr[0],pointOneStr[1],pointOneStr[2]);
          pointTwo = Point(pointTwoStr[0],pointTwoStr[1],pointTwoStr[2]);
          pointThree = Point(pointThreeStr[0],pointThreeStr[1],pointThreeStr[2]);
          points = [pointOne, pointTwo, pointThree];
          plane = Plane(pointOne, pointTwo, pointThree);
          basisMatrix = plane.basis_matrix;
          """normals.append({face : basisMatrix}); """
          newTensor = plane.T.array;
          
          flag = False;
          for face in faces:
            if(np.allclose(face.tensor, newTensor)):
              face.addVertices(points);
              flag = True;
              break;

          if(not flag):
            faces.append(Face(newTensor,points));
        except:
          pass;
      
      """  jsonReturn = [];
      for face in faces:
        jsonReturn.append(json.dumps()) """
      
      return json.dumps([face.toJson() for face in faces]);
  
  def transformCivilFile(self):
    allCartesianPoints = self.ifcFile.by_type('IfcCartesianPoint');
    allPoints = [cartesianPoint.Coordinates for cartesianPoint in allCartesianPoints];
    pointOffsetToSubtract = IfcFile.__calculateMinMaxPoint(allPoints, True, 1000);

    intermediateDirectory = f'{self.dirName}\\transformated';
    if(not os.path.exists(intermediateDirectory)):
      os.mkdir(intermediateDirectory);

    ifcpatch.execute({
      "input": self.url,
      "output": f'{intermediateDirectory}\\{self.fileNameWithoutExtension}_toDelete.ifc',
      "recipe": "ResetAbsoluteCoordinates",
      "log": "ifcpatch.log",
      "arguments": [-pointOffsetToSubtract[0],-pointOffsetToSubtract[1],-pointOffsetToSubtract[2]],
    }) 

    intermediateFileToDelete = ifcopenshell.open(f'{intermediateDirectory}\{self.fileNameWithoutExtension}_toDelete.ifc');
    ownerHistory = intermediateFileToDelete.by_type('IfcOwnerHistory')[0];
    project = intermediateFileToDelete.by_type('IfcProject')[0];
    building = intermediateFileToDelete.by_type('IfcBuilding')[0];
    site = intermediateFileToDelete.create_entity('IfcSite',GlobalId=ifcopenshell.guid.new(), Name='New Site', OwnerHistory = ownerHistory);
    buildingStorey = intermediateFileToDelete.create_entity('IfcBuildingStorey',GlobalId=ifcopenshell.guid.new(), Name='New Building Storey', OwnerHistory = ownerHistory);
    offsetLocation = pointOffsetToSubtract;
    dirZ = (0.0, 0.0, 1.0);
    dirX = (1.0, 0.0, 0.0);

    localPlacementSite = IfcFile.__createIfclocalplacement(intermediateFileToDelete,offsetLocation, dirZ, dirX);
    localPlacementBuildingStorey = IfcFile.__createIfclocalplacement(intermediateFileToDelete,(0.0,0.0,0.0), dirZ, dirX);

    building.ObjectPlacement.PlacementRelTo = localPlacementSite;
    localPlacementBuildingStorey.PlacementRelTo = building.ObjectPlacement;

    buildingStorey.ObjectPlacement = localPlacementBuildingStorey;
    site.ObjectPlacement = localPlacementSite;

    for prod in building.ContainsElements[0].RelatedElements:
      ifcopenshell.api.run("spatial.assign_container", intermediateFileToDelete, product=prod, relating_structure=buildingStorey);

    ifcopenshell.api.run("aggregate.assign_object", intermediateFileToDelete, product=site, relating_object=project);
    ifcopenshell.api.run("aggregate.assign_object", intermediateFileToDelete, product=building, relating_object=site);
    ifcopenshell.api.run("aggregate.assign_object", intermediateFileToDelete, product=buildingStorey, relating_object=building);

    intermediateFileToDelete.write(f'{self.dirName}\\transformated\\{self.fileName}');
    os.remove(f'{intermediateDirectory}\{self.fileNameWithoutExtension}_toDelete.ifc');
    
  def __createIfcaxis2placement(f, point, dir1, dir2):
    point = f.createIfcCartesianPoint(point)
    dir1 = f.createIfcDirection(dir1)
    dir2 = f.createIfcDirection(dir2)
    axis2placement = f.createIfcAxis2Placement3D(point, dir1, dir2)
    return axis2placement

  # Creates an IfcLocalPlacement from Location, Axis and RefDirection, specified as Python tuples, and relative placement
  def __createIfclocalplacement(f, point, dir1, dir2, relative_to=None):
      axis2placement = IfcFile.__createIfcaxis2placement(f, point, dir1, dir2)
      ifclocalplacement2 = f.createIfcLocalPlacement(relative_to, axis2placement)
      return ifclocalplacement2
  
  def __calculateMinMaxPoint(allPoints, flagMinValue, offset = 0):
    xCoordinates = [point[0] for point in allPoints if(point[0] > offset)];
    possibleMinX = min(xCoordinates) if len(xCoordinates) > 0 else 0.0;
    possibleMaxX = max(xCoordinates) if len(xCoordinates) > 0 else 0.0;
    minX = possibleMinX if possibleMinX != None else 0.0;
    maxX = possibleMaxX if possibleMaxX != None else 0.0;

    yCoordinates = [point[1] for point in allPoints if(point[1] > offset)]
    possibleMinY = min(yCoordinates) if len(yCoordinates) > 0 else 0.0;
    possibleMaxY = max(yCoordinates) if len(yCoordinates) > 0 else 0.0;
    minY = possibleMinY if possibleMinY != None else 0.0;
    maxY = possibleMaxY if possibleMaxY != None else 0.0;

    zCoordinates = [point[2] for point in allPoints if(point[2] > offset)];
    possibleMinZ = min(zCoordinates) if len(zCoordinates) > 0 else 0.0;
    possibleMaxZ = max(zCoordinates) if len(zCoordinates) > 0 else 0.0;
    minZ = possibleMinZ if possibleMinZ != None else 0.0;
    maxZ = possibleMaxZ if possibleMaxZ != None else 0.0;

    return (minX, minY, minZ) if flagMinValue else (maxX, maxY, maxZ);

  def getBoundingBoxOfIfcElement(self, vertices):
    minPoint = IfcFile.__calculateMinMaxPoint(vertices,True);
    maxPoint = IfcFile.__calculateMinMaxPoint(vertices,False);
    return [minPoint, maxPoint];

  """   def staticMethod():
    return "StaticMethod"; """
  