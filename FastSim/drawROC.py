#!/usr/bin/env python
from ROOT import *
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

colors = [kRed+1, kBlue+1, kGreen+2, kPink-6, kAzure+1]
lines = [0, 1, 9, 7, 10]

grps = []
fin = TFile("tmva.root")
for i, din in enumerate([x.GetName() for x in fin.GetListOfKeys()]):
    if not din.startswith("dataset"): continue
    din = fin.GetDirectory(din)
    if din == None: continue

    for j, d in enumerate([x.GetName() for x in din.GetListOfKeys()]):
        if not d.startswith("Method_"): continue
        methodName = d.split('_',1)[-1]
        d = din.GetDirectory("%s/%s" % (d, methodName))
        if d == None: continue

        hROC = d.Get("MVA_%s_rejBvsS" % (methodName))
        grp = TGraph()
        grp.SetLineWidth(2)
        grp.SetMarkerSize(1)
        grp.SetName(methodName)
        grp.SetLineColor(colors[i])
        grp.SetMarkerColor(colors[i])
        grp.SetLineStyle(lines[j])
        for b in range(hROC.GetNbinsX()+1):
            eff = hROC.GetXaxis().GetBinCenter(b+1)
            rej = hROC.GetBinContent(b+1)
        
            grp.SetPoint(b, eff, rej)
        auc = float(hROC.Integral())/hROC.GetNbinsX()

        grp.SetTitle("%s AUC=%.4f" % (methodName, auc))
        grps.append((grp, auc))
grps.sort(key=lambda x: x[1], reverse=True)

cROC = TCanvas("cROC", "cROC", 500, 500)
legROC = TLegend(0.15, 0.15, 0.6, 0.15+0.04*len(grps))
legROC.SetFillStyle(0)
legROC.SetBorderSize(0)
hFrame = TH1F("hFrame", "hFrame", 100, 0.75, 1.02)
hFrame.SetMinimum(0.75)
hFrame.SetMaximum(1.02)
hFrame.Draw()
for grp, auc in grps:
    legROC.AddEntry(grp, grp.GetTitle(), "lp")
    grp.Draw("l")
legROC.Draw()
