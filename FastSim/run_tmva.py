#!/usr/bin/env python
from ROOT import *

def bookMethods(loader, factory, suffix):
    loader.AddSignalTree    (treeS, 1.0)
    loader.AddBackgroundTree(treeB, 1.0)
    loader.PrepareTrainingAndTestTree(TCut(""), TCut(""),
                                      "nTrain_Signal=5000:nTrain_Background=5000:SplitMode=Random:NormMode=NumEvents:!V")

    factory.BookMethod(loader,TMVA.Types.kBDT, "_".join(["BDT", suffix]),
                       "!V:NTrees=200:MinNodeSize=2.5%:MaxDepth=2:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20")

    factory.BookMethod(loader,TMVA.Types.kBDT, "_".join(["BDTG", suffix]),
                       "!H:!V:NTrees=1000:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.50:nCuts=20:MaxDepth=2");

    factory.BookMethod(loader,TMVA.Types.kMLP, "_".join(["MLP", suffix]),
                       "!H:!V:NeuronType=tanh:VarTransform=N:NCycles=100:HiddenLayers=N+5:TestRate=5:!UseRegulator")

    return factory

fin = TFile("event.root")
treeS = fin.Get("treeS")
treeB = fin.Get("treeB")

fout = TFile.Open("tmva.root", "RECREATE")

TMVA.Tools.Instance()
factory = TMVA.Factory("TMVAClassification", fout,
                       "!V:ROC:!Correlations:!Silent:Color:!DrawProgressBar:AnalysisType=Classification" )

varSets = {
    "dtdr":["dt", "dr"],
    "vtx":["x1", "y1", "z1", "x2", "y2", "z2"],
    "dtdrvtx":["dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"],
    "dtvtx":["dt", "x1", "y1", "z1", "x2", "y2", "z2"],
    "all":["En1", "En2", "dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"],
}
loaders = []
for name, variables in varSets.iteritems():
    loader = TMVA.DataLoader("dataset_%s" % name)
    for var in variables: loader.AddVariable(var)
    bookMethods(loader, factory, name)
    loaders.append(loader)

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

#c = factory.GetROCCurve(loader)
#c.Draw()

