#!/usr/bin/env python

import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

from messageLogger import messageLogger as log

import ROOT
from ROOT import TFile, TH1F

import os, ConfigParser
from math import sqrt
import datetime

from defs import Backgrounds

from locations import locations
config_path = locations.masterListPath
from centralConfig import versions

from ConfigParser import ConfigParser
config = ConfigParser()
config.read("%s/%s"%(config_path,versions.masterListForMC))

ROOT.gROOT.ProcessLine(\
                                               "struct MyDileptonTreeFormat{\
                                                     Double_t weight;\
                                                     Double_t met_Edge;\
                                                     Double_t sum_mlb_Edge;\
                                                     Double_t lepsDPhi_Edge;\
                                                     Double_t lepsZPt_Edge;\
                                                    };")

def getMCTrees(theConfig):
    treePathOF = "/EMuDileptonTree"
    treePathEE = "/EEDileptonTree"
    treePathMM = "/MuMuDileptonTree"

    treesMCOF = ROOT.TList()
    treesMCEE = ROOT.TList()
    treesMCMM = ROOT.TList()

    
    cut = theConfig.selection.cut
    
    for dataset in theConfig.mcdatasets:
        scale = 0.0

        # dynamic scaling
        jobs = getattr(Backgrounds, dataset).subprocesses
        if (len(jobs) > 1):
                log.logDebug("Scaling and adding more than one job: %s" % (jobs))
        for job in jobs:
            treeMCOFraw = getTreeFromJob(theConfig.dataSetPath, theConfig.flag, theConfig.task, job, theConfig.runRange, treePathOF, cut=cut)
            treeMCEEraw = getTreeFromJob(theConfig.dataSetPath, theConfig.flag, theConfig.task, job, theConfig.runRange, treePathEE, cut=cut)
            treeMCMMraw = getTreeFromJob(theConfig.dataSetPath, theConfig.flag, theConfig.task, job, theConfig.runRange, treePathMM, cut=cut)
            
            dynXsection = eval(config.get(job,"crosssection"))
            from helpers import totalNumberOfGeneratedEvents
            dynNTotal = totalNumberOfGeneratedEvents(theConfig.dataSetPath)[job]
            
            dynScale = dynXsection * theConfig.runRange.lumi / dynNTotal
            #dynScale = 1 # No scaling to xsec
            
            # convert trees
            treesMCOF.Add(convertDileptonTree(treeMCOFraw, weight=dynScale))
            treeMCOFraw = None
            treesMCEE.Add(convertDileptonTree(treeMCEEraw, weight=dynScale))
            treeMCEEraw = None
            treesMCMM.Add(convertDileptonTree(treeMCMMraw, weight=dynScale))
            treeMCMMraw = None
                    
    treeMCOFtotal = ROOT.TTree.MergeTrees(treesMCOF)
    treeMCEEtotal = ROOT.TTree.MergeTrees(treesMCEE)
    treeMCMMtotal = ROOT.TTree.MergeTrees(treesMCMM)

    return (treeMCOFtotal, treeMCEEtotal, treeMCMMtotal)

def convertDileptonTree(tree, nMax= -1, weight=1.0, puReweighting=False):
    # TODO: make selection more efficient
    log.logDebug("Converting DileptonTree")
    
    from ROOT import MyDileptonTreeFormat
    data = MyDileptonTreeFormat()
    newTree = ROOT.TTree("treeInvM", "Dilepton Tree")
    newTree.SetDirectory(0)
    newTree.Branch("met_Edge", ROOT.AddressOf(data, "met_Edge"), "met_Edge/D")
    newTree.Branch("sum_mlb_Edge", ROOT.AddressOf(data, "sum_mlb_Edge"), "sum_mlb_Edge/D")
    newTree.Branch("lepsDPhi_Edge", ROOT.AddressOf(data, "lepsDPhi_Edge"), "lepsDPhi_Edge/D")
    newTree.Branch("lepsZPt_Edge", ROOT.AddressOf(data, "lepsZPt_Edge"), "lepsZPt_Edge/D")
    newTree.Branch("weight", ROOT.AddressOf(data, "weight"), "weight/D")
    
    
    
    # only part of tree?
    iMax = tree.GetEntries()
    if (nMax != -1):
            iMax = min(nMax, iMax)

    # Fill tree
    for i in xrange(int(iMax)):
        if (tree.GetEntry(i) > 0):
            data.met_Edge = tree.met
            data.lepsZPt_Edge = tree.p4.Pt()
            data.lepsDPhi_Edge = abs(tree.deltaPhi)
            data.sum_mlb_Edge = tree.sumMlb
            if (puReweighting):
                data.weight = tree.weight * weight
            else:
                data.weight = 1 * weight # no PU reweighting
            newTree.Fill()

    return newTree.CopyTree("")


def getTreeFromDataset(dataSetPath, flag, task, dataset, runRange, treePath, cut=""):
    jobList = dataset
    log.logDebug("Getting '%s' from joblist %s" % (treePath, str(jobList)))
    
    if (len(jobList) > 1):
        log.logError("Adding trees for multiple jobs without scaling!")
    
    cut += runRange.runCut
    if runRange.label != "Run2016_12_9fb":
        cut += " && (acos((vMet.Px()*jet1.Px()+vMet.Py()*jet1.Py())/vMet.Pt()/jet1.Pt()) > 0.4) && (acos((vMet.Px()*jet2.Px()+vMet.Py()*jet2.Py())/vMet.Pt()/jet2.Pt()) > 0.4)"
    
    tree = ROOT.TChain("%s%s" % (task, treePath))
    for job in jobList:
        fileName = "%s/%s.%s.%s.root" % (dataSetPath, flag, "processed", job)

        if (os.path.exists(fileName)):
            tree.Add(fileName)
        else:
            log.logWarning("File not found: %s" % fileName)

    if (cut != ""):
        log.logDebug("Cutting tree down to: %s" % cut)
        tree = tree.CopyTree(cut)
        #log.logError("Tree size: %d entries" % (tree.GetEntries()))

    if (tree != None):
        tree.SetDirectory(0)
    else:
        log.logError("Tree invalid: %s -%s - %s - %s" % (flag, task, dataset, treePath))
    return tree


def getTreeFromJob(dataSetPath, flag, task, job, runRange, treePath, cut=""):
    tree = ROOT.TChain("%s%s" % (task, treePath))
    fileName = "%s%s.%s.%s.root" % (dataSetPath, flag, "processed", job)
    if (os.path.exists(fileName)):
        tree.Add(fileName)
    else:
        log.logWarning("File not found: %s" % fileName)
    
    cut += runRange.runCut
    if runRange.label != "Run2016_12_9fb":
        cut += " && (acos((vMet.Px()*jet1.Px()+vMet.Py()*jet1.Py())/vMet.Pt()/jet1.Pt()) > 0.4) && (acos((vMet.Px()*jet2.Px()+vMet.Py()*jet2.Py())/vMet.Pt()/jet2.Pt()) > 0.4)"
        
    if (cut != ""):
        log.logDebug("Cutting tree down to: %s" % cut)
        tree = tree.CopyTree(cut)
        #log.logError("Tree size: %d entries" % (tree.GetEntries()))

    if (tree != None):
        tree.SetDirectory(0)
    else:
        log.logError("Tree invalid: %s -%s - %s - %s" % (flag, task, job, treePath))
    

    return tree


