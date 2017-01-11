import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT
import ratios

from setTDRStyle import setTDRStyle
from helpers import *    

################## SUMMARY OF CLASS plotTemplate #######################
## Constructors:
# * plotTemplate()
#
## Methods:
# * setPrimaryPlot(plot, drawOption)
#       Plot (histogram, graph) to be drawn first with drawOption, 
#       defining the axes and boundaries, redrawn 
#       after secondary plots by default so it will be on top
#
# * addSecondaryPlot(plot, drawOption)
#       Adds plot (anything with Draw(drawOption) method in root) to 
#       list of secondary plots
#
# * clearSecondaryPlots()
#       Resets list of secondary plots
#
# * addRatioErrorByHist(self,title, histUp, histDown, color, fillStyle)
#       See the RatioGraph class
#
# * addRatioErrorBySize(self,title, size, color, fillStyle, add)
#       See the RatioGraph class
#
# * addRatioPair(nominator, denominator, color)
#       Add a pair of histograms to be drawn in the ratioGraph. Will 
#       also be used for efficiency plots.
#
# * addResidualPlot(h1, h2, range=None, color=ROOT.kBlack, markerStyle=20, markerSize=1, fillColor=ROOT.kWhite, errList=None, options="")
#       Add a residual plot to be drawn with h1 and h2. h1 can be TH1 or 
#       TGraphErrors, while h2 can also be TF1. errList can be used to 
#       apply custom errors, each entry in the list being the error to be 
#       used. A range can be defined in the format (min, max), where min 
#       max are included.
#       options:    "-" to multiply residuals by -1.
#                   "P" to create a pull plot (divide by uncertainties)
#                   "H" to draw as a histogram (without errors). fillColor 
#                       is used as the histogram bar color
#
# * clearRatioPairs()
#       Empty list of ratioPairs
#
# * draw()
#       Draw full canvas
#
# * drawCanvas()
#       Draws canvas and pads in case one does not want to use draw()
#
# * drawLatexLabels()
#       If any of the labels were changed after calling draw() or one 
#       does not want to use draw(), this can be called to (re)draw all 
#       the labels
#
# * drawRatioPlot()
#       Draws all ratio or efficiency plots that were added as ratio 
#       pairs
#
# * drawLegend()
#       Draws legend of all plots with specified labels if hasLegend is True
#
# * setFolderPath(folderName)
#       Set Name of folder in fig/ to store output
#
# * saveAs(fileName)
#       Print canvas to fileName in folder that was defined earlier, 
#       prints with all defined filetypes, so fileName should not contain 
#       file ending
#
# * clean()
#       Sets all objects in plotTemplate to None
#
#
## Members for options:
# -logX,logY,logZ(bools): 
#       Draw axis with logarithmic scale, false by default
# -changeScale(bool):
#       True by default, defines if the minimum/maximum of primaryPlot 
#       should be adjusted by maximumScale or minimum/maximum. Should be
#       turned to False if primaryPlot is not a Histogramm
# -maximumScale(float):
#       Maximum of plot scaled by maximum value of primary plot
# -minimum, maximum(floats):
#       Overwrites maximum scale, set minimum and maximum y-value (z-value for 2D)
#       (z-value for 2D plots) of primary plot
# -labelX,labelY,labelZ(strings): 
#       Set axis title of primary plot, None (default) will not change titles of primary plot
# -marginTop, marginBottom, marginLeft, marginRight(floats): 
#       Pad outer margins
# -personalWork, preliminary, forTWIKI, plotData(bools): 
#       For text below CMS logo. Default: True, False, False, False
# -hasRatio, hasEfficiency, hasBottomWindow, hasRatio(bools): 
#       Draw ratio/efficiency/residual graph, if all are true, only ratio graph is drawn. hasBottomWindow only creates lower pad. 
#       Default: False
# -hasLegend (bool):
#       Automatically draw legend of all added plots that have specified labels
# -ratioLabel, efficiencyLabel(strings): 
#       Y-axis label of ratio/efficiency graph
# -ratioMin, ratioMax(floats):
#       Min/Max values in ratio graph
# -ratioPairs (list of tuples of histogram, histogram, color):
#       If not equal to [], will add ratios of the given pairs to the ratioPlot. Will also be used for efficiency plots.
# -redrawPrimary(bool):
#       Should primary plot be redrawn to be on top of other plots. On by default, not recommended for 2D plots
# -dilepton (string):
#       Used dilepton combination in plot. "SF", "EE", "EMu", "MuMu" will result in predefined dilepton strings.
#       If dilepton is set to a different string, this will be used directly.
# -fileTypes (list of strings):
#       List of file endings to print the canvas into. Default: ["pdf"]
#  ---
# Following members are for latex labels of cms, cmsExtra, region, cuts, lumi
#  -#PosX, #PosY (floats): 
#       Position of label in NDC. lumiPosX is always used with -(marginRight-0.05) as an offset, so it
#       will be aligned to the edge of the plot if a right margin is introduced
#  -cmsExtraSimPosY (float):
#       Position of cmsExtra label if using simulated data in private work
#  -#Size (float):
#       Text size
#  -#Font, #Align (ints):
#       Text font and align
#  -#Do (bool):
#       Should label be printed (not defined for cuts)
#  -cutsText(string): 
#       Text to describe cuts; if not set, the label will not be drawn
#  -lumiInt, lumiSqrtS (floats):
#       Integrated luminosity [fb^-1] and sqrt(s) [TeV]; if lumiInt is not set, no luminosity will be printed
#  ---
# Following members are for specifications about the residual plot
#  -residualLabel (string):
#       Y-axis title of residual graph
#  -residualRangeUp (float):
#       Upper bound for residual plot if set manually
#  -residualRangeLow (float):
#       Lower bound for residual plot if set manually. Default "None", so
#       -residualRangeUp will be used
#  -residualRangeMode (string):
#       "MANUAL", "AUTO" or "AUTOASYMM". If AUTO is used, the maximum 
#       values of residuals will be used (scaled by residualRangeScale [float])
#       "AUTOASYMM" allows for residual plot not centered around 0 if the 
#       distribution is asymmetric around 0. Default: "AUTO"
#  -residualZeroLineDo (bool):
#       draw line through 0. Default: True
#  -residualZeroLineWidth (float):
#       width of zero line. Default: 2.0
#  -residualZeroLineStyle (float):
#       line style of zero line. Default: 2.0
#  -residualZeroLineColor (int):
#       color of zero line. Default: ROOT.kBlack


