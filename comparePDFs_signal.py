import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
from ROOT import RooFit
from setTDRStyle import setTDRStyle
from defs import Regions
from messageLogger import messageLogger as log
import argparse 

from locations import locations

from plotTemplate import plotTemplate
        
        
def getSFTree(path, name):
        from helpers import readTreeFromFile
        eeTree = readTreeFromFile(path+name, "EE")
        mmTree = readTreeFromFile(path+name, "MuMu")
        
        sfTree = ROOT.TChain()
        sfTree.Add(eeTree)
        sfTree.Add(mmTree)
        
        cut = getattr(Regions,"SignalInclusive").cut
        cut+= "&& (acos((vMet.Px()*jet1.Px()+vMet.Py()*jet1.Py())/vMet.Pt()/jet1.Pt()) > 0.4) && (acos((vMet.Px()*jet2.Px()+vMet.Py()*jet2.Py())/vMet.Pt()/jet2.Pt()) > 0.4)"
        ROOT.gROOT.cd()
        sfTree = sfTree.CopyTree(cut)
        #exit()
        return sfTree
        

        
        
        return sfTree
        
def comparePDFs(dataSpace,pdfSpace, pdfSpace2,isMC):
        dataSet = None
        pdfSuffix = ""

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
        hDiff_ttbar = ROOT.TH1F("hDiff", "", 45, -15, 30)        
        hNormal_ttbar = ROOT.TH1F("hDiff", "", 45, 10, 55)        
        
        
        hDiff_ttbar.Sumw2()
        hNormal_ttbar.Sumw2()
        print "Calculating nll for ttbar"
        for i in range(dataSet.numEntries()):
        #for i in range(10000):
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
                               
                #-------------------------------------------------------
                nLL2 = -ROOT.TMath.Log(ptPdfVal2*sumMlbPdfVal2*deltaPhiPdfVal2*metPdfVal2)
                
                likelihoodRatio = nLL - nLL2
                hDiff_ttbar.Fill(likelihoodRatio)
                hNormal_ttbar.Fill(nLL)
          
        
                
       
        hDiff_ttbar.Scale(1./hDiff_ttbar.Integral())
        hNormal_ttbar.Scale(1./hNormal_ttbar.Integral())
        
        signalPath = "/user/teroerde/trees/sw8021v1015_Signal/"
        signals = ["sw8021v1015.processed.T6bbllslepton_msbottom_700_mneutralino_150.root",
        "sw8021v1015.processed.T6bbllslepton_msbottom_700_mneutralino_400.root",
        "sw8021v1015.processed.T6bbllslepton_msbottom_700_mneutralino_675.root",
        "sw8021v1015.processed.T6bbllslepton_msbottom_1250_mneutralino_150.root",
        "sw8021v1015.processed.T6bbllslepton_msbottom_1250_mneutralino_750.root",
        "sw8021v1015.processed.T6bbllslepton_msbottom_1250_mneutralino_1200.root",
        "sw8021v1015.processed.T6bbllslepton_msbottom_1600_mneutralino_150.root",
        "sw8021v1015.processed.T6bbllslepton_msbottom_1600_mneutralino_900.root",
        "sw8021v1015.processed.T6bbllslepton_msbottom_1600_mneutralino_1550.root"]
        
        #from glob import glob
        #import os
        #counter = 0
        #a = glob(signalPath+"*.root")
        #a.sort()
        #sigs = [os.path.basename(x) for x in a]
        
        #signals = []
        #for s in sigs:
                #if counter % 4 == 0:
                        #signals.append(s)
                #counter += 1
                
        
        template = plotTemplate()
        template2 = plotTemplate()
        
        signalHists_ratio = []
        signalHists_normal = []
        
        from plotTemplate import getNewColor
        for signal in signals:   
                print "Calculating nll for ", signal.split(".")[2]
                mb = signal.split("_")[2]
                mn = signal.split("_")[4].split(".")[0]
                
                tmpHist = ROOT.TH1F("hDiff"+signal, "", 45, -15, 30) 
                tmpHist_normal = ROOT.TH1F("hNormal"+signal, "", 45, 10, 55) 
                color = getNewColor()
                
                signalHists_ratio.append((mb, mn, tmpHist))
                signalHists_normal.append((mb, mn, tmpHist_normal))
                
                tmpHist.SetLineColor(color)
                tmpHist.SetLineStyle(2)
                tmpHist.SetLineWidth(1)
                tmpHist.Sumw2()
                tmpHist_normal.SetLineColor(color)
                tmpHist_normal.SetLineStyle(2)
                tmpHist_normal.SetLineWidth(1)
                tmpHist_normal.Sumw2()
                
                template.addSecondaryPlot(tmpHist, "hist", label="m_{#tilde{b}}=%s, m_{#tilde{n}}=%s"%(mb, mn))
                template2.addSecondaryPlot(tmpHist_normal, "hist", label="m_{#tilde{b}}=%s, m_{#tilde{n}}=%s"%(mb, mn))
                
                tmpTree = getSFTree(signalPath, signal)
                for event in tmpTree:
                        metVar.setVal(event.met)
                        zptVar.setVal(event.p4.Pt())
                        mlbVar.setVal(event.sumMlb)
                        ldpVar.setVal(abs(event.deltaPhi))
                        #-------------------------------------------------------
                        metVar2.setVal(event.met)
                        zptVar2.setVal(event.p4.Pt())
                        mlbVar2.setVal(event.sumMlb)
                        ldpVar2.setVal(abs(event.deltaPhi))
                        
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
                                       
                        #-------------------------------------------------------
                        nLL2 = -ROOT.TMath.Log(ptPdfVal2*sumMlbPdfVal2*deltaPhiPdfVal2*metPdfVal2)
                        
                        likelihoodRatio = nLL - nLL2   
                        tmpHist.Fill(likelihoodRatio)
                        tmpHist_normal.Fill(nLL)
                tmpHist.Scale(1./tmpHist.Integral())
                tmpHist_normal.Scale(1./tmpHist_normal.Integral())
        
        
        drawOption1 = "hist"
               
        label = "- ttbar SF"
        fileSuffix = "_ttbarSF"
        
        
        template.plotData = (isMC == 0)
        template.labelX = "#Delta(NLL_{ttbar},NLL_{signal})"
        template.labelY = "normalized units"
        template.minimum = 0
        template.setPrimaryPlot(hDiff_ttbar, "hist", label="t#bar{t}")
        template.hasLegend = True
        template.legendColumns = 3
        template.legendTextSize = 0.01
        template.legendPosY2 = 0.9
        template.legendPosY1 = 0.4
        template.legendPosX1 = 0.45
        
        template.draw()
        
        template.setFolderName("evaluation_likelihoodRatio")
        template.saveAs("ratio%s"%(fileSuffix))
        template.minimum = 0
        
        ####
        template2.plotData = (isMC == 0)
        template2.labelX = "NLL_{ttbar}"
        template2.labelY = "normalized units"
        template2.minimum = 0
        template2.setPrimaryPlot(hNormal_ttbar, "hist", label="t#bar{t}")
        template2.hasLegend = True
        template2.legendColumns = 3
        template2.legendTextSize = 0.01
        template2.legendPosY2 = 0.9
        template2.legendPosY1 = 0.4
        template2.legendPosX1 = 0.45
        template2.draw()
        
        template2.setFolderName("evaluation_likelihoodRatio")
        template2.saveAs("normal%s"%(fileSuffix))
        template2.minimum = 0
        
        for i in range(1, hDiff_ttbar.GetNbinsX()+1):
                if hDiff_ttbar.Integral(1, i) >= 0.95:
                        ratioPoint = i
                        break
                        
        for i in range(1, hNormal_ttbar.GetNbinsX()+1):
                if hNormal_ttbar.Integral(1, i) >= 0.95:
                        normalPoint = i
                        break
                        
        diffCut = hDiff_ttbar.GetBinLowEdge(ratioPoint)
        normalCut = hNormal_ttbar.GetBinLowEdge(normalPoint)
        
        total = 0
        diffPass = 0
        normalPass = 0
        
        diffEff = []
        normalEff = []
        
        for signal in signals:   
                mb = signal.split("_")[2]
                mn = signal.split("_")[4].split(".")[0]
                
                tmpTree = getSFTree(signalPath, signal)
                for event in tmpTree:
                        metVar.setVal(event.met)
                        zptVar.setVal(event.p4.Pt())
                        mlbVar.setVal(event.sumMlb)
                        ldpVar.setVal(abs(event.deltaPhi))
                        #-------------------------------------------------------
                        metVar2.setVal(event.met)
                        zptVar2.setVal(event.p4.Pt())
                        mlbVar2.setVal(event.sumMlb)
                        ldpVar2.setVal(abs(event.deltaPhi))
                        
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
                                       
                        #-------------------------------------------------------
                        nLL2 = -ROOT.TMath.Log(ptPdfVal2*sumMlbPdfVal2*deltaPhiPdfVal2*metPdfVal2)
                        
                        likelihoodRatio = nLL - nLL2   
                        total += 1
                        if likelihoodRatio > diffCut:
                                diffPass += 1
                        if nLL > normalCut:
                                normalPass += 1
                
                diffEff.append((mb,mn, float(diffPass)/total))
                normalEff.append((mb,mn, float(normalPass)/total))
                total = 0
                diffPass = 0
                normalPass = 0
        
        print "For likelihood ratio cutting at ", diffCut, "which excludes ",hDiff_ttbar.Integral(1, ratioPoint-1),"% of all ttbar events"
        print "For NLL cutting at ", normalCut, "which excludes ",hNormal_ttbar.Integral(1, normalPoint-1),"% of all ttbar events"
        
        print "%-*s %-*s %-*s %-*s"%(12, "masses", 20, "signal eff ratio", 20, "signal eff NLL", 20, "improvement")
        for diff, normal in zip(diffEff, normalEff):
                if normal[0] != diff[0] or normal[1] != diff[1]:
                        print "ALARM"
                print "%-*s %-*.4f %-*.4f %-*.4f"%(12, diff[0]+" "+diff[1], 20, diff[2], 20, normal[2], 20, diff[2]-normal[2])
                                       

def main():
        isMC = 1
        
        dataFilePath = "workspaces/saveDataSet_sw8021v1015_Run2016_36fb_noWeights.root"
        dataFile = ROOT.TFile(dataFilePath, "READ")
        dataSpace = dataFile.Get("work")
        
        pdfFilePath = "workspaces/workspace_NLLpdfs_sw8021v1015_Run2016_36fb.root"
        pdfFile = ROOT.TFile(pdfFilePath, "READ")
        pdfSpace = pdfFile.Get("w")
        
        
        #pdfFilePath2 = "pdfs_forMoriond_ver2.root"
        pdfFilePath2 = "workspaces/workspace_NLLpdfs_signal_sw8021v1015.root"
        pdfFile2 = ROOT.TFile(pdfFilePath2, "READ")
        pdfSpace2 = pdfFile2.Get("w")
        
        
        
        
        comparePDFs(dataSpace, pdfSpace, pdfSpace2, 2)
        
            
if __name__ == "__main__":
        main()
