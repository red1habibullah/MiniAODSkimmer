// -*- C++ -*-
//
// Package:    MiniAODCleanerTest/MiniAODCleaner
// Class:      ElectronCleanedPackedCandidateProducer
// 
/**\class ElectronCleanedPackedCandidateProducer ElectronCleanedPackedCandidateProducer.cc MiniAODCleanerTest/MiniAODCleaner/plugins/ElectronCleanedPackedCandidateProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Redwan Habibullah
//         Created:  Sat, 05 Jun 2021 00:45:17 GMT
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"
#include "FWCore/Framework/interface/EventSetup.h"

#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/JetReco/interface/PFJetCollection.h"
#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/Common/interface/AssociationMap.h"
#include "DataFormats/Common/interface/Ref.h"
#include "DataFormats/Common/interface/RefProd.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "TLorentzVector.h"
#include "TMath.h"
#include "DataFormats/Math/interface/deltaR.h"

//
// class declaration
//

class ElectronCleanedPackedCandidateProducer : public edm::stream::EDProducer<> {
   public:
      explicit ElectronCleanedPackedCandidateProducer(const edm::ParameterSet&);
      ~ElectronCleanedPackedCandidateProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginStream(edm::StreamID) override;
      virtual void produce(edm::Event&, const edm::EventSetup&) override;
      virtual void endStream() override;

      //virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
      //virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
      //virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
      //virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

      // ----------member data ---------------------------
  edm::EDGetTokenT<pat::ElectronRefVector> electronSrc_;
  edm::EDGetTokenT<pat::PackedCandidateCollection> packedCandSrc_;
  
  edm::ParameterSet* cfg_;

};

//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
ElectronCleanedPackedCandidateProducer::ElectronCleanedPackedCandidateProducer(const edm::ParameterSet& iConfig):
  electronSrc_(consumes<pat::ElectronRefVector>(iConfig.getParameter<edm::InputTag>("electronSrc"))),
  packedCandSrc_(consumes<pat::PackedCandidateCollection>(iConfig.getParameter<edm::InputTag>("packedCandSrc")))
{
  //register your products
  cfg_ = const_cast<edm::ParameterSet*>(&iConfig);
  
  produces<pat::PackedCandidateCollection >("packedPFCandidatesElectronCleaned");
  //now do what ever other initialization is needed
  
}


ElectronCleanedPackedCandidateProducer::~ElectronCleanedPackedCandidateProducer()
{
 
   // do anything here that needs to be done at destruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
ElectronCleanedPackedCandidateProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   

   
   edm::Handle<pat::ElectronRefVector> electrons;
   iEvent.getByToken(electronSrc_, electrons);

   edm::Handle<pat::PackedCandidateCollection> packedCands;
   iEvent.getByToken(packedCandSrc_, packedCands);
   std::unique_ptr<pat::PackedCandidateCollection> packedCandsExcludingElectrons(new pat::PackedCandidateCollection);

   //Get the PFCandidates being pointed to by pat::Electrons
   std::vector<reco::CandidatePtr> eSourceCandPtrs;
   
   if (electrons.isValid())
     {
       for (pat::ElectronRefVector::const_iterator iElectron = electrons->begin(); iElectron != electrons->end(); ++iElectron)
	 {

	   for( unsigned int i=0; i < (*iElectron)->numberOfSourceCandidatePtrs(); ++i)
	     {
	       eSourceCandPtrs.push_back((*iElectron)->sourceCandidatePtr(i));
	     }
	   
	   
	   
	 }
     }
   for( size_t i = 0; i < packedCands->size(); ++i)
     {
       //bool ElectronFlag= false;
       //if((*packedCands)[i].isElectron())
       if((*packedCands)[i].pdgId()==11)
	 {
	   reco::CandidatePtr ptr2PF(packedCands,i);
	   std::cout<< " ====packed Candidate is an electron=== "<<std::endl;
	   if (std::find(eSourceCandPtrs.begin(),eSourceCandPtrs.end(),ptr2PF) != eSourceCandPtrs.end())
	     {

	       //ElectronFlag=true;
	       std::cout<< " ***packed Candidate and Electron points to same PFCandidate*** "<<std::endl; 
	     }	   
	   else
	     {
	       packedCandsExcludingElectrons->push_back((*packedCands)[i]);
	     }
	 }
       else
	 {
	   packedCandsExcludingElectrons->push_back((*packedCands)[i]);
	 }
	 
     
     }
   


   iEvent.put(std::move(packedCandsExcludingElectrons),"packedPFCandidatesElectronCleaned");

}

// ------------ method called once each stream before processing any runs, lumis or events  ------------
void
ElectronCleanedPackedCandidateProducer::beginStream(edm::StreamID)
{
}

// ------------ method called once each stream after processing all runs, lumis and events  ------------
void
ElectronCleanedPackedCandidateProducer::endStream() {
}

// ------------ method called when starting to processes a run  ------------
/*
void
ElectronCleanedPackedCandidateProducer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a run  ------------
/*
void
ElectronCleanedPackedCandidateProducer::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when starting to processes a luminosity block  ------------
/*
void
ElectronCleanedPackedCandidateProducer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
ElectronCleanedPackedCandidateProducer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
ElectronCleanedPackedCandidateProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(ElectronCleanedPackedCandidateProducer);
