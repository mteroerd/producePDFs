import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
from ROOT import RooFit
from setTDRStyle import setTDRStyle

from messageLogger import messageLogger as log
import argparse 

from locations import locations

from plotTemplate import plotTemplate
        
def comparePDFs(dataSpace,pdfSpace, pdfSpace2,isMC):
        dataSet = None
        pdfSuffix = ""
        if isMC == 0:
                dataSet = dataSpace.data("dataOF")
                pdfSuffix = "_analyticalPDF_DA"
                
        elif isMC == 1:
                dataSet = dataSpace.data("ttbarOF")
                pdfSuffix = "_analyticalPDF_MC"
                
        elif isMC == 2:
                dataSet = dataSpace.data("ttbarSF")
                pdfSuffix = "_analyticalPDF_MC_SF"
        
        metPdf          = pdfSpace.pdf("met%s"%(pdfSuffix))
        ptPdf           = pdfSpace.pdf("zpt%s"%(pdfSuffix))
        sumMlbPdf       = pdfSpace.pdf("mlb%s"%(pdfSuffix))
        deltaPhiPdf     = pdfSpace.pdf("ldp%s"%(pdfSuffix))
        
        metVar = pdfSpace.var("met_Edge")
        zptVar = pdfSpace.var("lepsZPt_Edge")
        mlbVar = pdfSpace.var("sum_mlb_Edge")
        ldpVar = pdfSpace.var("lepsDPhi_Edge")
        
        metPdf2         = pdfSpace2.pdf("met%s"%(pdfSuffix))
        ptPdf2          = pdfSpace2.pdf("zpt%s"%(pdfSuffix))
        sumMlbPdf2      = pdfSpace2.pdf("mlb%s"%(pdfSuffix))
        deltaPhiPdf2    = pdfSpace2.pdf("ldp%s"%(pdfSuffix))
        
        metVar2 = pdfSpace2.var("met_Edge")
        zptVar2 = pdfSpace2.var("lepsZPt_Edge")
        mlbVar2 = pdfSpace2.var("sum_mlb_Edge")
        ldpVar2 = pdfSpace2.var("lepsDPhi_Edge")
        
        setTDRStyle()
        h1 = ROOT.TH1F("h1", "", 27, 10, 37)
        h2 = ROOT.TH1F("h2", "", 27, 10, 37)        
        hDiff = ROOT.TH1F("hDiff", "", 101, -1.005, 1.005)        
        
        h1.Sumw2()
        h2.Sumw2()
        hDiff.Sumw2()
        for i in range(dataSet.numEntries()):
        #for i in range(100):
                dataPoint = dataSet.get(i)

                metVar.setVal(dataPoint.getRealValue("met_Edge"))
                zptVar.setVal(dataPoint.getRealValue("lepsZPt_Edge"))
                mlbVar.setVal(dataPoint.getRealValue("sum_mlb_Edge"))
                ldpVar.setVal(dataPoint.getRealValue("lepsDPhi_Edge"))
                #-------------------------------------------------------
                metVar2.setVal(dataPoint.getRealValue("met_Edge"))
                zptVar2.setVal(dataPoint.getRealValue("lepsZPt_Edge"))
                mlbVar2.setVal(dataPoint.getRealValue("sum_mlb_Edge"))
                ldpVar2.setVal(dataPoint.getRealValue("lepsDPhi_Edge"))
                
                obsMet = ROOT.RooArgSet(metVar)
                obsZpt = ROOT.RooArgSet(zptVar)
                obsMlb = ROOT.RooArgSet(mlbVar)
                obsLdp = ROOT.RooArgSet(ldpVar)
                #-------------------------------------------------------
                obsMet2 = ROOT.RooArgSet(metVar2)
                obsZpt2 = ROOT.RooArgSet(zptVar2)
                obsMlb2 = ROOT.RooArgSet(mlbVar2)
                obsLdp2 = ROOT.RooArgSet(ldpVar2)
                
                ptPdfVal = ptPdf.getVal(obsZpt)
                sumMlbPdfVal = sumMlbPdf.getVal(obsMlb)
                deltaPhiPdfVal = deltaPhiPdf.getVal(obsLdp)
                metPdfVal = metPdf.getVal(obsMet)
                #-------------------------------------------------------
                ptPdfVal2       = ptPdf2.getVal(obsZpt2)
                sumMlbPdfVal2   = sumMlbPdf2.getVal(obsMlb2)
                deltaPhiPdfVal2 = deltaPhiPdf2.getVal(obsLdp2)
                metPdfVal2      = metPdf2.getVal(obsMet2)
                
                nLL = -ROOT.TMath.Log(ptPdfVal*sumMlbPdfVal*deltaPhiPdfVal*metPdfVal)
                h1.Fill(nLL)                
                #-------------------------------------------------------
                nLL2 = -ROOT.TMath.Log(ptPdfVal2*sumMlbPdfVal2*deltaPhiPdfVal2*metPdfVal2)
                h2.Fill(nLL2)
                
                nLLDiff = nLL - nLL2
                hDiff.Fill(nLLDiff)
          
        
                
        h1.SetMarkerColor(ROOT.kBlack)
        h1.SetLineColor(ROOT.kBlack)
        h1.SetLineWidth(2)
        h2.SetMarkerColor(ROOT.kRed)
        h2.SetLineColor(ROOT.kRed)
        h2.SetLineWidth(2)
        
        
        h1.Scale(1./h1.Integral())
        h2.Scale(1./h2.Integral())
        hDiff.Scale(1./hDiff.Integral())
        
        
        drawOption1 = "PE" if (isMC==0) else "hist"
        
        if isMC == 0:
                label = "- data OF"
                fileSuffix = "_dataOF"
        elif isMC == 1:
                label = "- ttbar OF"
                fileSuffix = "_ttbarOF"
        elif isMC == 2:
                label = "- ttbar SF"
                fileSuffix = "_ttbarSF"
        
        template = plotTemplate()
        template.plotData = (isMC == 0)
        template.labelX = "NLL"
        template.labelY = "normalized units"
        template.minimum = 0
        template.setPrimaryPlot(h1, drawOption1, "Own PDFs %s"%(label))
        template.addSecondaryPlot(h2, drawOption1,"ETH PDFs %s"%(label))
        template.nDivs = 506
        template.hasLegend = True
        
        template.draw()
        
        template.setFolderName("evaluation")
        template.saveAs("comparePDFs%s"%(fileSuffix))
        
        template = plotTemplate()
        template.plotData = (isMC == 0)
        template.labelX = "#Delta(NLL_{own},NLL_{ETH})"
        template.labelY = "normalized units"
        template.minimum = 0
        template.setPrimaryPlot(hDiff, "hist")
        template.draw()
        
        template.setFolderName("evaluation")
        template.saveAs("diffNLL%s"%(fileSuffix))
        template.minimum = 0
        #raw_input("...")
                                  

