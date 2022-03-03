
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


class ifcfile:
  # ctor
  def __init__(self, url):
    self.ifcfile = ifcopenshell.open(url);
    self.header = self.ifcFile.header;
    """ possibleName = self.header.file_name.name; """
    url_parsed = urlparse(url);
    self.file_name = os.path.basename(url_parsed.path);  
    self.file_name_without_extension = os.path.splitext(self.file_name)[0];
    self.dir_name = os.path.dirname(url_parsed.path);
    self.url = url;
    settings = geom.settings();
    settings.set(settings.USE_WORLD_COORDS,True);
    self.settings_geom = settings;    
    pass;

  # methods
  def get_geom_of_specific_ifcelement(self, guid_instance):
    ifcinst = self.ifcfile.by_guid(guid_instance);
    if(ifcinst.Representation != None):
      shape = geom.create_shape(self.settingsGeom, ifcinst)
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

      bbox = self.get_bounding_box_of_ifcelement(vertices);
      return {
        "Vertices": vertices,
        "Edges": edges,
        "Faces": faces,
        "BoundingBox": bbox,
        "GlobalId": guid_instance,
        "EntityLabel": ifcinst.id()
      }
  
  def get_boundary_points_for_specific_instance(self, guid_instance):
    geom_inst = self.get_geom_of_specific_ifcelement(guid_instance);
    if(geom_inst != None):
      p = shapely.geometry.Polygon(geom_inst['Vertices']);
      """points = MultiPoint(geomInst['Vertices'])
      triangulating = triangulate(points); """
      geom = p.convex_hull;
      a, b = geom.exterior.coords.xy;
      points_tuple = tuple(list(zip(a,b)));

      return {
        "FileName": self.file_name,
        "GlobalId": guid_instance,
        "Points": points_tuple
        };

  def getAllFaces(self, guid_instance):
    geom_inst = self.get_geom_of_specific_ifcelement(guid_instance);
    if(geom_inst != None):
      faces = [];
      for face in geom_inst['Faces']:
        try:
          point_one_str = geom_inst['Vertices'][face[0]];
          point_two_str = geom_inst['Vertices'][face[1]];
          point_three_str = geom_inst['Vertices'][face[2]];
          point_one = Point(point_one_str[0],point_one_str[1],point_one_str[2]);
          point_two = Point(point_two_str[0],point_two_str[1],point_two_str[2]);
          point_three = Point(point_three_str[0],point_three_str[1],point_three_str[2]);
          points = [point_one, point_two, point_three];
          plane = Plane(point_one, point_two, point_three);
          #basis_matrix = plane.basis_matrix;
          """normals.append({face : basisMatrix}); """
          new_tensor = plane.T.array;
          
          flag = False;
          for face in faces:
            if(np.allclose(face.tensor, new_tensor)):
              face.addVertices(points);
              flag = True;
              break;

          if(not flag):
            faces.append(Face(new_tensor,points));
        except:
          pass;
      
      """  jsonReturn = [];
      for face in faces:
        jsonReturn.append(json.dumps()) """
      
      return json.dumps([face.toJson() for face in faces]);
  
  def transform_civil_file(self):
    all_cartesian_points = self.ifcfile.by_type('IfcCartesianPoint');
    all_points = [cartesian_point.Coordinates for cartesian_point in all_cartesian_points];
    point_off_set_to_subtract = ifcfile.__calculate_min_max_point(all_points, True, 1000);

    intermediate_directory = f'{self.dir_name}\\transformated';
    if(not os.path.exists(intermediate_directory)):
      os.mkdir(intermediate_directory);

    ifcpatch.execute({
      "input": self.url,
      "output": f'{intermediate_directory}\\{self.file_name_without_extension}_toDelete.ifc',
      "recipe": "ResetAbsoluteCoordinates",
      "log": "ifcpatch.log",
      "arguments": [-point_off_set_to_subtract[0],-point_off_set_to_subtract[1],-point_off_set_to_subtract[2]],
    }) 

    intermediate_file_to_delete = ifcopenshell.open(f'{intermediate_directory}\{self.file_name_without_extension}_toDelete.ifc');
    ownerHistory = intermediate_file_to_delete.by_type('IfcOwnerHistory')[0];
    project = intermediate_file_to_delete.by_type('IfcProject')[0];
    building = intermediate_file_to_delete.by_type('IfcBuilding')[0];
    site = intermediate_file_to_delete.create_entity('IfcSite',GlobalId=ifcopenshell.guid.new(), Name='New Site', OwnerHistory = ownerHistory);
    buildingStorey = intermediate_file_to_delete.create_entity('IfcBuildingStorey',GlobalId=ifcopenshell.guid.new(), Name='New Building Storey', OwnerHistory = ownerHistory);
    offsetLocation = point_off_set_to_subtract;
    dirZ = (0.0, 0.0, 1.0);
    dirX = (1.0, 0.0, 0.0);

    local_placement_site = ifcfile.__createIfclocalplacement(intermediate_file_to_delete,offsetLocation, dirZ, dirX);
    local_placement_building_storey = ifcfile.__createIfclocalplacement(intermediate_file_to_delete,(0.0,0.0,0.0), dirZ, dirX);

    building.ObjectPlacement.PlacementRelTo = local_placement_site;
    local_placement_building_storey.PlacementRelTo = building.ObjectPlacement;

    buildingStorey.ObjectPlacement = local_placement_building_storey;
    site.ObjectPlacement = local_placement_site;

    for prod in building.ContainsElements[0].RelatedElements:
      ifcopenshell.api.run("spatial.assign_container", intermediate_file_to_delete, product=prod, relating_structure=buildingStorey);

    ifcopenshell.api.run("aggregate.assign_object", intermediate_file_to_delete, product=site, relating_object=project);
    ifcopenshell.api.run("aggregate.assign_object", intermediate_file_to_delete, product=building, relating_object=site);
    ifcopenshell.api.run("aggregate.assign_object", intermediate_file_to_delete, product=buildingStorey, relating_object=building);

    intermediate_file_to_delete.write(f'{self.dir_name}\\transformated\\{self.file_name}');
    os.remove(f'{intermediate_file_to_delete}\{self.file_name_without_extension}_toDelete.ifc');
    
  def __create_ifc_axis2placement(f, point, dir1, dir2):
    point = f.createIfcCartesianPoint(point)
    dir1 = f.createIfcDirection(dir1)
    dir2 = f.createIfcDirection(dir2)
    axis2placement = f.createIfcAxis2Placement3D(point, dir1, dir2)
    return axis2placement

  # Creates an IfcLocalPlacement from Location, Axis and RefDirection, specified as Python tuples, and relative placement
  def __create_ifc_local_placement(f, point, dir1, dir2, relative_to=None):
      axis2placement = ifcfile.__create_ifc_axis2placement(f, point, dir1, dir2)
      ifc_local_placement2 = f.__create_ifc_local_placement(relative_to, axis2placement)
      return ifc_local_placement2
  
  def __calculate_min_max_point(allPoints, flagMinValue, offset = 0):
    x_coordinates = [point[0] for point in allPoints if(point[0] > offset)];
    possible_min_x = min(x_coordinates) if len(x_coordinates) > 0 else 0.0;
    possible_max_x = max(x_coordinates) if len(x_coordinates) > 0 else 0.0;
    min_x = possible_min_x if possible_min_x != None else 0.0;
    max_x = possible_max_x if possible_max_x != None else 0.0;

    y_coordinates = [point[1] for point in allPoints if(point[1] > offset)]
    possible_min_y = min(y_coordinates) if len(y_coordinates) > 0 else 0.0;
    possible_max_y = max(y_coordinates) if len(y_coordinates) > 0 else 0.0;
    min_y = possible_min_y if possible_min_y != None else 0.0;
    max_y = possible_max_y if possible_max_y != None else 0.0;

    z_coordinates = [point[2] for point in allPoints if(point[2] > offset)];
    possible_min_z = min(z_coordinates) if len(z_coordinates) > 0 else 0.0;
    possible_max_z = max(z_coordinates) if len(z_coordinates) > 0 else 0.0;
    min_z = possible_min_z if possible_min_z != None else 0.0;
    max_z = possible_max_z if possible_max_z != None else 0.0;

    return (min_x, min_y, min_z) if flagMinValue else (max_x, max_y, max_z);

  def get_bounding_box_of_ifcelement(self, vertices):
    min_point = ifcfile.__calculate_min_max_point(vertices,True);
    max_point = ifcfile.__calculate_min_max_point(vertices,False);
    return [min_point, max_point];

  """   def staticMethod():
    return "StaticMethod"; """
  
