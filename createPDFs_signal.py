import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
from ROOT import gROOT, gStyle
from ROOT import RooFit
from setTDRStyle import setTDRStyle

from plotTemplate import plotTemplate

from messageLogger import messageLogger as log
from treeGetter import getTreeFromDataset, getTreeFromJob, convertDileptonTree, getMCTrees
import math
import argparse 
import random




def prepareDatasets(summlb, met, ptll, deltaphi, weight, signalOF, signalEE, signalMM, theConfig):
    vars = ROOT.RooArgSet(summlb, met, ptll, deltaphi, weight)
    
    #mc
    signal_tmpEE = ROOT.RooDataSet("signal_tmpEE", "signal_tmpEE", vars, RooFit.Import(signalEE), RooFit.WeightVar("weight"))
    signal_tmpSF = ROOT.RooDataSet("signal_tmpSF", "signal_tmpSF", vars, RooFit.Import(signalMM), RooFit.WeightVar("weight"))
    signal_tmpSF.append(signal_tmpEE)
    signal_tmpOF = ROOT.RooDataSet("signal_tmpOF", "signal_tmpOF", vars, RooFit.Import(signalOF), RooFit.WeightVar("weight"))
    

    signal_SF = ROOT.RooDataSet("signalSF", "Dataset with invariant mass of SFOS lepton pairs",
                               vars, RooFit.Import(signal_tmpSF), RooFit.WeightVar("weight"))
    signal_OF = ROOT.RooDataSet("signalOF", "Dataset with invariant mass of OFOS lepton pairs",
                               vars, RooFit.Import(signal_tmpOF), RooFit.WeightVar("weight"))

    
    result = {"signal_OF" : signal_OF, "signal_SF" : signal_SF}     
        
    return result   

#save objects from python garbage collection
allObj = []

def getFitPDF(w, vari, dilepton, isMc):
    if isMc:
        if dilepton == "OF":
            nameSuffix = "MC"
        else:
            nameSuffix = "MC_SF"
    else:
        nameSuffix = "DA"
    
    if   vari == "met_Edge":
        pdfName = "met_analyticalPDF_"
    elif vari == "lepsDPhi_Edge":
        pdfName = "ldp_analyticalPDF_"
    elif vari == "lepsZPt_Edge":
        pdfName = "zpt_analyticalPDF_"
    elif vari == "sum_mlb_Edge":
        pdfName = "mlb_analyticalPDF_"
        
    pdfName += nameSuffix
    
    shapes = ROOT.RooArgList()
    yields = ROOT.RooArgList()
    
    if vari == "met_Edge":
        a = ROOT.RooRealVar("met_c0_%s"%(nameSuffix), "a",-0.03, -1, 0)
        b = ROOT.RooRealVar("met_c1_%s"%(nameSuffix), "b",-0.01, -0.05, -0.005)
        exp1 = ROOT.RooExponential("exponential1%s"%(nameSuffix), "exponential1", w.var(vari), a)
        exp2 = ROOT.RooExponential("exponential2%s"%(nameSuffix), "exponential2", w.var(vari), b)
        yield1 = ROOT.RooRealVar    ("met_n1_%s"%(nameSuffix), "expoyield1",2400,0,10000)
        yield2 = ROOT.RooRealVar    ("met_n2_%s"%(nameSuffix), "expoyield2",1200,0,10000)
        shapes.add(exp1)
        yields.add(yield1)
        shapes.add(exp2)
        yields.add(yield2)
        allObj.extend([a,b, exp1, exp2, yield1, yield2, shapes, yields]) # save from python garbage collection
        fitFunc = ROOT.RooAddPdf(pdfName, pdfName, shapes, yields)
        
    elif vari == "lepsDPhi_Edge":
        a = ROOT.RooRealVar("ldp_a0_%s"%(nameSuffix), "a", 0.1, 0, 2)
        b = ROOT.RooRealVar("ldp_a2_%s"%(nameSuffix), "b", 0.3, 0, 2)
        #pol = ROOT.RooPolynomial(pdfName, "polynomial", w.var(vari), ROOT.RooArgList(a, b))
        pol = ROOT.RooGenericPdf(pdfName, "polynomial", "%s*(lepsDPhi_Edge)*(lepsDPhi_Edge) + %s"%("ldp_a0_%s"%(nameSuffix), "ldp_a2_%s"%(nameSuffix)), ROOT.RooArgList(w.var(vari), a, b))
        allObj.extend([a,b, pol]) # save from python garbage collection
        fitFunc = pol
        
    elif vari == "sum_mlb_Edge":
        a = ROOT.RooRealVar("mlb_peak_%s"%(nameSuffix) , "peak",  500, 400, 600)
        b = ROOT.RooRealVar("mlb_sigma_%s"%(nameSuffix), "sigma", 100, 90,200)
        c = ROOT.RooRealVar("mlb_alpha_%s"%(nameSuffix), "alpha", -1, -4.5, -0.5)
        d = ROOT.RooRealVar("mlb_n_%s"%(nameSuffix)    , "n",     1,0, 2)
        cb = ROOT.RooCBShape(pdfName, "crystalball", w.var(vari), a,b,c,d)
        allObj.extend([a,b,c,d,cb]) # save from python garbage collection
        fitFunc = cb
        
    elif vari == "lepsZPt_Edge":
        a = ROOT.RooRealVar("zpt_peak_%s"%(nameSuffix) , "peak", 150, 100, 200)
        b = ROOT.RooRealVar("zpt_sigma_%s"%(nameSuffix), "sigma", 80, 40, 150)
        c = ROOT.RooRealVar("zpt_alpha_%s"%(nameSuffix), "alpha", -1, -3.5, 0)
        d = ROOT.RooRealVar("zpt_n_%s"%(nameSuffix)    , "n", 22,5, 100)
        
        cb = ROOT.RooCBShape(pdfName, "crystalball", w.var(vari), a,b,c,d)
        
        allObj.extend([a,b,c,d,cb]) # save from python garbage collection
        
        fitFunc = cb
        
    else:
        print "Error! No known variable used for fit."
        sys.exit()

    return fitFunc