def countNumbersUp():
    countNumbersUp.counter += 1
    return countNumbersUp.counter
countNumbersUp.counter = 0    

class plotTemplate:    
    pathName = "fig/"
    folderName = ""
    fileTypes = ["pdf"]
    dilepton = None
    
    logX = False
    logY = False
    logZ = False
    redrawPrimary = True
    maximumScale = 1.8
    maximum = None
    minimum = None
    changeScale = True
    
    marginLeft = 0.15
    marginRight = 0.05
    marginTop = 0.05
    marginBottom = 0.14
    
    ##############
    latexCMS = None
    cmsPosX = 0.19 
    cmsPosY = 0.89
    cmsSize = 0.06
    cmsFont = 61
    cmsAlign = 11
    cmsColor = ROOT.kBlack
    cmsDo = True
    ##############
    latexCMSExtra = None
    cmsExtraPosX = 0.19
    cmsExtraPosY = 0.85
    cmsExtraSimPosY = 0.82
    cmsExtraSize = 0.045
    cmsExtraFont = 52
    cmsExtraAlign = 11
    cmsExtraColor = ROOT.kBlack
    cmsExtraDo = True
    ##############
    latexLumi = None
    lumiPosX = 0.95 
    lumiPosY = 0.96
    lumiSize = 0.04
    lumiFont = 42
    lumiAlign = 31
    lumiSqrtS = 13
    lumiInt = None
    lumiColor = ROOT.kBlack
    lumiDo = True
    ##############
    latexRegion = None
    latexRegion2 = None
    regionPosX = 0.92
    regionPosY = 0.89
    regionSize = 0.03
    regionFont = 42
    regionAlign = 32
    regionColor = ROOT.kBlack
    regionName = ""
    regionDo = True
    ##############
    latexCuts = None
    cutsPosX = 0.92
    cutsPosY = 0.81
    cutsSize = 0.03
    cutsFont = 42
    cutsAlign = 32
    cutsText = None
    cutsColor = ROOT.kBlack
    ##############
    hasLegend = False
    legend = None
    legendColumns = 1
    legendPosX1 = 0.55
    legendPosX2 = 0.90
    legendPosY1 = 0.55
    legendPosY2 = 0.70
    legendFont = 42
    legendTextSize = 0.03
    legendTextColor = 1
    legendBorderSize = 0
    legendFillColor = 0
    legendFillStyle = 0
    ##############    
    
    labelX = None
    labelY = None
    labelZ = None 
    nDivs = None
    
    ratioLabel = "ratio"    
    efficiencyLabel = "efficiency"
    ratioMin = 0
    ratioMax = 2
    efficiencyMin = 0
    efficiencyMax = 1.2
    ratioErrsSize = []
    ratioErrsHist = []
    ratioPairs = []
    ratioPadHeight = 0.3
    hasEfficiency = False
    efficiencyOption = "cp"
    hasRatio = False
    hasBottomWindow = False
    hasResidual = False
    
    residualPlots = []
    residualGraphs = []
    residualLabel = ""
    residualRangeUp =  3
    residualRangeLow = None
    residualRangeMode = "AUTO" # MANUAL, AUTO, AUTOASYMM
    residualRangeScale = 1.1 
    residualZeroLineDo = True
    residualZeroLine = None
    residualZeroLineWidth = 2
    residualZeroLineStyle = 2
    residualZeroLineColor = ROOT.kBlack
    
    forTWIKI = False
    preliminary = False
    personalWork = True
    plotData = False
    
    def __init__(self):        
        self.canvas = None
        self.plotPad = None
        self.ratioPad = None
        
        self.primaryPlot = None
        self.secondaryPlots = []
        
        self.ratioErrsSize = []
        self.ratioErrsHist = []
        
        self.ratioPairs = []
        setTDRStyle() 
        
        self.latexCMS      = None
        self.latexCMSExtra = None
        self.latexCuts     = None
        self.latexLumi     = None
        self.latexRegion   = None
        
    
    
    def addRatioPair(self, nominator, denominator, color=ROOT.kBlack, markerstyle=20):
        self.ratioPairs.append((nominator, denominator, color, markerstyle))
        
    def clearRatioPairs(self):
        self.ratioPairs = []

    def addRatioErrorBySize(self,title, size, color, fillStyle, add,number=0):
        self.ratioErrsSize.append((title,size,color,fillStyle,add,number))

    def addRatioErrorByHist(self,title, histUp, histDown, color, fillStyle,number=0):
        self.ratioErrsHist.append((title,histUp,histDown,color,fillStyle,number))
        
    def setFolderName(self,name):
        self.folderName = name
        self.pathName = "fig/%s/"%(name)
    
    def saveAs(self,fileName):
        ensurePathExists(self.pathName)
        for typ in self.fileTypes:
            self.canvas.Print(self.pathName+fileName+"."+typ)
    
    def setPrimaryPlot(self,hist, drawOption, label=None):
        self.primaryPlot = (hist, drawOption, label)
    
    def addSecondaryPlot(self,hist, drawOption="", label = None):
        self.secondaryPlots.append((hist, drawOption, label))
        
    
    def addResidualPlot(self, h1, h2, resRange=None, color=ROOT.kBlack, markerStyle=20, markerSize=1, fillColor=ROOT.kWhite, errList=None, options=""):
        self.residualPlots.append((h1, h2, resRange, color, markerStyle, markerSize, fillColor, errList, options))
      
    def clearSecondaryPlots(self):
        self.secondaryPlots = []
    
    def drawCanvas(self):
        self.canvas = ROOT.TCanvas("hCanvas%d"%(countNumbersUp()), "", 800,800)
        if self.hasRatio or self.hasEfficiency or self.hasResidual or self.hasBottomWindow:
            self.plotPad = ROOT.TPad("plotPad","plotPad",0,self.ratioPadHeight,1,1)
        else:
            self.plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
        self.plotPad.UseCurrentStyle()
        self.plotPad.Draw()  
        
        if self.hasRatio or self.hasEfficiency or self.hasResidual or self.hasBottomWindow:
            self.ratioPad = ROOT.TPad("ratioPad","ratioPad",0,0,1,self.ratioPadHeight)
            self.ratioPad.UseCurrentStyle()
            self.ratioPad.Draw()
         
        if self.hasRatio or self.hasEfficiency or self.hasResidual or self.hasBottomWindow:
            self.plotPad.SetTopMargin    (self.marginTop)
            self.plotPad.SetLeftMargin   (self.marginLeft)
            self.plotPad.SetRightMargin  (self.marginRight)
            self.ratioPad.SetBottomMargin(self.marginBottom)
            self.ratioPad.SetLeftMargin  (self.marginLeft)
            self.ratioPad.SetRightMargin (self.marginRight)
        else:
            self.plotPad.SetTopMargin   (self.marginTop)
            self.plotPad.SetLeftMargin  (self.marginLeft)
            self.plotPad.SetRightMargin (self.marginRight)
            self.plotPad.SetBottomMargin(self.marginBottom)
            
        self.plotPad.cd()  
        
        if self.logX:
            self.plotPad.SetLogx()
            if self.hasRatio or self.hasEfficiency or self.hasResidual or self.hasBottomWindow:
                self.ratioPad.SetLogx()
        if self.logY:
            self.plotPad.SetLogy()
        if self.logZ:
            self.plotPad.SetLogz()
    
    def drawLatexLabels(self):
        #CMS Text
        if self.cmsDo:
            if self.latexCMS == None:
                self.latexCMS = ROOT.TLatex()
            self.latexCMS.SetTextFont(self.cmsFont)
            self.latexCMS.SetTextSize(self.cmsSize)
            self.latexCMS.SetTextAlign(self.cmsAlign)
            self.latexCMS.SetNDC(True)
            self.latexCMS.SetTextColor(self.cmsColor)
            self.latexCMS.DrawLatex(self.cmsPosX,self.cmsPosY,"CMS")
        else:
            self.latexCMS = None
        #Sub CMS Text
        if self.cmsExtraDo:
            if self.latexCMSExtra == None:
                self.latexCMSExtra = ROOT.TLatex()
            self.latexCMSExtra.SetTextFont(self.cmsExtraFont)
            self.latexCMSExtra.SetTextSize(self.cmsExtraSize)
            self.latexCMSExtra.SetTextAlign(self.cmsExtraAlign)
            self.latexCMSExtra.SetNDC(True) 
            self.latexCMSExtra.SetTextColor(self.cmsExtraColor)
            yLabelPos = self.cmsExtraPosY
            cmsExtra = ""
            if self.personalWork:
                cmsExtra = "Private Work"
                if not self.plotData:
                    cmsExtra = "#splitline{Private Work}{Simulation}"
                    yLabelPos = self.cmsExtraSimPosY
            elif not self.plotData:
                cmsExtra = "Simulation" 
            elif self.preliminary:
                cmsExtra = "Preliminary"
            elif self.forTWIKI:
                cmsExtra = "Unpublished"        
            self.latexCMSExtra.DrawLatex(self.cmsExtraPosX,yLabelPos,"%s"%(cmsExtra))
        else:
            self.latexCMSExtra = None
        #Lumi and sqrt(s) Text
        if self.lumiDo:
            if self.latexLumi == None:
                self.latexLumi = ROOT.TLatex()
            self.latexLumi.SetTextFont(self.lumiFont)
            self.latexLumi.SetTextAlign(self.lumiAlign)
            self.latexLumi.SetTextSize(self.lumiSize)
            self.latexLumi.SetNDC(True)  
            self.latexLumi.SetTextColor(self.lumiColor)                      
            if self.lumiInt != None:
                self.latexLumi.DrawLatex(self.lumiPosX-(self.marginRight-0.05), self.lumiPosY, "%s fb^{-1} (%s TeV)"%(self.lumiInt,self.lumiSqrtS))   
            else:
                self.latexLumi.DrawLatex(self.lumiPosX-(self.marginRight-0.05), self.lumiPosY, "%s TeV"%(self.lumiSqrtS))
        else:
            self.latexLumi = None
        #Region identifier
        if self.regionDo:
            if self.latexRegion == None:
                self.latexRegion = ROOT.TLatex()
            self.latexRegion.SetTextAlign(self.regionAlign)
            self.latexRegion.SetTextSize(self.regionSize)
            self.latexRegion.SetNDC(True)
            self.latexRegion.SetTextFont(self.regionFont)
            self.latexRegion.SetTextColor(self.regionColor)
            if self.dilepton != None:
                if self.dilepton == "SF":
                    dileptonLabel = "ee+#mu#mu"
                elif self.dilepton == "EE":
                    dileptonLabel = "ee"
                elif self.dilepton == "MuMu":
                    dileptonLabel = "#mu#mu"
                elif self.dilepton == "EMu":
                    dileptonLabel = "e#mu"
                else:
                    dileptonLabel = self.dilepton
            else:
                dileptonLabel = ""
            
            if dileptonLabel != "":
                if self.regionName != "":
                    self.latexRegion2 = self.latexRegion.Clone()
                    self.latexRegion.DrawLatex(self.regionPosX,self.regionPosY+0.5*self.regionSize,self.regionName) 
                    self.latexRegion2.DrawLatex(self.regionPosX,self.regionPosY-0.5*self.regionSize,dileptonLabel)
                else:
                    self.latexRegion.DrawLatex(self.regionPosX,self.regionPosY,dileptonLabel) 
            else:
                self.latexRegion.DrawLatex(self.regionPosX,self.regionPosY,self.regionName) 
        else:
            self.latexRegion = None
        #Cuts
        if self.cutsText != None:
            if self.latexCuts == None:
                self.latexCuts = ROOT.TLatex()
            self.latexCuts.SetTextFont(self.cutsFont)
            self.latexCuts.SetTextAlign(self.cutsAlign)
            self.latexCuts.SetTextSize(self.cutsSize)
            self.latexCuts.SetNDC(True)   
            self.latexCuts.SetTextColor(self.cutsColor)    
            self.latexCuts.DrawLatex(self.cutsPosX, self.cutsPosY, self.cutsText)
        else:
            self.latexCuts = None
            
    def clean(self):       
        self.latexCMS       = None
        self.latexCMSExtra  = None
        self.latexCuts      = None
        self.latexLumi      = None
        self.latexRegion    = None
        self.primaryPlot    = None
        self.legend         = None
        self.secondaryPlots = []
        self.ratioGraphs    = []
        self.residualGraphs  = []
        self.residualPlots   = []
        self.residualZeroLine= None
        self.ratioPairs     = []
        self.pathName       = "fig/"
        self.folderName     = ""
        self.canvas         = None
        self.plotPad        = None
        self.ratioPad       = None
        self.hAxis          = None
    
    def drawRatioPlots(self):
        if self.hasRatio or self.hasEfficiency or self.hasResidual:
            self.ratioPad.cd()
            if self.hasRatio:
                self.ratioGraphs = []
                for nominator, denominator, color, markerstyle in self.ratioPairs:
                    self.ratioGraphs.append(ratios.RatioGraph(nominator, denominator, xMin=self.primaryPlot[0].GetXaxis().GetBinLowEdge(1), xMax=self.primaryPlot[0].GetXaxis().GetBinUpEdge(self.primaryPlot[0].GetNbinsX()),title=self.ratioLabel,yMin=self.ratioMin,yMax=self.ratioMax,ndivisions=10,color=color,  adaptiveBinning=1000 ))
                for err in self.ratioErrsSize:
                    self.ratioGraphs[err[5]].addErrorBySize(err[0],err[1],err[2],err[3],err[4])
                for err in self.ratioErrsHist:
                    self.ratioGraphs[err[5]].addErrorByHistograms(err[0],err[1],err[2],err[3],err[4])
                for number,graph in enumerate(self.ratioGraphs):
                    if number == 0:
                        graph.draw(ROOT.gPad,True,False,True,chi2Pos=0.8)
                        graph.hAxis.GetXaxis().SetNdivisions(self.primaryPlot[0].GetXaxis().GetNdivisions())
                    else:
                        graph.draw(ROOT.gPad,False,False,True,chi2Pos=0.8)
                    graph.graph.SetMarkerStyle(markerstyle)
                    
            elif self.hasEfficiency:
                self.ratioGraphs = []
                self.plotPad.Update() # So that Uxmin and Uxmax are retrievable
                self.hAxis = ROOT.TH2F("hAxis%d"%(countNumbersUp()), "", 20, self.plotPad.GetUxmin(), self.plotPad.GetUxmax(), 10, self.efficiencyMin, self.efficiencyMax)    
                self.hAxis.GetYaxis().SetNdivisions(408)
                self.hAxis.GetYaxis().SetTitleOffset(0.4)
                self.hAxis.GetYaxis().SetTitleSize(0.15)
                self.hAxis.GetXaxis().SetLabelSize(0.0)
                self.hAxis.GetYaxis().SetLabelSize(0.15)
                self.hAxis.GetXaxis().SetNdivisions(self.primaryPlot[0].GetXaxis().GetNdivisions())
                self.hAxis.GetYaxis().SetTitle(self.efficiencyLabel)
                self.hAxis.Draw("AXIS")
                for nominator, denominator, color, markerstyle in self.ratioPairs:
                    tmp = ROOT.TGraphAsymmErrors(nominator,denominator, self.efficiencyOption)
                    tmp.SetMarkerColor(color)
                    tmp.SetLineColor(color)
                    tmp.SetMarkerStyle(markerstyle)
                    self.ratioGraphs.append(tmp)
                    self.ratioGraphs[len(self.ratioGraphs)-1].Draw("same P")
                    
            elif self.hasResidual:
                low = self.residualRangeLow if (self.residualRangeLow != None) else -self.residualRangeUp
                up  = self.residualRangeUp
                
                minRes =  100000000000.0
                maxRes = -100000000000.0
                
                self.plotPad.Update() # So that Uxmin and Uxmax are retrievable
                self.hAxis = ROOT.TH2F("hAxis%d"%(countNumbersUp()), "", 20, self.plotPad.GetUxmin(), self.plotPad.GetUxmax(), 10, low, up)    
                self.hAxis.GetYaxis().SetNdivisions(408)
                self.hAxis.GetYaxis().SetTitleOffset(0.4)
                self.hAxis.GetYaxis().SetTitleSize(0.15)
                self.hAxis.GetXaxis().SetLabelSize(0.0)
                self.hAxis.GetYaxis().SetLabelSize(0.15)
                self.hAxis.GetXaxis().SetNdivisions(self.primaryPlot[0].GetXaxis().GetNdivisions())
                self.hAxis.GetYaxis().SetTitle(self.residualLabel)
                self.hAxis.Draw("AXIS")
                
                if self.residualZeroLineDo:
                    self.residualZeroLine = ROOT.TLine(self.plotPad.GetUxmin(),0,self.plotPad.GetUxmax(),0)
                    self.residualZeroLine.SetLineColor(self.residualZeroLineColor)
                    self.residualZeroLine.SetLineWidth(self.residualZeroLineWidth)
                    self.residualZeroLine.SetLineStyle(self.residualZeroLineStyle)
                    self.residualZeroLine.Draw("same")
                
                self.residualGraphs = []
                
                for h1, h2, resRange, color, markerstyle, markersize, fillcolor, errList, options in self.residualPlots:
                    
                    tmp = ROOT.TGraphAsymmErrors()
                    tmp.SetMarkerColor(color)
                    tmp.SetMarkerSize(markersize)
                    tmp.SetLineColor(color)
                    tmp.SetFillColor(fillcolor)
                    tmp.SetMarkerStyle(markerstyle)
                    self.residualGraphs.append(tmp)
                    if h1.InheritsFrom(ROOT.TH1.Class()):
                        slope = 0
                        for i in range(1, h1.GetNbinsX()+1):
                            
                            xPos = h1.GetBinCenter(i)
                            if resRange != None:
                                if xPos > resRange[1] or xPos < resRange[0]:
                                    tmp.SetPoint(i, xPos, 0)
                                    tmp.SetPointError(i, 0, 0, 0, 0)
                                    continue
                            
                            minuent = h1.GetBinContent(i)
                            minuent_err = (h1.GetBinErrorLow(i), h1.GetBinErrorUp(i))
                            
                            
                            
                            if h2.InheritsFrom(ROOT.TH1.Class()):
                                subtrahent = h2.GetBinContent(h2.FindBin(xPos))
                                subtrahent_err = (h2.GetBinErrorLow(h2.FindBin(xPos)), h2.GetBinErrorUp(h2.FindBin(xPos)))
                            elif h2.InheritsFrom(ROOT.TF1.Class()):
                                subtrahent = h2.Eval(xPos)
                                slope = h2.Derivative(xPos)
                                subtrahent_err = (0,0)
                            else: 
                                print "Error in drawResiduals: Invalid type of subtrahent", h1
                                exit()
                            
                            residual = minuent - subtrahent
                            if residual >= 0:
                                i_m = 0
                                i_s = 1
                            else:
                                i_m = 1
                                i_s = 0
                                
                            residual_err = (minuent_err[i_m]**2 + subtrahent_err[i_s]**2)**0.5
                            if errList != None:
                                residual_err = errList[i-1]
                            
                            if "P" in options:
                                if residual_err > 0:
                                    residual /= residual_err
                                    residual_err = 1
                                else:
                                    residual = 0
                                    residual_err = 0
                                
                            if "-" in options:
                                residual = -residual
                            
                            if residual < minRes:
                                minRes = residual
                            if residual > maxRes:
                                maxRes = residual
                                
                            
                            tmp.SetPoint(i, xPos, residual)
                            tmp.SetPointError(i, 0, 0, residual_err, residual_err)
                                
                    elif h1.InheritsFrom(ROOT.TGraphErrors.Class()):
                        for i in range(h1.GetN()):
                            xPos = h1.GetX()[i]
                            if resRange != None:
                                if xPos > resRange[1] or xPos < resRange[0]:
                                    tmp.SetPoint(i, xPos, 0)
                                    tmp.SetPointError(i, 0, 0, 0, 0)
                                    continue

                            
                            minuent = h1.GetY()[i]
                            if h1.InheritsFrom(ROOT.TGraphAsymmErrors.Class()):
                                    minuent_err = (h1.GetEYlow()[i], h1.GetEYhigh()[i])
                            else:
                                    minuent_err = (h1.GetEY()[i], h1.GetEY()[i])
                                    
                            if h2.InheritsFrom(ROOT.TH1.Class()):
                                subtrahent = h2.GetBinContent(h2.FindBin(xPos))
                                subtrahent_err = h2.GetBinError(h2.FindBin(xPos))
                            elif h2.InheritsFrom(ROOT.TGraphErrors.Class()):
                                subtrahent = h2.GetY()[i]
                                if h2.InheritsFrom(ROOT.TGraphAsymmErrors.Class()):
                                    subtrahent_err = (h2.GetEYlow()[i], h2.GetEYhigh()[i])
                                else:
                                    subtrahent_err = (h2.GetEY()[i], h2.GetEY()[i])
                            elif h2.InheritsFrom(ROOT.TF1.Class()):
                                subtrahent = h2.Eval(xPos)
                                subtrahent_err = (0,0)
                                
                            residual = minuent - subtrahent
                            if residual >= 0:
                                i_m = 0
                                i_s = 1
                            else:
                                i_m = 1
                                i_s = 0
                                
                            residual_err = (minuent_err[i_m]**2 + subtrahent_err[i_s]**2 )**0.5
                            if errList != None:
                                residual_err = errList[i]
                            
                            if "P" in options:
                                if residual_err > 0:
                                    residual /= residual_err
                                    residual_err = 1
                                else:
                                    residual = 0
                                    residual_err = 0
                            if "-" in options:
                                residual = -residual
                            
                            if residual < minRes:
                                minRes = residual
                            if residual > maxRes:
                                maxRes = residual
                            
                            tmp.SetPoint(i, xPos, residual)
                            tmp.SetPointError(i, 0, 0, residual_err, residual_err)
                    
                    
                    else:
                        print "Error in drawResiduals: Invalid type of minuent ", h2
                        exit()
                
                    if "H" in options:
                        tmp.Draw("same BX")
                    else:
                        tmp.Draw("same P")
                
                if self.residualRangeMode.upper() == "AUTO":
                    boundaries = max(abs(minRes), maxRes)
                    boundLow = -boundaries * self.residualRangeScale
                    boundUp = boundaries * self.residualRangeScale      
                    self.hAxis.GetYaxis().SetLimits(boundLow, boundUp)              
                elif self.residualRangeMode.upper() == "AUTOASYMM":
                    boundLow = minRes * self.residualRangeScale
                    boundUp = maxRes * self.residualRangeScale
                    self.hAxis.GetYaxis().SetLimits(boundLow, boundUp)              
                
    
    def draw(self):
        self.drawCanvas()
          
        if self.changeScale:
            if self.primaryPlot[0].InheritsFrom(ROOT.TH1.Class()):
                if self.maximum == None:
                    self.primaryPlot[0].SetMaximum(self.primaryPlot[0].GetMaximum()*self.maximumScale)
                else:
                    self.primaryPlot[0].SetMaximum(self.maximum)
                if self.minimum != None:
                    self.primaryPlot[0].SetMinimum(self.minimum)
        
        if self.labelX != None:
            self.primaryPlot[0].GetXaxis().SetTitle(self.labelX)
        if self.labelY != None:
            self.primaryPlot[0].GetYaxis().SetTitle(self.labelY)
        if self.labelZ != None:
            self.primaryPlot[0].GetZaxis().SetTitle(self.labelZ)

        if self.nDivs != None:
            self.primaryPlot[0].GetXaxis().SetNdivisions(self.nDivs)
        
        self.primaryPlot[0].Draw(self.primaryPlot[1])
        
        for plot, drawStyle, label in self.secondaryPlots:
            plot.Draw(drawStyle+"same")
         
        if self.redrawPrimary:
            self.primaryPlot[0].Draw(self.primaryPlot[1]+"same")
        
        self.drawLatexLabels()
        
        self.drawLegend()
        
        self.plotPad.RedrawAxis()
        
        self.drawRatioPlots()
    
    def drawLegend(self):
        if self.hasLegend:
            if self.legend == None:
                self.legend = ROOT.TLegend(self.legendPosX1, self.legendPosY1, self.legendPosX2, self.legendPosY2)
            self.legend.SetTextSize(self.legendTextSize)
            self.legend.SetTextFont(self.legendFont)
            self.legend.SetTextColor(self.legendTextColor)
            self.legend.SetBorderSize(self.legendBorderSize)
            self.legend.SetNColumns(self.legendColumns)
            self.legend.SetFillStyle(self.legendFillStyle)
            self.legend.SetFillColor(self.legendFillColor)
            
            for plot, drawOption, label in [self.primaryPlot]+self.secondaryPlots:
                if label != None:
                    drawOpt = drawOption.replace("hist","l")
                    self.legend.AddEntry(plot, label, drawOpt)
            
            self.legend.Draw("same")
            
# simple example on how to create a custom template
class plotTemplate2D(plotTemplate):
    marginRight = 0.2
    regionPosX = 0.78
    cutsPosX = 0.78
    redrawPrimary = False
    maximumScale = 1.1
    
    def __init__(self):
        plotTemplate.__init__(self)
        

    
