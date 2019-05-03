from ROOT import *
import sys, os
import random
import numpy as np

sigFrac = 0.1

f = TFile("template.root")
hSig = f.Get("hSig")
hBkg1 = f.Get("hBkg1")

fout = TFile("event.root", "recreate")
tree = TTree("tree", "tree")
var = np.zeros((10,1), dtype=np.double)
event = np.zeros((1,1), dtype=np.int32)
category = np.zeros((1,1), dtype=np.int32)
tree.Branch("event", event[0], "event/I")
tree.Branch("catetory", category[0], "category/I")
tree.Branch("En1", var[0], "En1/d")
tree.Branch("En2", var[1], "En2/d")
tree.Branch("dt", var[2], "dt/d")
tree.Branch("dr", var[3], "dr/d")
tree.Branch("x1", var[4], "x1/d")
tree.Branch("y1", var[5], "y1/d")
tree.Branch("z1", var[6], "z1/d")
tree.Branch("x2", var[7], "x2/d")
tree.Branch("y2", var[8], "y2/d")
tree.Branch("z2", var[9], "z2/d")
for i in range(10000):
    event[0] = i
    if random.uniform(0,1) < sigFrac:
        category[0] = 1
        hSig.GetRandom(var)
    else:
        category[0] = 2
        hBkg1.GetRandom(var)
    tree.Fill()
fout.Write()