def fitVariables(useExistingDataSet, region, puReweighting, verbose, sigs, path):
    if not verbose:
        ROOT.RooMsgService.instance().setGlobalKillBelow(RooFit.WARNING)  
        ROOT.RooMsgService.instance().setSilentMode(ROOT.kTRUE)
    
    from fitConfig import fitConfig
    theConfig = fitConfig(region,"Run2016_36fb")
    theConfig.puReweighting = puReweighting
    
    if puReweighting:
        puString = ""
    else:
        puString = "_noWeights"
    
    if not useExistingDataSet:
        #Read in and convert dilepton trees of signal
        (sgOF, sgEE, sgMM) = getMCTrees(theConfig, signals=sigs, signalPath=path)
        
        
        #Initialize RooVars and prepare trees as datasets
        weight = ROOT.RooRealVar("weight","weight",1.,-100.,10.)
        ptll = ROOT.RooRealVar("lepsZPt_Edge","ptll",1,0,1000)
        met  = ROOT.RooRealVar("met_Edge", "met", 151, 150, 1000)
        deltaPhi = ROOT.RooRealVar("lepsDPhi_Edge", "deltaPhi", 1, 0, 3.14)
        sumMlb = ROOT.RooRealVar("sum_mlb_Edge", "sumMlb", 1, 0, 3000)
        
        print "Preparing trees as RooDataSets"
        datasets = prepareDatasets(sumMlb, met, ptll, deltaPhi, weight, sgOF, sgEE, sgMM, theConfig)
        
        #Create workspace and import datasets and variables
        w = ROOT.RooWorkspace("work", ROOT.kTRUE)
        w.factory("lepsZPt_Edge[150,0,1000]")
        w.factory("met_Edge[325,150,1000]")
        w.factory("lepsDPhi_Edge[1,0,3.14]")
        w.factory("sum_mlb_Edge[1,0,3000]")
        w.factory("weight[1,-100,10.]")
        
        print "Importing datasets into workspace"
        getattr(w, 'import')(datasets["signal_OF"])
        getattr(w, 'import')(datasets["signal_SF"])
        
        w.writeToFile("workspaces/saveDataSet_signal_%s%s.root"%(theConfig.flag,puString))
    else:
        print "Reading out existing workspace workspaces/saveDataSet_signal_%s%s.root"%(theConfig.flag, puString)
        f = ROOT.TFile("workspaces/saveDataSet_signal_%s%s.root"%(theConfig.flag, puString))
        w = f.Get("work")
        w.Print()
    
    #For normalization of datasets in plot

    fits =  [
            ("lepsZPt_Edge", ";p_{T}^{ll} [GeV]; Events / (6 GeV)",     (50, 0, 300)), 
            ("sum_mlb_Edge", ";#Sigma m_{lb} [GeV]; Events / (10 GeV)", (100, 0, 1000)),
            ("met_Edge",     ";met [GeV]; Events / (3.5 GeV)",          (100, 150, 500)), 
            ("lepsDPhi_Edge",";|#Delta#phi_{ll}|; Events / (0.0314)",   (100,0,3.14))
            ]
    
    ws = ROOT.RooWorkspace("w", ROOT.kTRUE)
    
    print "Starting fits"
    ttof = float(w.data("signalOF").sumEntries())
    ttsf = float(w.data("signalSF").sumEntries()) 

    for vari, title, binning in fits:

        #mcFitOF = getFitPDF(w, vari, "OF", True )
        mcFitSF = getFitPDF(w, vari, "SF", True )
        
        template = plotTemplate()
        template.plotData = True
        
        frame = w.var(vari).frame(RooFit.Title(title), RooFit.Range(binning[1], binning[2]))
   
        ROOT.RooAbsData.plotOn(w.data("signalOF"), frame, RooFit.Name("signalOF_P"), RooFit.Binning(*binning), RooFit.LineColor(ROOT.kRed),  RooFit.MarkerColor(ROOT.kRed),  RooFit.XErrorSize(0), RooFit.MarkerStyle(8), RooFit.MarkerSize(0.8), )
        #mcFitOF.fitTo(w.data("signalOF"), RooFit.Range(binning[1], binning[2]), RooFit.SumW2Error(ROOT.kTRUE))
        #mcFitOF.plotOn(frame, RooFit.Name("signalOF_L"), RooFit.LineColor(ROOT.kRed))
        
        ROOT.RooAbsData.plotOn(w.data("signalSF"), frame, RooFit.Name("signalSF_P"), RooFit.Binning(*binning), RooFit.LineColor(ROOT.kBlue), RooFit.MarkerColor(ROOT.kBlue), RooFit.XErrorSize(0), RooFit.MarkerStyle(8), RooFit.MarkerSize(0.8), RooFit.Rescale(ttof/ttsf))
        mcFitSF.fitTo(w.data("signalSF"), RooFit.Range(binning[1], binning[2]), RooFit.SumW2Error(ROOT.kTRUE))
        mcFitSF.plotOn(frame, RooFit.Name("signalSF_L"), RooFit.LineColor(ROOT.kBlue))
        
        frame.SetMinimum(0)
        #frame.SetMaximum(yMax*1.3)
        template.drawCanvas()
        frame.Draw()
        template.drawLatexLabels()
        
        leg = ROOT.TLegend(0.5,0.70,0.9,0.85)
        leg.SetNColumns(2)
        leg.SetTextSize(0.03)
        leg.SetTextFont(42)
        
        leg.AddEntry(frame.findObject("signalOF_P"), "signal (OF)", "pe")
        #leg.AddEntry(frame.findObject("signalOF_L"), "fit signal (OF)", "l")
        
        leg.AddEntry(frame.findObject("signalSF_P"), "signal (SF)", "pe")
        leg.AddEntry(frame.findObject("signalSF_L"), "fit signal (SF)", "l")
        
        leg.Draw("same")
        
        
        template.saveAs(vari+"_signal_fit_"+theConfig.runRange.label)
    
        #getattr(ws,"import")(mcFitOF) 
        getattr(ws,"import")(mcFitSF)
        
        

    print "Fits are done"
    allObj = None
    ws.Print()
    fileName = "workspaces/workspace_NLLpdfs_signal_%s.root"%(theConfig.flag)
    print "Saving pdfs in workspace "+fileName
    ws.writeToFile(fileName)
    
    
    
    
