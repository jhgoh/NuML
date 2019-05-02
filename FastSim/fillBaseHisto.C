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
	//TFile* f1 = TFile::Open("input1.root");
	//TTree* t1 = (TTree*)f1->Get("tree");
	//const int nEvent1 = t1->GetEntries();
	const int nEvent1 = 1000; // comment out this line if your tree exists
	for ( int i=0; i<nEvent1; ++i ) {
		vars[Key::En1] = gRandom->Uniform(0,10);
		vars[Key::En2] = gRandom->Uniform(0,6);
		vars[Key::dt] = gRandom->Uniform(0,1000);

		const double x1 = gRandom->Uniform(-2000, 2000);
		const double x2 = gRandom->Uniform(-2000, 2000);
		const double y1 = gRandom->Uniform(-2000, 2000);
		const double y2 = gRandom->Uniform(-2000, 2000);
		const double z1 = gRandom->Uniform(-2000, 2000);
		const double z2 = gRandom->Uniform(-2000, 2000);
		if ( std::hypot(x1, y1) > 2000 ) { --i; continue; }
		if ( std::hypot(x2, y2) > 2000 ) { --i; continue; }

		vars[Key::r1] = std::hypot(x1, y1);
		vars[Key::r2] = std::hypot(x2, y2);
		vars[Key::phi1] = std::atan2(y1, x1);
		vars[Key::phi2] = std::atan2(y2, x2);
		vars[Key::z1] = z1;
		vars[Key::z2] = z2;
		vars[Key::dr] = std::sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)+(z1-z2)*(z1-z2));

		hSig->Fill(vars);
	}

	// Loop over your background events
	//TFile* f2 = TFile::Open("input2.root");
	//TTree* t2 = (TTree*)f2->Get("tree");
	//const int nEvent2 = t2->GetEntries();
	const int nEvent2 = 100000; // comment out this line if your tree exists
	for ( int i=0; i<nEvent2; ++i ) {
		vars[Key::En1] = gRandom->Uniform(0,10);
		vars[Key::En2] = gRandom->Uniform(0,6);
		vars[Key::dt] = gRandom->Uniform(0,1000);

		const double x1 = gRandom->Uniform(-2000, 2000);
		const double x2 = gRandom->Uniform(-2000, 2000);
		const double y1 = gRandom->Uniform(-2000, 2000);
		const double y2 = gRandom->Uniform(-2000, 2000);
		const double z1 = gRandom->Uniform(-2000, 2000);
		const double z2 = gRandom->Uniform(-2000, 2000);
		if ( std::hypot(x1, y1) > 2000 ) { --i; continue; }
		if ( std::hypot(x2, y2) > 2000 ) { --i; continue; }

		vars[Key::r1] = std::hypot(x1, y1);
		vars[Key::r2] = std::hypot(x2, y2);
		vars[Key::phi1] = std::atan2(y1, x1);
		vars[Key::phi2] = std::atan2(y2, x2);
		vars[Key::z1] = z1;
		vars[Key::z2] = z2;
		vars[Key::dr] = std::sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)+(z1-z2)*(z1-z2));

		hBkg1->Fill(vars);
	}

	// Finish
	hSig->Write();
	hBkg1->Write();
	f->Close();
}
