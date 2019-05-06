#!/usr/bin/env python
from ROOT import *

fin = TFile("event.root")
treeS = fin.Get("treeS")
treeB = fin.Get("treeB")

TMVA.Tools.Instance()

fout = TFile.Open("tmva.root", "RECREATE");

factory = TMVA.Factory("TMVAClassification", fout,
                       "!V:ROC:!Correlations:!Silent:Color:!DrawProgressBar:AnalysisType=Classification" );

loader = TMVA.DataLoader("dataset");
#for var in ["En1", "En2", "dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"]:
#for var in ["dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"]:
for var in ["dt", "dr"]:
#for var in ["x1", "y1", "z1", "x2", "y2", "z2"]:
    loader.AddVariable(var)

loader.AddSignalTree    (treeS, 1.0)
loader.AddBackgroundTree(treeB, 1.0)
loader.PrepareTrainingAndTestTree(TCut(""), TCut(""),
                                  "nTrain_Signal=5000:nTrain_Background=5000:SplitMode=Random:NormMode=NumEvents:!V")

factory.BookMethod(loader,TMVA.Types.kBDT, "BDT",
                   "!V:NTrees=200:MinNodeSize=2.5%:MaxDepth=2:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20")

factory.BookMethod(loader,TMVA.Types.kBDT, "BDTG",
                   "!H:!V:NTrees=1000:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.50:nCuts=20:MaxDepth=2");

factory.BookMethod(loader,TMVA.Types.kMLP, "MLP",
                   "!H:!V:NeuronType=tanh:VarTransform=N:NCycles=100:HiddenLayers=N+5:TestRate=5:!UseRegulator")

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

c = factory.GetROCCurve(loader)
c.Draw()