def main():
    parser = argparse.ArgumentParser(description='Create PDFs for NLL')
    
    parser.add_argument("-s", "--selection", dest = "selection" , action="store", default="SignalInclusive",
                          help="selection which to apply.")
    parser.add_argument("-S", "--signals", dest = "signals" , action="append", default=[],
                          help="selection which to apply.")
    parser.add_argument("-P", "--path", dest = "signalPath" , action="store", default="",
                          help="path to signal samples")
    parser.add_argument("-u", "--use", action="store_true", dest="useExisting", default=False,
                          help="use existing datasets from workspace, default is false.")
    parser.add_argument("-p", "--pileup", action="store_true", dest="puReweighting", default=False,
                          help="use PU reweighting on MC samples")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False,
                          help="Verbose mode.")                          
    args = parser.parse_args()  
    
    
    useExistingDataSet = args.useExisting
    region = args.selection
    puReweighting = args.puReweighting
    verbose = args.verbose
    signals = args.signals
    signalPath = args.signalPath
    
    if signals == []:
        signals = ["T6bbllslepton_msbottom_700_mneutralino_400"]
    if signalPath == "":
        signalPath = "/user/teroerde/trees/sw8021v1015_Signal/"
    
    fitVariables(useExistingDataSet, region, puReweighting, verbose, signals, signalPath)

if __name__ == "__main__":
    main()
