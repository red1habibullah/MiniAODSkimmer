#include "MiniAODSkimmer/MiniAODCleaner/interface/LumiTree.h"

LumiTree::LumiTree(const edm::ParameterSet &iConfig)
{
    // Declare use of TFileService
    usesResource("TFileService");

    edm::Service<TFileService> FS;

    // create lumitree_
    lumitree_ = FS->make<TTree>("LumiTree", "LumiTree");
    lumiSummary_ = std::unique_ptr<LumiSummaryBranches>(new LumiSummaryBranches(lumitree_, iConfig, consumesCollector()));
}

LumiTree::~LumiTree() { }

void LumiTree::beginJob() { }

void LumiTree::beginLuminosityBlock(edm::LuminosityBlock const& iEvent, edm::EventSetup const& iSetup) {
    lumiSummary_->beginLumi(iEvent);
}

void LumiTree::endLuminosityBlock(edm::LuminosityBlock const& iEvent, edm::EventSetup const& iSetup) {
    lumitree_->Fill();
}

void LumiTree::endJob() { }

void LumiTree::analyze(const edm::Event &iEvent, const edm::EventSetup &iSetup) {
    lumiSummary_->fill(iEvent);
}
