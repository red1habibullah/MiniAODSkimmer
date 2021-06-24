// -*- C++ -*-
//
// Package:    MiniAODCleanerTest/MiniAODCleaner
// Class:      MuonCleanedPackedCandidateProducer
// 
/**\class MuonCleanedPackedCandidateProducer MuonCleanedPackedCandidateProducer.cc MiniAODCleanerTest/MiniAODCleaner/plugins/MuonCleanedPackedCandidateProducer.cc

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

class MuonCleanedPackedCandidateProducer : public edm::stream::EDProducer<> {
   public:
      explicit MuonCleanedPackedCandidateProducer(const edm::ParameterSet&);
      ~MuonCleanedPackedCandidateProducer();

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
  edm::EDGetTokenT<pat::MuonRefVector> muonSrc_;
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
MuonCleanedPackedCandidateProducer::MuonCleanedPackedCandidateProducer(const edm::ParameterSet& iConfig):
  muonSrc_(consumes<pat::MuonRefVector>(iConfig.getParameter<edm::InputTag>("muonSrc"))),
  packedCandSrc_(consumes<pat::PackedCandidateCollection>(iConfig.getParameter<edm::InputTag>("packedCandSrc")))
{
  //register your products
  cfg_ = const_cast<edm::ParameterSet*>(&iConfig);
  
  produces<pat::PackedCandidateCollection >("packedPFCandidatesMuonCleaned");
  //now do what ever other initialization is needed
  
}


MuonCleanedPackedCandidateProducer::~MuonCleanedPackedCandidateProducer()
{
 
   // do anything here that needs to be done at destruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
MuonCleanedPackedCandidateProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   

   
   edm::Handle<pat::MuonRefVector> muons;
   iEvent.getByToken(muonSrc_, muons);

   edm::Handle<pat::PackedCandidateCollection> packedCands;
   iEvent.getByToken(packedCandSrc_, packedCands);
   std::unique_ptr<pat::PackedCandidateCollection> packedCandsExcludingMuons(new pat::PackedCandidateCollection);

   //Get the PFCandidates being pointed to by pat::Muons
   std::vector<reco::CandidatePtr> eSourceCandPtrs;
   
   if (muons.isValid())
     {
       for (pat::MuonRefVector::const_iterator iMuon = muons->begin(); iMuon != muons->end(); ++iMuon)
	 {

	   for( unsigned int i=0; i < (*iMuon)->numberOfSourceCandidatePtrs(); ++i)
	     {
	       eSourceCandPtrs.push_back((*iMuon)->sourceCandidatePtr(i));
	     }
	   
	   
	   
	 }
     }
   for( size_t i = 0; i < packedCands->size(); ++i)
     {
       //bool MuonFlag= false;
       //if((*packedCands)[i].isMuon())
       if((*packedCands)[i].pdgId()==13)
	 {
	   std::cout<< " packed Candidate is a Muon "<<std::endl;
	   reco::CandidatePtr ptr2PF(packedCands,i);
	   
	   if (std::find(eSourceCandPtrs.begin(),eSourceCandPtrs.end(),ptr2PF) != eSourceCandPtrs.end())
	     {

	       //MuonFlag=true;
	       std::cout<< " packed Candidate and Muon points to same PFCandidate "<<std::endl; 
	     }	   
	   else
	     {
	       packedCandsExcludingMuons->push_back((*packedCands)[i]);
	     }
	 }
       else
	 {
	   packedCandsExcludingMuons->push_back((*packedCands)[i]);
	 }
	 
     
     }
   


   iEvent.put(std::move(packedCandsExcludingMuons),"packedPFCandidatesMuonCleaned");

}

// ------------ method called once each stream before processing any runs, lumis or events  ------------
void
MuonCleanedPackedCandidateProducer::beginStream(edm::StreamID)
{
}

// ------------ method called once each stream after processing all runs, lumis and events  ------------
void
MuonCleanedPackedCandidateProducer::endStream() {
}

// ------------ method called when starting to processes a run  ------------
/*
void
MuonCleanedPackedCandidateProducer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a run  ------------
/*
void
MuonCleanedPackedCandidateProducer::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when starting to processes a luminosity block  ------------
/*
void
MuonCleanedPackedCandidateProducer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
MuonCleanedPackedCandidateProducer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
MuonCleanedPackedCandidateProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(MuonCleanedPackedCandidateProducer);
