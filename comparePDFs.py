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
        hDiff = ROOT.TH1F("hDiff", "", 50, -1, 1)        
        
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
        drawOption2 = "PE" if (isMC==0) else "L"
        
        if isMC == 0:
                label = "- data OF"
                fileSuffix = "_dataOF"
        elif isMC == 1:
                label = "- ttbar OF"
                fileSuffix = "_ttbarOF"
        elif isMC == 2:
                label = "- ttbar SF"
                fileSuffix = "_ttbarSF"
                
        leg = ROOT.TLegend(0.6, 0.7, 0.8, 0.85)
        leg.AddEntry(h1, "Own PDFs %s"%(label), drawOption2)
        leg.AddEntry(h2, "ETH PDFs %s"%(label), drawOption2)
        leg.SetTextSize(0.03)
        leg.SetTextFont(42)
        
        template = plotTemplate()
        template.plotData = (isMC == 0)
        template.labelX = "NLL"
        template.labelY = "normalized units"
        template.minimum = 0
        template.setPrimaryPlot(h1, drawOption1)
        template.addSecondaryPlot(h2, drawOption1)
        template.addSecondaryPlot(leg)
        template.nDivs = 506
        template.draw()
        
        template.setFolderName("evaluation")
        template.saveAs("comparePDFs%s"%(fileSuffix))
        
        template = plotTemplate()
        template.plotData = (isMC == 0)
        template.labelX = "#Delta(NLL_{own},NLL_{ETH})"
        template.labelY = "normalized units"
        template.setPrimaryPlot(hDiff, drawOption1)
        template.draw()
        
        template.setFolderName("evaluation")
        template.saveAs("diffNLL%s"%(fileSuffix))
        template.minimum = 0
        #raw_input("...")
                                  

def main():
        isMC = 1
        
        
        dataFilePath = "workspaces/saveDataSet_sw8010v1010_Run2016_7_7fb_noWeights.root"
        dataFile = ROOT.TFile(dataFilePath, "READ")
        dataSpace = dataFile.Get("work")
        
        pdfFilePath = "workspaces/workspace_NLLpdfs_sw8010v1010_Run2016_7_7fb.root"
        pdfFile = ROOT.TFile(pdfFilePath, "READ")
        pdfSpace = pdfFile.Get("w")
        
        
        pdfFilePath2 = "pdfs_version5_80X_2016Data_savingTheWorkspace_withSFPDFs_12p9invfb.root"
        pdfFile2 = ROOT.TFile(pdfFilePath2, "READ")
        pdfSpace2 = pdfFile2.Get("w")
        
        
        #dataSpace.Print()
        #pdfSpace.Print()
        #pdfSpace2.Print()
        for isMC in [0,1,2]:
                comparePDFs(dataSpace, pdfSpace, pdfSpace2, isMC)
        
            
if __name__ == "__main__":
        main()
