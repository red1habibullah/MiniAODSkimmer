#include "MiniAODSkimmer/MiniAODCleaner/interface/LumiSummaryBranches.h"

LumiSummaryBranches::LumiSummaryBranches(TTree * tree, const edm::ParameterSet& iConfig, edm::ConsumesCollector cc):
    genEventInfoToken_(cc.consumes<GenEventInfoProduct>(iConfig.getParameter<edm::InputTag>("genEventInfo"))),
    lheEventProductToken_(cc.consumes<LHEEventProduct>(iConfig.getParameter<edm::InputTag>("lheEventProduct")))
{
  hasSummary_ = iConfig.exists("nevents") && iConfig.exists("summedWeights");
  doGenWeights_ = iConfig.exists("doGenWeights") ? iConfig.getParameter<bool>("doGenWeights") : true;
  if (hasSummary_) {
    neventsToken_ = cc.consumes<int, edm::InLumi>(iConfig.getParameter<edm::InputTag>("nevents"));
    summedWeightsToken_ = cc.consumes<float, edm::InLumi>(iConfig.getParameter<edm::InputTag>("summedWeights"));
    if (doGenWeights_) summedGenWeightsToken_ = cc.consumes<std::vector<float>, edm::InLumi>(iConfig.getParameter<edm::InputTag>("summedGenWeights"));
  }
  // add branches
  tree->Branch("run", &runBranch_, "run/I");
  tree->Branch("lumi", &lumiBranch_, "lumi/I");
  tree->Branch("nevents", &neventsBranch_, "nevents/I");
  tree->Branch("summedWeights", &summedWeightsBranch_, "summedWeights/F");
  if (doGenWeights_) tree->Branch("summedGenWeights", &summedGenWeightsBranch_);
}

void LumiSummaryBranches::beginLumi(const edm::LuminosityBlock& iEvent)
{
  runBranch_ = iEvent.run();
  lumiBranch_ = iEvent.luminosityBlock();
  if (hasSummary_) {
    edm::Handle<int> neventsHandle;
    iEvent.getByToken(neventsToken_, neventsHandle);

    edm::Handle<float> summedWeightsHandle;
    iEvent.getByToken(summedWeightsToken_, summedWeightsHandle);

    hasSummary_ = neventsHandle.isValid() and summedWeightsHandle.isValid();

    neventsBranch_ = hasSummary_ ? *neventsHandle : 0;
    summedWeightsBranch_ = hasSummary_ ? *summedWeightsHandle : 0;

    if (doGenWeights_) {
      edm::Handle<std::vector<float> > summedGenWeightsHandle;
      iEvent.getByToken(summedGenWeightsToken_, summedGenWeightsHandle);
      if (hasSummary_) summedGenWeightsBranch_ = *summedGenWeightsHandle;
    }
  }
  else {
    neventsBranch_ = 0;
    summedWeightsBranch_ = 0;
    if (doGenWeights_) summedGenWeightsBranch_.clear();
  }
}

void LumiSummaryBranches::fill(const edm::Event& iEvent)
{
  if (hasSummary_) return;

  edm::Handle<GenEventInfoProduct> genEventInfo;
  iEvent.getByToken(genEventInfoToken_, genEventInfo);

  neventsBranch_++;
  Float_t genWeight = 0.;
  if (genEventInfo.isValid()) {
      genWeight = genEventInfo->weight();
  }
  summedWeightsBranch_ += genWeight;

  if (doGenWeights_) {
    edm::Handle<LHEEventProduct> lheInfo;
    iEvent.getByToken(lheEventProductToken_, lheInfo);

    if (lheInfo.isValid()) {
      for (size_t i=0; i<lheInfo->weights().size(); ++i) {
        if (summedGenWeightsBranch_.size()<i+1) {
          summedGenWeightsBranch_.push_back(lheInfo->weights()[i].wgt);
        }
        else {
          summedGenWeightsBranch_[i] += lheInfo->weights()[i].wgt;
        }
      }
    }
  }

}

