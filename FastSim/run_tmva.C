#include "TFile.h"
#include "TTree.h"
#include <map>
#include <string>
#include <memory>
#include <TMVA/DataLoader.h>

void bookMethods(TMVA::Factory& factory, TMVA::DataLoader& loader,
                 /*const std::string& varSetName, const std::vector<std::string>& varables, */std::string suffix)
{
  //const unsigned nvar = variables.size();

  factory.BookMethod(&loader,TMVA::Types::kBDT, suffix.empty() ? "BDT" : ("BDT_"+suffix).c_str(),
                     "!V:NTrees=1000:MinNodeSize=2.5%:MaxDepth=2:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20");
  factory.BookMethod(&loader,TMVA::Types::kBDT, suffix.empty() ? "BDTG" : ("BDTG_"+suffix).c_str(),
                       "!H:!V:NTrees=1000:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.50:nCuts=20:MaxDepth=2");
  factory.BookMethod(&loader,TMVA::Types::kMLP, suffix.empty() ? "MLP" : ("MLP_"+suffix).c_str(),
                       "!H:!V:NeuronType=tanh:VarTransform=N:NCycles=100:HiddenLayers=N+5:TestRate=5:!UseRegulator");
}

void run_tmva()
{
  TFile* fin = TFile::Open("event.root");
  TTree* treeS = (TTree*)fin->Get("treeS");
  TTree* treeB = (TTree*)fin->Get("treeB");

  TFile* fout = TFile::Open("tmva.root", "RECREATE");

  TMVA::Tools::Instance();
  TMVA::Factory factory("TMVAClassification", fout,
                        "!V:ROC:!Correlations:!Silent:Color:!DrawProgressBar:AnalysisType=Classification");


  std::map<std::string, std::vector<std::string> > varSets;
  varSets["dtdr"] = {"dt", "dr"},
  varSets["vtx"] = {"x1", "y1", "z1", "x2", "y2", "z2"};
  varSets["dtdrvtx"] = {"dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"};
  varSets["dtvtx"] = {"dt", "x1", "y1", "z1", "x2", "y2", "z2"};
  varSets["all"] = {"En1", "En2", "dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"};
  std::vector<std::string> allVars = {"En1", "En2", "dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"};

  std::vector<std::unique_ptr<TMVA::DataLoader>> loaders;
  for ( std::map<std::string, std::vector<std::string> >::const_iterator iVarSet = varSets.begin();
        iVarSet != varSets.end(); ++iVarSet ) {
    const std::string name = iVarSet->first;
    const std::vector<std::string> variables = iVarSet->second;
    loaders.push_back(std::unique_ptr<TMVA::DataLoader>(new TMVA::DataLoader(("dataset_"+name).c_str())));
    TMVA::DataLoader& loader = *loaders[loaders.size()-1];
    loader.AddSignalTree(treeS, 1.0);
    loader.AddBackgroundTree(treeB, 1.0);
    loader.PrepareTrainingAndTestTree("", "",
                                      "nTrain_Signal=5000:nTrain_Background=5000:SplitMode=Random:NormMode=NumEvents:!V");
    for ( unsigned i=0, n=variables.size(); i<n; ++i ) loader.AddVariable(variables[i]);
    for ( unsigned i=0, n=allVars.size(); i<n; ++i ) {
      bool isUsed = false;
      for ( unsigned j=0, m=variables.size(); j<m; ++j ) {
        if ( variables[j] == allVars[i] ) { isUsed = true; break; }
      }
      if ( !isUsed ) loader.AddSpectator(allVars[i]);
    }

    bookMethods(factory, loader, name);//, variables, name);
  }

  factory.TrainAllMethods();
  factory.TestAllMethods();
  factory.EvaluateAllMethods();

  //c = factory.GetROCCurve(loader);
  //c.Draw();
}
