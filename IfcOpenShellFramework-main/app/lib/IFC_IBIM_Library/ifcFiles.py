import glob
import uuid
from .ifcFile import IfcFile


class IfcFiles(list):
  #static variable
  ifcModelsLoaded = [];

  #ctor
  def __new__(cls, urlFolder, guidModels):
    isAlreadyOpen = next(filter(lambda ifcModels: ifcModels.url == urlFolder & ifcModels.guidFiles == guidModels, IfcFiles.ifcModelsLoaded), None);
    if  isAlreadyOpen != None:
      return isAlreadyOpen;
    else:
      return super(IfcFiles, cls).__new__(cls);

  # ctor-initializer
  def __init__(self,urlFolder, guidModels):
    if not hasattr(self,'guidFiles'):
      allIfcFilesPaths = glob.glob(f'{urlFolder}/*.ifc');
      for ifcFilePath in allIfcFilesPaths:
        ifcFileExtended = IfcFile(ifcFilePath);
        self.append(ifcFileExtended);
      self.guidFiles = guidModels;
      self.url = urlFolder;
      IfcFiles.ifcModelsLoaded.append(self);

  # methods 
  def closeIfcs(guidModels): 
    IfcFiles.ifcModelsLoaded = list(filter(lambda ifcModels: str(ifcModels.guidFiles) != guidModels, IfcFiles.ifcModelsLoaded))

  def getSpecificFile(guidModels, fileName):
    files = next(filter(lambda ifcModels: str(ifcModels.guidFiles) == guidModels, IfcFiles.ifcModelsLoaded), None);
    if  files != None:
      return next(filter(lambda ifcFile: ifcFile.fileName == fileName, files), None);

  