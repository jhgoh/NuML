#!/usr/bin/env python
from ROOT import *
import sys, os
has_keras = True
try:
    import keras
    import tensorflow as tf
    from keras.layers.core import Dense
    #from keras.optimizers import Adam
except:
    has_keras = False

def bookMethods(factory, loader, varSet, suffix):
    varSetName, variables = varSet
    nvar = len(variables)

    factory.BookMethod(loader,TMVA.Types.kBDT, "_".join(["BDT", suffix]),
                       "!V:NTrees=1000:MinNodeSize=2.5%:MaxDepth=2:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20")

    factory.BookMethod(loader,TMVA.Types.kBDT, "_".join(["BDTG", suffix]),
                       "!H:!V:NTrees=1000:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.50:nCuts=20:MaxDepth=2");

    factory.BookMethod(loader,TMVA.Types.kMLP, "_".join(["MLP", suffix]),
                       "!H:!V:NeuronType=tanh:VarTransform=N:NCycles=100:HiddenLayers=N+5:TestRate=5:!UseRegulator")

    if has_keras:
        if os.path.exists('model_%s.h5' % varSetName): os.remove('model_%s.h5' % varSetName)
        model = keras.models.Sequential()
        model.add(Dense(64, kernel_initializer='normal', activation='relu', input_shape=(nvar,), kernel_regularizer=keras.regularizers.l2(1e-5)))
        model.add(Dense(64, kernel_initializer='normal', activation='relu', kernel_regularizer=keras.regularizers.l2(1e-5)))
        model.add(Dense(64, kernel_initializer='normal', activation='relu', kernel_regularizer=keras.regularizers.l2(1e-5)))
        model.add(Dense(2, kernel_initializer='normal', activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy',])
        model.save('model_%s.h5' % varSetName)
        model.summary()
        factory.BookMethod(loader, TMVA.Types.kPyKeras, "_".join(['PyKeras', suffix]),
                           'H:!V:VarTransform=N:FilenameModel=model_%s.h5:NumEpochs=100:BatchSize=128' % varSetName)

fin = TFile("event.root")
treeS = fin.Get("treeS")
treeB = fin.Get("treeB")

fout = TFile.Open("tmva.root", "RECREATE")

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()
factory = TMVA.Factory("TMVAClassification", fout,
                       "!V:ROC:!Correlations:!Silent:Color:!DrawProgressBar:AnalysisType=Classification" )

varSets = {
    "dtdr":["dt", "dr"],
    "vtx":["x1", "y1", "z1", "x2", "y2", "z2"],
    "dtdrvtx":["dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"],
    "dtvtx":["dt", "x1", "y1", "z1", "x2", "y2", "z2"],
    "all":["En1", "En2", "dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"],
}
allVars = ["En1", "En2", "dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"]
loaders = []
for name, variables in varSets.iteritems():
    loader = TMVA.DataLoader("dataset_%s" % name)
    loader.AddSignalTree    (treeS, 1.0)
    loader.AddBackgroundTree(treeB, 1.0)
    loader.PrepareTrainingAndTestTree(TCut(""), TCut(""),
                                      "nTrain_Signal=5000:nTrain_Background=5000:SplitMode=Random:NormMode=NumEvents:!V")
    for var in variables: loader.AddVariable(var)
    for var in allVars:
        if var not in variables: loader.AddSpectator(var)

    bookMethods(factory, loader, (name, variables), name)
    loaders.append(loader)

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

#c = factory.GetROCCurve(loader)
#c.Draw()

