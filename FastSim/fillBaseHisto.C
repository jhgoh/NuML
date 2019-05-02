#include <THnSparse.h>
#include <TFile.h>
#include <TTree.h>
#include <TAxis.h>
#include <iostream>

void fillBaseHisto()
{
  // Define variable binning and range
  // Variables: E1, E2, dt, dr, x1, y1, z1, x2, y2, z2,
  const int nDim = 10;
  const char* varNames[nDim] = {"En1", "En2", "dt", "dr", "x1", "y1", "z1", "x2", "y2", "z2"};
  struct Key { enum    { E1,  E2,   dt,   dr,    x1,    y1,    z1,    x2,    y2,    z2}; };
  int    nbins[nDim] = { 12,   6,   20,   20,    20,    20,    25,    20,    20,    25};
  double xmins[nDim] = {  0,   0,    0,    0, -2000, -2000, -2500, -2000, -2000, -2500};
  double xmaxs[nDim] = { 12,   6, 2000, 5000,  2000,  2000,  2500,  2000,  2000,  2500};
  double vars[nDim];

  // Prepare output. hSig for signal, hBkg1 for the 1st background source
  TFile* f = TFile::Open("hist.root", "recreate");
  THnSparseD* hSig  = new THnSparseD("hSig" , "signal histogram"     , nDim, nbins, xmins, xmaxs);
  THnSparseD* hBkg1 = new THnSparseD("hBkg1", "background1 histogram", nDim, nbins, xmins, xmaxs);
  for ( int i=0; i<nDim; ++i ) {
    hSig->GetAxis(i)->SetName(varNames[i]);
    hBkg1->GetAxis(i)->SetName(varNames[i]);
    hSig->GetAxis(i)->SetTitle(varNames[i]);
    hBkg1->GetAxis(i)->SetTitle(varNames[i]);
  }

  /********************************************************************/
  /*                 Please complete lines below                      */
  /********************************************************************/

  // Loop over your signal events
  TFile* f1 = TFile::Open("input1.root"); // input file for the signal
  TTree* t1 = (TTree*)f1->Get("tree"); // probably you have different name of the tree
  t1->SetBranchAddress("en1"     , &vars[Key::E1]);
  t1->SetBranchAddress("en2"     , &vars[Key::E2]);
  t1->SetBranchAddress("dt"      , &vars[Key::dt]);
  t1->SetBranchAddress("dr"      , &vars[Key::dr]);
  t1->SetBranchAddress("s1_vertx", &vars[Key::x1]);
  t1->SetBranchAddress("s1_verty", &vars[Key::y1]);
  t1->SetBranchAddress("s1_vertz", &vars[Key::z1]);
  t1->SetBranchAddress("s2_vertx", &vars[Key::x2]);
  t1->SetBranchAddress("s2_verty", &vars[Key::y2]);
  t1->SetBranchAddress("s2_vertz", &vars[Key::z2]);
  const int nEvent1 = t1->GetEntries();
  for ( int i=0; i<nEvent1; ++i ) {
    t1->GetEntry(i);
    hSig->Fill(vars);
  }

  // Loop over your background events
  TFile* f2 = TFile::Open("input2.root"); // input file for the bkg
  TTree* t2 = (TTree*)f2->Get("tree"); // probably you have different name of the tree
  t2->SetBranchAddress("en1"     , &vars[Key::E1]);
  t2->SetBranchAddress("en2"     , &vars[Key::E2]);
  t2->SetBranchAddress("dt"      , &vars[Key::dt]);
  t2->SetBranchAddress("dr"      , &vars[Key::dr]);
  t2->SetBranchAddress("s1_vertx", &vars[Key::x1]);
  t2->SetBranchAddress("s1_verty", &vars[Key::y1]);
  t2->SetBranchAddress("s1_vertz", &vars[Key::z1]);
  t2->SetBranchAddress("s2_vertx", &vars[Key::x2]);
  t2->SetBranchAddress("s2_verty", &vars[Key::y2]);
  t2->SetBranchAddress("s2_vertz", &vars[Key::z2]);
  const int nEvent2 = t2->GetEntries();
  for ( int i=0; i<nEvent2; ++i ) {
    t2->GetEntry(i);
    hBkg1->Fill(vars);
  }

  // Finish
  hSig->Write();
  hBkg1->Write();
  f->Close();
}
