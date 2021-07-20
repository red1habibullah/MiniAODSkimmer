// -*- C++ -*-
//
// Package:    RecoJets/JetProducers
// Class:      ElectronFilterMedium
// 
/**\class ElectronFilterMedium ElectronFilterMedium.cc RecoJets/JetProducers/plugins/ElectronFilterMedium.cc

 Description: [one line class summary]
Creates a collection of electrons passing the Loose Electron ID.returns true if at least one electron passes
The values have been updated for 2017 MC/Data 
 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Redwan Habibullah
//         Created:  Sat, 24 Feb 2018 03:28:23 GMT
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDFilter.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "DataFormats/EgammaCandidates/interface/GsfElectron.h"
#include "DataFormats/PatCandidates/interface/Electron.h"

#include "PhysicsTools/SelectorUtils/interface/CutApplicatorBase.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectronFwd.h"

#include "DataFormats/Common/interface/ValueMap.h"
#include "TLorentzVector.h"


#include "TMath.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectronCore.h"

#include "DataFormats/EgammaCandidates/interface/Conversion.h"
//#include "RecoEgamma/EgammaTools/interface/ConversionTools.h"
#include "CommonTools/Egamma/interface/ConversionTools.h"

//#include "RecoEgamma/EgammaTools/interface/EffectiveAreas.h"
#include "CommonTools/Egamma/interface/EffectiveAreas.h"

#include "PhysicsTools/SelectorUtils/interface/CutApplicatorWithEventContentBase.h"

#include "DataFormats/EgammaCandidates/interface/ConversionFwd.h"
#include "DataFormats/TrackReco/interface/TrackBase.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "DataFormats/Common/interface/RefToBaseVector.h"

#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/MET.h"
using namespace edm;
using namespace std;
//
// class declaration
//

class ElectronFilterMedium : public edm::stream::EDFilter<> {
public:
      explicit ElectronFilterMedium(const edm::ParameterSet&);
  ~ElectronFilterMedium();
  
  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  float dEtaInSeed(pat::ElectronCollection::const_iterator ele);
  float GsfEleEInverseMinusPInverse(pat::ElectronCollection::const_iterator ele);
  
  int GsfEleMissingHitsCut(pat::ElectronCollection::const_iterator ele);
  
  double GsfEleEffAreaPFIsoCut(pat::ElectronCollection::const_iterator ele,edm::Event& iEvent);
  bool GsfEleConversionVetoCut(pat::ElectronCollection::const_iterator ele,edm::Event& iEvent);
  
  
private:
  virtual void beginStream(edm::StreamID) override;
  virtual bool filter(edm::Event&, const edm::EventSetup&) override;
  virtual void endStream() override;
  
  //virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
  //virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
  //virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
  //virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&

  // ----------member data ---------------------------
  float dEtaInSeedCut;
  float GsfEleEInverseMinusPInverseCut;
  float effA;
  float rhos;
  edm::EDGetTokenT<pat::ElectronCollection> electronSrc_;
  edm::EDGetTokenT<double>rho_;
  edm::EDGetTokenT<reco::ConversionCollection> convs_;
  edm::EDGetTokenT<reco::BeamSpot> thebs_;
  edm::EDGetTokenT<reco::VertexCollection> vtx_;
  edm::EDGetTokenT<reco::GsfTrackCollection> trk_;
  std::vector<double> Etamin = {0.0000,1.000,1.4790,2.000,2.2000,2.3000,2.4000};
  std::vector<double> Etamax ={1.0000,1.4790,2.0000,2.2000,2.3000,2.4000,5.000};
  std::vector<double> EA = {0.1703,0.1715,0.1213,0.1635,0.1937,0.2393};
  int EBcount= 0;
  int EEcount= 0;
  int Tcount= 0;
  unsigned int EBpcount_c = 0;
  unsigned int EEpcount_c = 0;
  unsigned int Passcount= 0;  
  math::XYZPointF p1;
  math::XYZPoint p2;
  double dz;
  double dxy;
  
  
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
ElectronFilterMedium::ElectronFilterMedium(const edm::ParameterSet& iConfig):
  electronSrc_(consumes<pat::ElectronCollection>(iConfig.getParameter<edm::InputTag>("electrons"))),
  rho_(consumes<double>(iConfig.getParameter<edm::InputTag>("Rho"))),
  convs_(consumes<reco::ConversionCollection>(iConfig.getParameter<edm::InputTag>("conv"))),
  thebs_(consumes<reco::BeamSpot>(iConfig.getParameter<edm::InputTag>("BM"))),
  vtx_ (consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("vertex")))
  //trk_(consumes<reco::GsfTrackCollection>(iConfig.getParameter<edm::InputTag>("Tracks")))
{
  //now do what ever initialization is needed
  //produces<reco::GsfElectronCollection>( "LooseElectron" );
  produces<pat::ElectronCollection>("MiniMediumElectron");
  produces<pat::ElectronRefVector>("MediumElectronRef");
}


ElectronFilterMedium::~ElectronFilterMedium()
{
  
  // do anything here that needs to be done at destruction time
  // (e.g. close files, deallocate resources etc.)
  
}


//
// member functions
//
float ElectronFilterMedium::dEtaInSeed (pat::ElectronCollection::const_iterator ele){
  return ele->superCluster().isNonnull() && ele->superCluster()->seed().isNonnull() ?
    ele->deltaEtaSuperClusterTrackAtVtx() - ele->superCluster()->eta() + ele->superCluster()->seed()->eta() : std::numeric_limits<float>::max();
}
float ElectronFilterMedium::GsfEleEInverseMinusPInverse (pat::ElectronCollection::const_iterator ele)
{
  const float ecal_energy_inverse = 1.0/ele->ecalEnergy();
  const float eSCoverP = ele->eSuperClusterOverP();
  return std::abs(1.0 - eSCoverP)*ecal_energy_inverse;
}
int ElectronFilterMedium::GsfEleMissingHitsCut(pat::ElectronCollection::const_iterator ele)
{

  constexpr reco::HitPattern::HitCategory missingHitType =
    reco::HitPattern::MISSING_INNER_HITS;
    const unsigned mHits =
      ele->gsfTrack()->hitPattern().numberOfAllHits(missingHitType);
    return mHits;
}


bool ElectronFilterMedium::GsfEleConversionVetoCut(pat::ElectronCollection::const_iterator ele ,edm::Event& iEvent)
{

  edm::Handle<reco::ConversionCollection> convs;
  iEvent.getByToken(convs_,convs);
  edm::Handle<reco::BeamSpot> thebs;
  iEvent.getByToken(thebs_,thebs);
  if(thebs.isValid() && convs.isValid() ) {
    return !ConversionTools::hasMatchedConversion(*ele,*convs,
						  thebs->position());
  } else {
    edm::LogWarning("GsfEleConversionVetoCut")
      << "Couldn't find a necessary collection, returning true!";
    return true;
  }

}

// ------------ method called on each new Event  ------------
bool ElectronFilterMedium::filter(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  using namespace reco;
   unsigned int EBpcount = 0;
   unsigned int EEpcount = 0;
  Handle<pat::ElectronCollection> electrons;
  iEvent.getByToken(electronSrc_,electrons);
  unique_ptr<pat::ElectronCollection> passedelectrons(new pat::ElectronCollection);
  unique_ptr<pat::ElectronRefVector> passedelectronRef(new pat::ElectronRefVector);
  
  Handle<reco::VertexCollection> Vertex;
  iEvent.getByToken(vtx_,Vertex);
  
  edm::Handle<double>_rhoHandle;
  iEvent.getByToken(rho_,_rhoHandle);

  for(pat::ElectronCollection::const_iterator iele = electrons->begin() ; iele !=electrons->end(); ++iele)
    { ++Tcount;
    
      pat::ElectronRef ERef(electrons,iele-electrons->begin());

      dEtaInSeedCut =abs(dEtaInSeed(iele));
      GsfEleEInverseMinusPInverseCut = GsfEleEInverseMinusPInverse(iele);
      
      
      
      
      //-------------------The new H/E variables------------//
      double HoE=iele->hadronicOverEm();
      double E_c = iele->superCluster()->energy();
      double rho = _rhoHandle.isValid() ? (*_rhoHandle) : 0;    
      bool isPassConVeto = iele->passConversionVeto();

      p1 = iele->trackPositionAtVtx();
      for(unsigned j= 0;j< Vertex->size();j++)
	{
	  p2=(Vertex->at(0)).position();
      	}      
      dz = abs(p1.z()-p2.z());
      dxy = sqrt((p1.x()-p2.x())*(p1.x()-p2.x()) + (p1.y()-p2.y())*(p1.y()-p2.y()));
      
      
      if( iele->isEB())	{++EBcount;
        
	  
	if( (iele->full5x5_sigmaIetaIeta()<0.0106)  && (HoE < (0.046 + 1.16/E_c + 0.0324*rho/E_c)) && (abs(iele->deltaPhiSuperClusterTrackAtVtx()) <0.0547) && (GsfEleEInverseMinusPInverseCut < 0.184) && (dEtaInSeedCut < 0.0032) && (GsfEleMissingHitsCut(iele) <= 1 ) && /*(GsfEleConversionVetoCut(iele,iEvent))*/ (isPassConVeto==true) && (iele->pt()>3))
	    {
	      passedelectrons->push_back(*iele);
	      passedelectronRef->push_back(ERef);
	      ++EBpcount;
	      ++EBpcount_c;
	    }
	  
	}
      if(iele->isEE())
	
	{++EEcount;
	 
	  if((iele->full5x5_sigmaIetaIeta()<0.0387) && (HoE < (0.0275 + 2.52/E_c + 0.183*rho/E_c)) && (abs(iele->deltaPhiSuperClusterTrackAtVtx()) <0.0394) && (GsfEleEInverseMinusPInverseCut < 0.0721) &&(dEtaInSeedCut <0.00632) && (GsfEleMissingHitsCut(iele) <= 1 ) && /*(GsfEleConversionVetoCut(iele,iEvent))*/ (isPassConVeto==true) && (iele->pt()>3) )

	    {


	      passedelectrons->push_back(*iele);
	      passedelectronRef->push_back(ERef);
	      //cout<< "EEPushback" <<endl;
	      ++EEpcount;
	      ++EEpcount_c;
	    }

	}


    }


  //iEvent.put(move(passedelectrons), "LooseElectron");
  iEvent.put(move(passedelectrons),"MiniMediumElectron");
  iEvent.put(move(passedelectronRef),"MediumElectronRef");
  return true;
  //else return false;
}

// ------------ method called once each stream before processing any runs, lumis or events  ------------
void
ElectronFilterMedium::beginStream(edm::StreamID)
{
}

// ------------ method called once each stream after processing all runs, lumis and events  ------------
void
ElectronFilterMedium::endStream() {
}

// ------------ method called when starting to processes a run  ------------
/*
  void
  ElectronFilterMedium::beginRun(edm::Run const&, edm::EventSetup const&)
{ 
}
*/
 
// ------------ method called when ending the processing of a run  ------------
/*
void
ElectronFilterMedium::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when starting to processes a luminosity block  ------------
/*
void
ElectronFilterMedium::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
ElectronFilterMedium::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
ElectronFilterMedium::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}
//define this as a plug-in
DEFINE_FWK_MODULE(ElectronFilterMedium);
