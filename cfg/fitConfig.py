import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

from locations import locations
from centralConfig import versions

class fitConfig:               
                useMC = True
                mcdatasets = ["TT_Powheg"]
                dataset = ["MergedData"]
                
                dataSetPath = locations.dataSetPath
                task = versions.cuts+"DileptonFinalTrees"
                flag = locations.dataSetPath.split("/")[-2]
                
                def __init__(self,region="SignalInclusive",runName = "Full2012"):
                        sys.path.append(pathes.basePath)
                        
                        self.dataSetPath = locations.dataSetPath
                        
                        self.flag = locations.dataSetPath.split("/")[-2]
                        
                        self.task = versions.cuts+"DileptonFinalTrees"
                        
                        from defs import runRanges
                        if not runName in dir(runRanges):
                                print "invalid run name, exiting"
                                sys.exit()
                        else:   
                                self.runRange =  getattr(runRanges,runName)
                        
                        from defs import Regions
                        if not region in dir(Regions):
                                print "invalid region, exiting"
                                sys.exit()
                        else:   
                                self.selection = getattr(Regions,region)
                             
