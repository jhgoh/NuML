#include <THnSparse.h>
#include <iostream>

void fillBaseHisto()
{
	// Define variable binning and range
	// Variables: En1, En2, dt, dr, r1, phi1, z1, r2, phi2, z2, 
	const int nDim = 10;
	const double pi = 3.1415927;
	const char* varNames[nDim] = {"En1", "En2", "dt", "dr", "r1", "phi1", "z1", "r2", "phi2", "z2"};
	struct Key { enum {En1, En2, dt, dr, r1, phi1, z1, r2, phi2, z2}; }; 
	int    nbins[nDim] = {12, 6,   20,   20,   10,  10,    10,   10,  10,    10};
	double xmins[nDim] = { 0, 0,    0,    0,    0, -pi, -2500,    0, -pi, -2500};
	double xmaxs[nDim] = {12, 6, 2000, 5000, 2000,  pi,  2500, 2000,  pi,  2500};
	double vars[nDim];
	double x1, y1, x2, y2;

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
	t1->SetBranchAddress("en1", &vars[Key::En1]);
	t1->SetBranchAddress("en2", &vars[Key::En2]);
	t1->SetBranchAddress("dt", &vars[Key::dt]);
	t1->SetBranchAddress("dr", &vars[Key::dr]);
	t1->SetBranchAddress("s1_vertx", &x1);
	t1->SetBranchAddress("s1_verty", &y1);
	t1->SetBranchAddress("s1_vertz", &vars[Key::z1]);
	t1->SetBranchAddress("s2_vertx", &x2);
	t1->SetBranchAddress("s2_verty", &y2);
	t1->SetBranchAddress("s2_vertz", &vars[Key::z2]);
	const int nEvent1 = t1->GetEntries();
	for ( int i=0; i<nEvent1; ++i ) {
		vars[Key::r1] = std::hypot(x1, y1);
		vars[Key::r2] = std::hypot(x2, y2);
		vars[Key::phi1] = std::atan2(y1, x1);
		vars[Key::phi2] = std::atan2(y2, x2);

		hSig->Fill(vars);
	}

	// Loop over your background events
	TFile* f2 = TFile::Open("input2.root"); // input file for the bkg
	TTree* t2 = (TTree*)f2->Get("tree"); // probably you have different name of the tree
	const int nEvent2 = t2->GetEntries();
	t2->SetBranchAddress("en1", &vars[Key::En1]);
	t2->SetBranchAddress("en2", &vars[Key::En2]);
	t2->SetBranchAddress("dt", &vars[Key::dt]);
	t2->SetBranchAddress("dr", &vars[Key::dr]);
	t2->SetBranchAddress("s1_vertx", &x1);
	t2->SetBranchAddress("s1_verty", &y1);
	t2->SetBranchAddress("s1_vertz", &vars[Key::z1]);
	t2->SetBranchAddress("s2_vertx", &x2);
	t2->SetBranchAddress("s2_verty", &y2);
	t2->SetBranchAddress("s2_vertz", &vars[Key::z2]);
	for ( int i=0; i<nEvent2; ++i ) {
		vars[Key::r1] = std::hypot(x1, y1);
		vars[Key::r2] = std::hypot(x2, y2);
		vars[Key::phi1] = std::atan2(y1, x1);
		vars[Key::phi2] = std::atan2(y2, x2);

		hBkg1->Fill(vars);
	}

	// Finish
	hSig->Write();
	hBkg1->Write();
	f->Close();
}
