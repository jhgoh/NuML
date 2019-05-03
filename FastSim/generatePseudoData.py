#!/usr/bin/env python

from ROOT import *
import sys, os
import random
import numpy as np

sigFrac = 0.1

f = TFile("template.root")
hSig = f.Get("hSig")
hBkg1 = f.Get("hBkg1")

fout = TFile("event.root", "recreate")
treeS = TTree("treeS", "Signal tree")
treeB = TTree("treeB", "Background tree")
var = np.zeros((10,1), dtype=np.double)
event = np.zeros((1,1), dtype=np.int32)
treeS.Branch("event", event[0], "event/I")
treeB.Branch("event", event[0], "event/I")
for i, varName in enumerate(["En1", "En2", "dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"]):
    treeS.Branch(varName, var[i], varName+"/d")
    treeB.Branch(varName, var[i], varName+"/d")

for i in range(100000):
    event[0] = i
    if random.uniform(0,1) < sigFrac:
        category = 1
        hSig.GetRandom(var)
        treeS.Fill()
    else:
        category = 2
        hBkg1.GetRandom(var)
        treeB.Fill()
fout.Write()