def compareParameters(pdfSpace, pdfSpace2):
        args  = pdfSpace.allVars()
        args2 = pdfSpace2.allVars()
        
        it = args.createIterator()
        while it:
                if it == None:
                        break
                try:
                        print "RWTH %-*s | %-*.4f | %-*.4f | %-*.4f"%(15, it.GetName(), 8, it.getBinning().lowBound(), 8, it.getBinning().highBound(), 8, it.getValV())
                        it2 = args2.find(it.GetName())
                        print "ETH  %-*s | %-*.4f | %-*.4f | %-*.4f"%(15, it2.GetName(), 8, it2.getBinning().lowBound(), 8, it2.getBinning().highBound(), 8, it2.getValV())
                        print
                except:
                        break
                it.Next()
        
        #pdfSpace2.Print()

def printMaxVals(workspace, dataset):
        dat = workspace.data(dataset)
        minMet = 1000
        maxMet = 0
        minMlb = 3000
        maxMlb = 0
        minZpt = 1000
        maxZpt = 0
        minLdp = 3.2
        maxLdp = 0
        for i in range(dat.numEntries()):
                point = dat.get(i)
                met = point.getRealValue("met_Edge")
                if met < minMet:
                        minMet = met
                elif met > maxMet:
                        maxMet = met
                        
                mlb = point.getRealValue("sum_mlb_Edge")
                if mlb < minMlb:
                        minMlb = mlb
                elif mlb > maxMlb:
                        maxMlb = mlb
                        
                zpt = point.getRealValue("lepsZPt_Edge")
                if zpt < minZpt:
                        minZpt = zpt
                elif zpt > maxZpt:
                        maxZpt = zpt
                        
                ldp = point.getRealValue("lepsDPhi_Edge")
                if ldp < minLdp:
                        minLdp = ldp
                elif ldp > maxLdp:
                        maxLdp = ldp
        print "met ", minMet, maxMet
        print "mlb ", minMlb, maxMlb
        print "zpt ", minZpt, maxZpt
        print "ldp ", minLdp, maxLdp        

def main():
        isMC = 1
        
        dataFilePath = "workspaces/saveDataSet_sw8021v1015_Run2016_36fb_noWeights.root"
        dataFile = ROOT.TFile(dataFilePath, "READ")
        dataSpace = dataFile.Get("work")
        
        pdfFilePath = "workspaces/workspace_NLLpdfs_sw8021v1015_Run2016_36fb.root"
        pdfFile = ROOT.TFile(pdfFilePath, "READ")
        pdfSpace = pdfFile.Get("w")
        
        
        pdfFilePath2 = "pdfs_forMoriond_ver2.root"
        #pdfFilePath2 = "pdfs_version5_80X_2016Data_savingTheWorkspace_withSFPDFs_12p9invfb.root"
        pdfFile2 = ROOT.TFile(pdfFilePath2, "READ")
        pdfSpace2 = pdfFile2.Get("w")
        
        
        #compareParameters(pdfSpace, pdfSpace2)
        printMaxVals(dataSpace, "dataOF")
        printMaxVals(pdfSpace2, "em_data_cuts_of_sr_met150_of")
        #return
        
        for isMC in [0,]:
                comparePDFs(dataSpace, pdfSpace, pdfSpace2, isMC)
        
            
if __name__ == "__main__":
        main()
