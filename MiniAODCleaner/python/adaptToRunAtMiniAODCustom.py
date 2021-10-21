import FWCore.ParameterSet.Config as cms
import six

import PhysicsTools.PatAlgos.tools.helpers as configtools
from PhysicsTools.PatAlgos.tools.helpers import cloneProcessingSnippet
from PhysicsTools.PatAlgos.tools.helpers import massSearchReplaceAnyInputTag
from PhysicsTools.PatAlgos.tools.helpers import removeIfInSequence

##############
#Tools to adapt Tau sequences to run tau ReReco+PAT at MiniAOD samples
#With cleaned PackedPFCandidate Collection
##############



def addTauReRecoCustom(process):
    #PAT
    process.load('PhysicsTools.PatAlgos.producersLayer1.tauProducer_cff')
    process.load('PhysicsTools.PatAlgos.selectionLayer1.tauSelector_cfi')
    process.selectedPatTaus.cut="pt > 18. && tauID(\'decayModeFindingNewDMs\')> 0.5"
    #Tau RECO
    process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")    
    process.miniAODTausTask = cms.Task(
    process.PFTauTask, 
    process.makePatTausTask,
    process.selectedPatTaus
    
    )
    process.miniAODTausSequence =cms.Sequence(process.miniAODTausTask)
    #######ElectronCleaned#########
    transfermods=[]
    transferlabels=[]
    for mods in process.miniAODTausTask.moduleNames():
        transfermods.append(mods)
    transfermodsnew=[]
    process.miniAODTausTaskElectronCleaned=cms.Task()
    #loop over the modules, rename and remake the task by hand
    for mod in transfermods:
        module=getattr(process,mod)
        transferlabels.append(module.label())
        newmod=module.clone()
        namepostfix='ElectronCleaned'
        newname=mod+namepostfix
        setattr(process,newname,newmod)
        process.miniAODTausTaskElectronCleaned.add(getattr(process,newname))
    for names in process.miniAODTausTaskElectronCleaned.moduleNames():
        if 'ak4PFJetTracksAssociatorAtVertexElectronCleaned' in names or 'pfRecoTauTagInfoProducerElectronCleaned' in names or 'recoTauAK4PFJets08RegionElectronCleaned' in names:
            process.miniAODTausTaskElectronCleaned.remove(getattr(process, names))
    
        
    process.LooseFilter = cms.EDFilter("ElectronFilter",
                                   vertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
                                   Rho = cms.InputTag("fixedGridRhoFastjetAll"),
                                   electrons = cms.InputTag("slimmedElectrons"),
                                   conv = cms.InputTag("reducedConversions"),
                                   BM = cms.InputTag("offlineBeamSpot"),
                                   #Tracks = cms.InputTag("electronGsfTracks"),                                                       
    )    
    process.PackedCandsElectronCleaned =cms.EDProducer(
        'ElectronCleanedPackedCandidateProducer',
        electronSrc = cms.InputTag("LooseFilter","LooseElectronRef"),
        packedCandSrc = cms.InputTag("packedPFCandidates"),
    )
    
    process.electronCleanedPackedCandidateTask=cms.Task(process.LooseFilter,process.PackedCandsElectronCleaned)
    process.miniAODTausTaskElectronCleaned.add(process.electronCleanedPackedCandidateTask)
    
    labelpostfix='ElectronCleaned'
    renamedict={}
    for label in transferlabels:
        renamedict[label]=label+labelpostfix
        #print renamedict
    
    process.miniAODTausSequenceElectronCleaned =  cms.Sequence(process.miniAODTausTaskElectronCleaned)
    for label_old,label_new in renamedict.items():
        #print " old label: ", label_old
        #print "new label: ", label_new
        massSearchReplaceAnyInputTag(process.miniAODTausSequenceElectronCleaned,label_old,label_new)    
        massSearchReplaceAnyInputTag(process.miniAODTausSequenceElectronCleaned,cms.InputTag(label_old,"category"),cms.InputTag(label_new,"category"))    
    #########MuonCleaned########
    process.miniAODTausTaskMuonCleaned=cms.Task()
    for mod in transfermods:
        module=getattr(process,mod)
        #print mod
        #=============== name ==================="
        #print module.label()
        #print "=================== label ================"
        transferlabels.append(module.label())
        newmod=module.clone()
        namepostfix='MuonCleaned'
        newname=mod+namepostfix
        setattr(process,newname,newmod)
        process.miniAODTausTaskMuonCleaned.add(getattr(process,newname))
    for names in process.miniAODTausTaskMuonCleaned.moduleNames():
        if 'ak4PFJetTracksAssociatorAtVertexMuonCleaned' in names or 'pfRecoTauTagInfoProducerMuonCleaned' in names or 'recoTauAK4PFJets08RegionMuonCleaned' in names:
            process.miniAODTausTaskMuonCleaned.remove(getattr(process, names))
    

    
    process.LooseMuonFilter = cms.EDFilter('PATMuonRefSelector',
                                           src = cms.InputTag('slimmedMuons'),
                                           cut = cms.string('pt > 3.0 && isPFMuon && (isGlobalMuon || isTrackerMuon)'),
    )
    
    process.PackedCandsMuonCleaned =cms.EDProducer(
        'MuonCleanedPackedCandidateProducer',
        muonSrc = cms.InputTag("LooseMuonFilter"),
        packedCandSrc = cms.InputTag("packedPFCandidates"),
    )
    
    process.muonCleanedPackedCandidateTask=cms.Task(process.LooseMuonFilter,process.PackedCandsMuonCleaned)
    process.miniAODTausTaskMuonCleaned.add(process.muonCleanedPackedCandidateTask)
    
    labelmupostfix='MuonCleaned'
    renamedictmu={}
    for label in transferlabels:
        renamedictmu[label]=label+labelmupostfix
        #print renamedictmu
    
    process.miniAODTausSequenceMuonCleaned =  cms.Sequence(process.miniAODTausTaskMuonCleaned)
    for label_old,label_new in renamedictmu.items():
        #print " old label: ", label_old
        #print "new label: ", label_new
        massSearchReplaceAnyInputTag(process.miniAODTausSequenceMuonCleaned,label_old,label_new)    
        massSearchReplaceAnyInputTag(process.miniAODTausSequenceMuonCleaned,cms.InputTag(label_old,"category"),cms.InputTag(label_new,"category"))    
    

    ######## Tau-Reco Path ####### 
    process.TauReco = cms.Path(process.miniAODTausSequence)
    process.TauRecoElectronCleaned = cms.Path(process.miniAODTausSequenceElectronCleaned)
    process.TauRecoMuonCleaned = cms.Path(process.miniAODTausSequenceMuonCleaned)
    process.schedule = cms.Schedule(process.TauReco,process.TauRecoElectronCleaned,process.TauRecoMuonCleaned) 
    
    
def convertModuleToMiniAODInput(process, name):
    module = getattr(process, name)
    if hasattr(module, 'particleFlowSrc'):
        if "ElectronCleanedPackedCandidateProducer" in name or "MuonCleanedPackeCandidateProducer" in name:
            module.particleFlowSrc = cms.InputTag("packedPFCandidates", "", "")
        elif "ElectronCleaned" in name:
            module.particleFlowSrc = cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned')
        elif "MuonCleaned" in name:
            module.particleFlowSrc = cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned')
        else:
            module.particleFlowSrc = cms.InputTag("packedPFCandidates", "", "")
    if hasattr(module, 'vertexSrc'):
        module.vertexSrc = cms.InputTag('offlineSlimmedPrimaryVertices')
    if hasattr(module, 'qualityCuts') and hasattr(module.qualityCuts, 'primaryVertexSrc'):
        module.qualityCuts.primaryVertexSrc = cms.InputTag('offlineSlimmedPrimaryVertices')
    
def adaptTauToMiniAODReReco(process, runType, reclusterJets=True):
    #runType=kwargs.pop('runType')
    
    jetCollection = 'slimmedJets'
    # Add new jet collections if reclustering is demanded
    if reclusterJets:
        jetCollection = 'patJetsPAT'
        from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets
        process.ak4PFJetsPAT = ak4PFJets.clone(
            src=cms.InputTag("packedPFCandidates")
        )
        # trivial PATJets
        from PhysicsTools.PatAlgos.producersLayer1.jetProducer_cfi import _patJets
        process.patJetsPAT = _patJets.clone(
            jetSource            = cms.InputTag("ak4PFJetsPAT"),
            addJetCorrFactors    = cms.bool(False),
            jetCorrFactorsSource = cms.VInputTag(),
            addBTagInfo          = cms.bool(False),
            addDiscriminators    = cms.bool(False),
            discriminatorSources = cms.VInputTag(),
            addAssociatedTracks  = cms.bool(False),
            addJetCharge         = cms.bool(False),
            addGenPartonMatch    = cms.bool(False),
            embedGenPartonMatch  = cms.bool(False),
            addGenJetMatch       = cms.bool(False),
            getJetMCFlavour      = cms.bool(False),
            addJetFlavourInfo    = cms.bool(False),
        )
        process.miniAODTausTask.add(process.ak4PFJetsPAT)
        process.miniAODTausTask.add(process.patJetsPAT)
        ###################### ElectronCleaned ######################
        jetCollectionElectronCleaned = 'patJetsPATElectronCleaned'
        jetCollectionMuonCleaned = 'patJetsPATMuonCleaned'
        from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets
        process.ak4PFJetsPATElectronCleaned = ak4PFJets.clone(
            src=cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned')

        )
        from PhysicsTools.PatAlgos.producersLayer1.jetProducer_cfi import _patJets
        process.patJetsPATElectronCleaned = _patJets.clone(
            jetSource            = cms.InputTag("ak4PFJetsPATElectronCleaned"),
            addJetCorrFactors    = cms.bool(False),
            jetCorrFactorsSource = cms.VInputTag(),
            addBTagInfo          = cms.bool(False),
            addDiscriminators    = cms.bool(False),
            discriminatorSources = cms.VInputTag(),
            addAssociatedTracks  = cms.bool(False),
            addJetCharge         = cms.bool(False),
            addGenPartonMatch    = cms.bool(False),
            embedGenPartonMatch  = cms.bool(False),
            addGenJetMatch       = cms.bool(False),
            getJetMCFlavour      = cms.bool(False),
            addJetFlavourInfo    = cms.bool(False),
        )
       
        process.miniAODTausTaskElectronCleaned.add(process.ak4PFJetsPATElectronCleaned)
        process.miniAODTausTaskElectronCleaned.add(process.patJetsPATElectronCleaned)
        
        from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets
        process.ak4PFJetsPATMuonCleaned = ak4PFJets.clone(
            src=cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned')

        )
        from PhysicsTools.PatAlgos.producersLayer1.jetProducer_cfi import _patJets
        process.patJetsPATMuonCleaned = _patJets.clone(
            jetSource            = cms.InputTag("ak4PFJetsPATMuonCleaned"),
            addJetCorrFactors    = cms.bool(False),
            jetCorrFactorsSource = cms.VInputTag(),
            addBTagInfo          = cms.bool(False),
            addDiscriminators    = cms.bool(False),
            discriminatorSources = cms.VInputTag(),
            addAssociatedTracks  = cms.bool(False),
            addJetCharge         = cms.bool(False),
            addGenPartonMatch    = cms.bool(False),
            embedGenPartonMatch  = cms.bool(False),
            addGenJetMatch       = cms.bool(False),
            getJetMCFlavour      = cms.bool(False),
            addJetFlavourInfo    = cms.bool(False),
        )
       
        process.miniAODTausTaskMuonCleaned.add(process.ak4PFJetsPATMuonCleaned)
        process.miniAODTausTaskMuonCleaned.add(process.patJetsPATMuonCleaned)
        
        
    

    process.recoTauAK4Jets08RegionPAT = cms.EDProducer("RecoTauPatJetRegionProducer",
                                                       deltaR = process.recoTauAK4PFJets08Region.deltaR,
                                                       maxJetAbsEta = process.recoTauAK4PFJets08Region.maxJetAbsEta,
                                                       minJetPt = process.recoTauAK4PFJets08Region.minJetPt,
                                                       pfCandAssocMapSrc = cms.InputTag(""),
                                                       pfCandSrc = cms.InputTag("packedPFCandidates"),
                                                       src = cms.InputTag(jetCollection)
                                                       )

    process.recoTauPileUpVertices.src = cms.InputTag("offlineSlimmedPrimaryVertices")
    # Redefine recoTauCommonTask 
    # with redefined region and PU vertices, and w/o track-to-vertex associator and tauTagInfo (the two latter are probably obsolete and not needed at all)
    process.recoTauCommonTask = cms.Task(
        process.recoTauAK4Jets08RegionPAT,
        process.recoTauPileUpVertices
    )
    
    process.recoTauAK4Jets08RegionPATElectronCleaned = cms.EDProducer("RecoTauPatJetRegionProducer",
                                                                      deltaR = process.recoTauAK4PFJets08RegionElectronCleaned.deltaR,
                                                                      maxJetAbsEta = process.recoTauAK4PFJets08RegionElectronCleaned.maxJetAbsEta,
                                                                      minJetPt = process.recoTauAK4PFJets08RegionElectronCleaned.minJetPt,
                                                                      pfCandAssocMapSrc = cms.InputTag(""),
                                                                      pfCandSrc = cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned'),
                                                                      src = cms.InputTag(jetCollectionElectronCleaned)
                                                                  )

    process.recoTauPileUpVerticesElectronCleaned.src = cms.InputTag("offlineSlimmedPrimaryVertices")
    
    
    # Redefine recoTauCommonTask-ElectronCleaned 
    process.miniAODTausTaskElectronCleaned.add(process.recoTauAK4Jets08RegionPATElectronCleaned)
    process.miniAODTausTaskElectronCleaned.add(process.recoTauPileUpVerticesElectronCleaned)
    
    process.recoTauAK4Jets08RegionPATMuonCleaned = cms.EDProducer("RecoTauPatJetRegionProducer",
                                                                      deltaR = process.recoTauAK4PFJets08RegionMuonCleaned.deltaR,
                                                                      maxJetAbsEta = process.recoTauAK4PFJets08RegionMuonCleaned.maxJetAbsEta,
                                                                      minJetPt = process.recoTauAK4PFJets08RegionMuonCleaned.minJetPt,
                                                                      pfCandAssocMapSrc = cms.InputTag(""),
                                                                      pfCandSrc = cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned'),
                                                                      src = cms.InputTag(jetCollectionMuonCleaned)
                                                                  )

    process.recoTauPileUpVerticesMuonCleaned.src = cms.InputTag("offlineSlimmedPrimaryVertices")
    
    # Redefine recoTauCommonTask-MuonCleaned 
    process.miniAODTausTaskMuonCleaned.add(process.recoTauAK4Jets08RegionPATMuonCleaned)
    process.miniAODTausTaskMuonCleaned.add(process.recoTauPileUpVerticesMuonCleaned)
    
    for moduleName in process.TauReco.moduleNames(): 
        convertModuleToMiniAODInput(process, moduleName)
        
    for moduleName in process.TauRecoElectronCleaned.moduleNames(): 
        convertModuleToMiniAODInput(process, moduleName)
        
    for moduleName in process.TauRecoMuonCleaned.moduleNames(): 
        convertModuleToMiniAODInput(process, moduleName)
    
    # Adapt TauPiZeros producer
    process.ak4PFJetsLegacyHPSPiZeros.builders[0].qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
    process.ak4PFJetsLegacyHPSPiZeros.jetSrc = cms.InputTag(jetCollection)

    # Adapt TauPiZeros producer-ElectronCleaned
    process.ak4PFJetsLegacyHPSPiZerosElectronCleaned.builders[0].qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
    process.ak4PFJetsLegacyHPSPiZerosElectronCleaned.jetSrc = cms.InputTag(jetCollectionElectronCleaned)

    # Adapt TauPiZeros producer-MuonCleaned
    process.ak4PFJetsLegacyHPSPiZerosMuonCleaned.builders[0].qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
    process.ak4PFJetsLegacyHPSPiZerosMuonCleaned.jetSrc = cms.InputTag(jetCollectionMuonCleaned)

     

    # Adapt TauChargedHadrons producer
    for builder in process.ak4PFJetsRecoTauChargedHadrons.builders:
        builder.qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
        if builder.name.value() == 'tracks': #replace plugin based on generalTracks by one based on lostTracks
            builder.name = 'lostTracks'
            builder.plugin = 'PFRecoTauChargedHadronFromLostTrackPlugin'
            builder.srcTracks = cms.InputTag("lostTracks")
    process.ak4PFJetsRecoTauChargedHadrons.jetSrc = cms.InputTag(jetCollection)
    
    # Adapt TauChargedHadrons producer-ElectronCleaned
    for builder in process.ak4PFJetsRecoTauChargedHadronsElectronCleaned.builders:
        builder.qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
        if builder.name.value() == 'tracks': #replace plugin based on generalTracks by one based on lostTracks
            builder.name = 'lostTracks'
            builder.plugin = 'PFRecoTauChargedHadronFromLostTrackPlugin'
            builder.srcTracks = cms.InputTag("lostTracks")
    process.ak4PFJetsRecoTauChargedHadronsElectronCleaned.jetSrc = cms.InputTag(jetCollectionElectronCleaned)
    
    # Adapt TauChargedHadrons producer-MuonCleaned
    for builder in process.ak4PFJetsRecoTauChargedHadronsMuonCleaned.builders:
        builder.qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
        if builder.name.value() == 'tracks': #replace plugin based on generalTracks by one based on lostTracks
            builder.name = 'lostTracks'
            builder.plugin = 'PFRecoTauChargedHadronFromLostTrackPlugin'
            builder.srcTracks = cms.InputTag("lostTracks")
    process.ak4PFJetsRecoTauChargedHadronsMuonCleaned.jetSrc = cms.InputTag(jetCollectionMuonCleaned)
    
    
    # Adapt combinatoricRecoTau producer
    process.combinatoricRecoTaus.jetRegionSrc = 'recoTauAK4Jets08RegionPAT'
    process.combinatoricRecoTaus.jetSrc = jetCollection
    # Adapt builders
    for builder in process.combinatoricRecoTaus.builders:
        for name,value in six.iteritems(builder.parameters_()):
            if name == 'qualityCuts':
                builder.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
            elif name == 'pfCandSrc':
                builder.pfCandSrc = 'packedPFCandidates'
                
    # Adapt combinatoricRecoTau producer - ElectronCleaned
    process.combinatoricRecoTausElectronCleaned.jetRegionSrc = 'recoTauAK4Jets08RegionPATElectronCleaned'
    process.combinatoricRecoTausElectronCleaned.jetSrc = jetCollectionElectronCleaned
    # Adapt builders - ElectronCleaned                                                                                                                 
    for builder in process.combinatoricRecoTausElectronCleaned.builders:
        for name,value in six.iteritems(builder.parameters_()):
            if name == 'qualityCuts':
                builder.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
            elif name == 'pfCandSrc':
                builder.pfCandSrc =cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned')
    
    # Adapt combinatoricRecoTau producer - MuonCleaned
    process.combinatoricRecoTausMuonCleaned.jetRegionSrc = 'recoTauAK4Jets08RegionPATMuonCleaned'
    process.combinatoricRecoTausMuonCleaned.jetSrc = jetCollectionMuonCleaned
    # Adapt builders - MuonCleaned                                                                                                                 
    for builder in process.combinatoricRecoTausMuonCleaned.builders:
        for name,value in six.iteritems(builder.parameters_()):
            if name == 'qualityCuts':
                builder.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
            elif name == 'pfCandSrc':
                builder.pfCandSrc =cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned')
    
    # Adapt supported modifiers and remove unsupported ones 
    modifiersToRemove_ = cms.VPSet()

    for mod in process.combinatoricRecoTaus.modifiers:
        if mod.name.value() == 'elec_rej':
            modifiersToRemove_.append(mod)
            continue
        elif mod.name.value() == 'TTIworkaround':
            modifiersToRemove_.append(mod)
            continue
        for name,value in six.iteritems(mod.parameters_()):
            if name == 'qualityCuts':
                mod.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
    for mod in modifiersToRemove_:
        process.combinatoricRecoTaus.modifiers.remove(mod)
    
    modifiersToRemoveElectronCleaned_ = cms.VPSet()  
    
    for mod in process.combinatoricRecoTausElectronCleaned.modifiers:
        if mod.name.value() == 'elec_rej':
            modifiersToRemoveElectronCleaned_.append(mod)
            continue
        elif mod.name.value() == 'TTIworkaround':
            modifiersToRemoveElectronCleaned_.append(mod)
            continue
        for name,value in six.iteritems(mod.parameters_()):
            if name == 'qualityCuts':
                mod.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
    for mod in modifiersToRemoveElectronCleaned_:
        process.combinatoricRecoTausElectronCleaned.modifiers.remove(mod)

    modifiersToRemoveMuonCleaned_ = cms.VPSet()  
    
    for mod in process.combinatoricRecoTausMuonCleaned.modifiers:
        if mod.name.value() == 'elec_rej':
            modifiersToRemoveMuonCleaned_.append(mod)
            continue
        elif mod.name.value() == 'TTIworkaround':
            modifiersToRemoveMuonCleaned_.append(mod)
            continue
        for name,value in six.iteritems(mod.parameters_()):
            if name == 'qualityCuts':
                mod.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
    for mod in modifiersToRemoveMuonCleaned_:
        process.combinatoricRecoTausMuonCleaned.modifiers.remove(mod)

    
    # Redefine tau PV producer
    process.hpsPFTauPrimaryVertexProducer.__dict__['_TypedParameterizable__type'] = 'PFTauMiniAODPrimaryVertexProducer'
    process.hpsPFTauPrimaryVertexProducer.PVTag = 'offlineSlimmedPrimaryVertices'
    process.hpsPFTauPrimaryVertexProducer.packedCandidatesTag = cms.InputTag("packedPFCandidates")
    process.hpsPFTauPrimaryVertexProducer.lostCandidatesTag = cms.InputTag("lostTracks")

    # Redefine tau PV producer-ElectronCleaned
    process.hpsPFTauPrimaryVertexProducerElectronCleaned.__dict__['_TypedParameterizable__type'] = 'PFTauMiniAODPrimaryVertexProducer'
    process.hpsPFTauPrimaryVertexProducerElectronCleaned.PVTag = 'offlineSlimmedPrimaryVertices'
    process.hpsPFTauPrimaryVertexProducerElectronCleaned.packedCandidatesTag = cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned')
    process.hpsPFTauPrimaryVertexProducerElectronCleaned.lostCandidatesTag = cms.InputTag("lostTracks")
    
    # Redefine tau PV producer-MuonCleaned
    process.hpsPFTauPrimaryVertexProducerMuonCleaned.__dict__['_TypedParameterizable__type'] = 'PFTauMiniAODPrimaryVertexProducer'
    process.hpsPFTauPrimaryVertexProducerMuonCleaned.PVTag = 'offlineSlimmedPrimaryVertices'
    process.hpsPFTauPrimaryVertexProducerMuonCleaned.packedCandidatesTag = cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned')
    process.hpsPFTauPrimaryVertexProducerMuonCleaned.lostCandidatesTag = cms.InputTag("lostTracks")
    
    
    # Redefine tau SV producer
    process.hpsPFTauSecondaryVertexProducer = cms.EDProducer("PFTauSecondaryVertexProducer",
                                                             PFTauTag = cms.InputTag("hpsPFTauProducer")
    )
    
    # Redefine tau SV producer-ElectronCleaned
    process.hpsPFTauSecondaryVertexProducerElectronCleaned = cms.EDProducer("PFTauSecondaryVertexProducer",
                                                             PFTauTag = cms.InputTag("hpsPFTauProducerElectronCleaned")
    )
    
    # Redefine tau SV producer-MuonCleaned
    process.hpsPFTauSecondaryVertexProducerMuonCleaned = cms.EDProducer("PFTauSecondaryVertexProducer",
                                                             PFTauTag = cms.InputTag("hpsPFTauProducerMuonCleaned")
    
    )
    # Remove RecoTau producers which are not supported (yet?), i.e. against-e/mu discriminats
    for moduleName in process.TauReco.moduleNames(): 
        if 'ElectronRejection' in moduleName or 'MuonRejection' in moduleName:
            if 'ByDeadECALElectronRejection' in moduleName: continue
            process.miniAODTausTask.remove(getattr(process, moduleName))
    
    
    # Remove RecoTau producers which are not supported (yet?), i.e. against-e/mu discriminats
    for moduleName in process.TauRecoElectronCleaned.moduleNames(): 
        if 'ElectronRejection' in moduleName or 'MuonRejection' in moduleName:
            if 'ByDeadECALElectronRejection' in moduleName: continue
            process.miniAODTausTaskElectronCleaned.remove(getattr(process, moduleName))
    

    # Remove RecoTau producers which are not supported (yet?), i.e. against-e/mu discriminats
    for moduleName in process.TauRecoMuonCleaned.moduleNames(): 
        if 'ElectronRejection' in moduleName or 'MuonRejection' in moduleName:
            if 'ByDeadECALElectronRejection' in moduleName: continue
            process.miniAODTausTaskMuonCleaned.remove(getattr(process, moduleName))
            
            
    
    
    # Instead add against-mu discriminants which are MiniAOD compatible
    #from RecoTauTag.RecoTau.hpsPFTauDiscriminationByAMuonRejectionSimple_cff import hpsPFTauDiscriminationByLooseMuonRejectionSimple, hpsPFTauDiscriminationByTightMuonRejectionSimple
    from RecoTauTag.RecoTau.hpsPFTauDiscriminationByMuonRejectionSimple_cff import hpsPFTauDiscriminationByMuonRejectionSimple
    
    process.hpsPFTauDiscriminationByMuonRejectionSimple = hpsPFTauDiscriminationByMuonRejectionSimple
    #process.hpsPFTauDiscriminationByTightMuonRejectionSimple = hpsPFTauDiscriminationByTightMuonRejectionSimple
    process.miniAODTausTask.add(process.hpsPFTauDiscriminationByMuonRejectionSimple)
    #process.miniAODTausTask.add(process.hpsPFTauDiscriminationByTightMuonRejectionSimple)

    process.hpsPFTauDiscriminationByMuonRejectionSimpleElectronCleaned = process.hpsPFTauDiscriminationByMuonRejectionSimple.clone(PFTauProducer = cms.InputTag("hpsPFTauProducerElectronCleaned"))
    #process.hpsPFTauDiscriminationByTightMuonRejectionSimpleElectronCleaned = hpsPFTauDiscriminationByTightMuonRejectionSimple.clone(PFTauProducer = cms.InputTag("hpsPFTauProducerElectronCleaned"))
    process.miniAODTausTaskElectronCleaned.add(process.hpsPFTauDiscriminationByMuonRejectionSimpleElectronCleaned)
    #process.miniAODTausTaskElectronCleaned.add(process.hpsPFTauDiscriminationByTightMuonRejectionSimpleElectronCleaned)
    
    process.hpsPFTauDiscriminationByMuonRejectionSimpleMuonCleaned = process.hpsPFTauDiscriminationByMuonRejectionSimple.clone(PFTauProducer = cms.InputTag("hpsPFTauProducerMuonCleaned"))
    #process.hpsPFTauDiscriminationByTightMuonRejectionSimpleMuonCleaned = hpsPFTauDiscriminationByTightMuonRejectionSimple.clone(PFTauProducer = cms.InputTag("hpsPFTauProducerMuonCleaned"))
    process.miniAODTausTaskMuonCleaned.add(process.hpsPFTauDiscriminationByMuonRejectionSimpleMuonCleaned)
    #process.miniAODTausTaskMuonCleaned.add(process.hpsPFTauDiscriminationByTightMuonRejectionSimpleMuonCleaned)

    #####
    # PAT part in the following

    
    if runType=='signal' or runType=='background':
        print(runType,': Identified')
    
        process.tauGenJets.GenParticles = cms.InputTag("prunedGenParticles")
        process.tauMatch.matched = cms.InputTag("prunedGenParticles")

        process.tauGenJetsElectronCleaned.GenParticles = cms.InputTag("prunedGenParticles")
        process.tauMatchElectronCleaned.matched = cms.InputTag("prunedGenParticles")
   
        process.tauGenJetsMuonCleaned.GenParticles = cms.InputTag("prunedGenParticles")
        process.tauMatchMuonCleaned.matched = cms.InputTag("prunedGenParticles")
    
    else:
        print (runType, ': Identified, No MC Matching')
        from PhysicsTools.PatAlgos.tools.coreTools import runOnData
        runOnData(process, names = ['Taus'], outputModules = [])
        runOnData(process, names = ['Taus'],outputModules = [],postfix='MuonCleaned')
        runOnData(process, names = ['Taus'],outputModules = [],postfix='ElectronCleaned')
        
    # Remove unsupported tauIDs
    for name, src in six.iteritems(process.patTaus.tauIDSources.parameters_()):
        if name.find('againstElectron') > -1 or name.find('againstMuon') > -1:
            if name.find('againstElectronDeadECAL') > -1: continue
            delattr(process.patTaus.tauIDSources,name)
    # Add MiniAOD specific ones
        setattr(process.patTaus.tauIDSources,'againstMuonLooseSimple',
            cms.PSet(inputTag = cms.InputTag('hpsPFTauDiscriminationByMuonRejectionSimple'),
                     provenanceConfigLabel = cms.string('IDWPdefinitions'),
                     idLabel = cms.string('ByLooseMuonRejectionSimple')
                 ))
    
    setattr(process.patTaus.tauIDSources,'againstMuonTightSimple',
            cms.PSet(inputTag = cms.InputTag('hpsPFTauDiscriminationByMuonRejectionSimple'),
                     provenanceConfigLabel = cms.string('IDWPdefinitions'),
                     idLabel = cms.string('ByTightMuonRejectionSimple')
                 ))
    
    for name, src in six.iteritems(process.patTausElectronCleaned.tauIDSources.parameters_()):
        if name.find('againstElectron') > -1 or name.find('againstMuon') > -1:
            if name.find('againstElectronDeadECAL') > -1 : continue #and name.find('ElectronCleaned') > -1: continue
            delattr(process.patTausElectronCleaned.tauIDSources,name)
    # Add MiniAOD specific ones
    setattr(process.patTausElectronCleaned.tauIDSources,'againstMuonLooseSimple',
            cms.PSet(inputTag = cms.InputTag('hpsPFTauDiscriminationByMuonRejectionSimpleElectronCleaned'),
                     provenanceConfigLabel = cms.string('IDWPdefinitions'),
                     idLabel = cms.string('ByLooseMuonRejectionSimple')
                 ))
    
    setattr(process.patTausElectronCleaned.tauIDSources,'againstMuonTightSimple',
            cms.PSet(inputTag = cms.InputTag('hpsPFTauDiscriminationByMuonRejectionSimpleElectronCleaned'),
                     provenanceConfigLabel = cms.string('IDWPdefinitions'),
                     idLabel = cms.string('ByTightMuonRejectionSimple')
                 ))
    
    
    for name, src in six.iteritems(process.patTausMuonCleaned.tauIDSources.parameters_()):
        if name.find('againstElectron') > -1 or name.find('againstMuon') > -1:
            if name.find('againstElectronDeadECAL') > -1 : continue #and name.find('MuonCleaned'): continue
            delattr(process.patTausMuonCleaned.tauIDSources,name)
    setattr(process.patTausMuonCleaned.tauIDSources,'againstMuonLooseSimple',
            cms.PSet(inputTag = cms.InputTag('hpsPFTauDiscriminationByMuonRejectionSimpleMuonCleaned'),
                     provenanceConfigLabel = cms.string('IDWPdefinitions'),
                     idLabel = cms.string('ByLooseMuonRejectionSimple')
                 ))
    
    setattr(process.patTausMuonCleaned.tauIDSources,'againstMuonTightSimple',
            cms.PSet(inputTag = cms.InputTag('hpsPFTauDiscriminationByMuonRejectionSimpleMuonCleaned'),
                     provenanceConfigLabel = cms.string('IDWPdefinitions'),
                     idLabel = cms.string('ByTightMuonRejectionSimple')
                 ))
    print('New ID')
    # Run TauIDs (anti-e && deepTau) on top of selectedPatTaus
    _updatedTauName = 'selectedPatTausNewIDs'
    _noUpdatedTauName = 'selectedPatTausNoNewIDs'
    import RecoTauTag.RecoTau.tools.runTauIdMVA as tauIdConfig
    tauIdEmbedder = tauIdConfig.TauIDEmbedder(
        process, debug = False,
        updatedTauName = _updatedTauName,
        toKeep = ['againstEle2018','deepTau2017v2p1','2017v2']
    )
    tauIdEmbedder.runTauID()
    setattr(process, _noUpdatedTauName, process.selectedPatTaus.clone(cut = cms.string('pt > 8.0 && abs(eta)<2.3 && tauID(\'decayModeFinding\')> 0.5')))
    process.miniAODTausTask.add(getattr(process,_noUpdatedTauName))
    delattr(process, 'selectedPatTaus')
    process.deepTau2017v2p1.taus = _noUpdatedTauName
    process.patTauDiscriminationByElectronRejectionMVA62018Raw.PATTauProducer = _noUpdatedTauName
    process.patTauDiscriminationByElectronRejectionMVA62018.PATTauProducer = _noUpdatedTauName
    process.rerunDiscriminationByIsolationOldDMMVArun2017v2raw.PATTauProducer = _noUpdatedTauName
    process.rerunDiscriminationByIsolationOldDMMVArun2017v2.PATTauProducer = _noUpdatedTauName
    process.selectedPatTaus = getattr(process, _updatedTauName).clone(
        src = _noUpdatedTauName
    )
    process.newTauIDsTask = cms.Task(
        process.rerunMvaIsolationTask,
        process.selectedPatTaus
    )
    process.miniAODTausTask.add(process.newTauIDsTask)
    print('New ID Done')
    print('New ID ElectronCleaned')
    # Run TauIDs (anti-e && deepTau) on top of selectedPatTaus-ElectronCleaned
    _updatedTauNameElectronCleaned = 'selectedPatTausNewIDsElectronCleaned'
    _noUpdatedTauNameElectronCleaned = 'selectedPatTausNoNewIDsElectronCleaned'
    
    import MiniAODSkimmer.MiniAODCleaner.tools.runTauIdMVA_ElectronCleaned as tauIdConfigElectronCleaned
    tauIdEmbedderElectronCleaned = tauIdConfigElectronCleaned.TauIDEmbedder(
        process, debug = False,
        updatedTauName = _updatedTauNameElectronCleaned,
        postfix="ElectronCleaned",
        toKeep = ['againstEle2018','deepTau2017v2p1','2017v2']
    )
    tauIdEmbedderElectronCleaned.runTauID()
    setattr(process, _noUpdatedTauNameElectronCleaned, process.selectedPatTausElectronCleaned.clone(cut = cms.string('pt > 8.0 && abs(eta)<2.3 && tauID(\'decayModeFinding\')> 0.5')))
    process.miniAODTausTaskElectronCleaned.add(getattr(process,_noUpdatedTauNameElectronCleaned))
    delattr(process,'selectedPatTausElectronCleaned')
    process.deepTau2017v2p1ElectronCleaned.taus = _noUpdatedTauNameElectronCleaned
    process.patTauDiscriminationByElectronRejectionMVA62018RawElectronCleaned.PATTauProducer = _noUpdatedTauNameElectronCleaned
    process.patTauDiscriminationByElectronRejectionMVA62018ElectronCleaned.PATTauProducer = _noUpdatedTauNameElectronCleaned
    process.rerunDiscriminationByIsolationOldDMMVArun2017v2rawElectronCleaned.PATTauProducer = _noUpdatedTauNameElectronCleaned
    process.rerunDiscriminationByIsolationOldDMMVArun2017v2ElectronCleaned.PATTauProducer = _noUpdatedTauNameElectronCleaned
    process.selectedPatTausElectronCleaned = getattr(process, _updatedTauNameElectronCleaned).clone(
        src = _noUpdatedTauNameElectronCleaned
    )
    process.newTauIDsTaskElectronCleaned = cms.Task(
        process.rerunMvaIsolationTaskElectronCleaned,
        process.selectedPatTausElectronCleaned
    )
    process.miniAODTausTaskElectronCleaned.add(process.newTauIDsTaskElectronCleaned)
    print('New ID ElectronCleaned - Done ')
    print('New ID MuonCleaned')
    # Run TauIDs (anti-e && deepTau) on top of selectedPatTaus-MuonCleaned
    _updatedTauNameMuonCleaned = 'selectedPatTausNewIDsMuonCleaned'
    _noUpdatedTauNameMuonCleaned = 'selectedPatTausNoNewIDsMuonCleaned'
    
    import MiniAODSkimmer.MiniAODCleaner.tools.runTauIdMVA_MuonCleaned as tauIdConfigMuonCleaned
    tauIdEmbedderMuonCleaned = tauIdConfigMuonCleaned.TauIDEmbedder(
        process, debug = False,
        updatedTauName = _updatedTauNameMuonCleaned,
        postfix="MuonCleaned",
        toKeep = ['againstEle2018','deepTau2017v2p1','2017v2']
    )
    tauIdEmbedderMuonCleaned.runTauID()
    setattr(process, _noUpdatedTauNameMuonCleaned, process.selectedPatTausMuonCleaned.clone(cut = cms.string('pt > 8.0 && abs(eta)<2.3 && tauID(\'decayModeFinding\')> 0.5')))
    process.miniAODTausTaskMuonCleaned.add(getattr(process,_noUpdatedTauNameMuonCleaned))
    delattr(process,'selectedPatTausMuonCleaned')
    process.deepTau2017v2p1MuonCleaned.taus = _noUpdatedTauNameMuonCleaned
    process.patTauDiscriminationByElectronRejectionMVA62018RawMuonCleaned.PATTauProducer = _noUpdatedTauNameMuonCleaned
    process.patTauDiscriminationByElectronRejectionMVA62018MuonCleaned.PATTauProducer = _noUpdatedTauNameMuonCleaned
    process.rerunDiscriminationByIsolationOldDMMVArun2017v2rawMuonCleaned.PATTauProducer = _noUpdatedTauNameMuonCleaned
    process.rerunDiscriminationByIsolationOldDMMVArun2017v2MuonCleaned.PATTauProducer = _noUpdatedTauNameMuonCleaned
    process.selectedPatTausMuonCleaned = getattr(process, _updatedTauNameMuonCleaned).clone(
        src = _noUpdatedTauNameMuonCleaned
    )
    process.newTauIDsTaskMuonCleaned = cms.Task(
        process.rerunMvaIsolationTaskMuonCleaned,
        process.selectedPatTausMuonCleaned
    )
    process.miniAODTausTaskMuonCleaned.add(process.newTauIDsTaskMuonCleaned)
    print('New ID MuonCleaned - Done ')

    # print('Slimming the various Tau Collections')
   
    
def addFurtherSkimming(process):
    #doMM =kwargs.pop('doMM',False)
    #doMT = kwargs.pop('doMT',False)
    


    print('Slimming the various Tau Collections')
    process.slimpath = cms.Path()
    from PhysicsTools.PatAlgos.slimming.slimmedTaus_cfi import slimmedTaus
    process.slimmedTausUnCleaned = slimmedTaus.clone(src = cms.InputTag('selectedPatTaus'))
    process.slimmedTausElectronCleaned = slimmedTaus.clone(src = cms.InputTag('selectedPatTausElectronCleaned'), packedPFCandidates = cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned'))
    process.slimmedTausMuonCleaned = slimmedTaus.clone(src = cms.InputTag('selectedPatTausMuonCleaned'), packedPFCandidates = cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned'))
    process.slimpath *=process.slimmedTausUnCleaned
    process.slimpath  *=process.slimmedTausElectronCleaned
    process.slimpath  *=process.slimmedTausMuonCleaned
    process.schedule.append(process.slimpath)
    print('Slimming Done')
    #########################
    ### Skim Path MiniAOD ###
    #########################
    process.main_path = cms.Path()
    process.main_path_et = cms.Path()
    process.main_path_mt = cms.Path()
    

    ###### Will only use main-skim so these won't be associated to schedule ######
    process.z_path = cms.Path()
    process.z_tau_eff_path = cms.Path()

    
    ###############
    ### Trigger ###
    ###############
    process.HLT =cms.EDFilter("HLTHighLevel",
                              TriggerResultsTag = cms.InputTag("TriggerResults","","HLT"),
                              HLTPaths = cms.vstring("HLT_IsoMu24_v*", "HLT_IsoTkMu24_v*", "HLT_IsoMu27_v*", "HLT_IsoTkMu27_v*"), #2017
                              #HLTPaths = cms.vstring("HLT_IsoMu24_v*"), #2018  
                              eventSetupPathsKey = cms.string(''),
                              andOr = cms.bool(True), #----- True = OR, False = AND between the HLTPaths
                              throw = cms.bool(False) # throw exception on unknown path names
                    )
    process.main_path *= process.HLT
    process.main_path_et *= process.HLT
    process.main_path_mt *= process.HLT
    
    ###############
    ### Muon ID ###
    ###############
    process.analysisMuonsNoIso = cms.EDFilter('PATMuonSelector',
                                              src = cms.InputTag('slimmedMuons'),
                                              cut = cms.string('pt > 3.0 && abs(eta)<2.4 && isPFMuon && (isGlobalMuon || isTrackerMuon)'),
                )
    process.analysisMuonsIso = cms.EDFilter('PATMuonSelector',
                                            src = cms.InputTag('analysisMuonsNoIso'),
                                            cut = cms.string('(pfIsolationR04().sumChargedHadronPt'
                                                             '+ max(0., pfIsolationR04().sumNeutralHadronEt'
                                                             '+ pfIsolationR04().sumPhotonEt'
                                                             '- 0.5*pfIsolationR04().sumPUPt))'
                                                             '/pt()<0.25'),
                                        )
    process.analysisMuonsNoIsoCount = cms.EDFilter("PATCandViewCountFilter",
        minNumber = cms.uint32(1),
        maxNumber = cms.uint32(999),
        src = cms.InputTag('analysisMuonsNoIso'),
    )
    
    process.analysisMuonsIsoCount = cms.EDFilter("PATCandViewCountFilter",
        minNumber = cms.uint32(1),
        maxNumber = cms.uint32(999),
        src = cms.InputTag('analysisMuonsIso'),
    )
        
    process.main_path *= process.analysisMuonsNoIso
    process.main_path *= process.analysisMuonsNoIsoCount
    process.main_path_et *= process.analysisMuonsNoIso
    process.main_path_et *= process.analysisMuonsNoIsoCount
    process.main_path_mt *= process.analysisMuonsNoIso
    process.main_path_mt *= process.analysisMuonsNoIsoCount
    
    #########################
    ### Trigger Threshold ###
    #########################
    process.triggerMuon = cms.EDFilter('PATMuonSelector',
                                       src = cms.InputTag('analysisMuonsNoIso'),
                                       cut = cms.string('pt > 24.0'),
                                   )
    process.triggerMuonCount = cms.EDFilter("PATCandViewCountFilter",
                                            minNumber = cms.uint32(1),
                                            maxNumber = cms.uint32(999),
                                            src = cms.InputTag('triggerMuon'),
                                        )
    process.main_path *= process.triggerMuon
    process.main_path *= process.triggerMuonCount
    process.main_path_et *= process.triggerMuon
    process.main_path_et *= process.triggerMuonCount
    process.main_path_mt *= process.triggerMuon
    process.main_path_mt *= process.triggerMuonCount
    
    ############################
    ### Require two OS muons ### -> Dropped as we don't want to separate out skims
    ############################
    
    process.mumuZ = cms.EDProducer("CandViewShallowCloneCombiner",
                                   decay = cms.string("{0}@+ {0}@-".format('slimmedMuons')),
                                   cut   = cms.string("60<mass<120"),
                               )
    process.mumuZCount = cms.EDFilter("PATCandViewCountFilter",
                                      minNumber = cms.uint32(1),
                                      maxNumber = cms.uint32(999),
                                      src = cms.InputTag('mumuZ'),
                                  )
    process.z_path *= process.mumuZ
    process.z_path *= process.mumuZCount
    
    ########################
    ### Tau requirements ###
    ########################
    
    process.analysisTaus = cms.EDFilter('PATTauSelector',
                                        src = cms.InputTag('slimmedTausUnCleaned'),
                                        cut = cms.string('pt > 8.0 && abs(eta)<2.3 && tauID(\'decayModeFinding\')> 0.5'),
                                     )
    process.analysisTausCount = cms.EDFilter("PATCandViewCountFilter",
                                             minNumber = cms.uint32(1),
                                             maxNumber = cms.uint32(999),
                                             src = cms.InputTag('analysisTaus'),
                                          )
    process.analysisTausMuonCleaned = cms.EDFilter('PATTauSelector',
                                                   src = cms.InputTag('slimmedTausMuonCleaned'),
                                                   cut = cms.string('pt > 8.0 && abs(eta)<2.3 && tauID(\'decayModeFinding\')> 0.5'),
                                               )
    process.analysisTausMuonCleanedCount = cms.EDFilter("PATCandViewCountFilter",
                                                        minNumber = cms.uint32(1),
                                                        maxNumber = cms.uint32(999),
                                                        src = cms.InputTag('analysisTausMuonCleaned'),
                                                     )
    process.analysisMuonsNoIsoMTCount = cms.EDFilter("PATCandViewCountFilter",
                                                     minNumber = cms.uint32(3),
                                                     maxNumber = cms.uint32(999),
                                                     src = cms.InputTag('analysisMuonsNoIso'),
                                                 )
    process.analysisTausElectronCleaned = cms.EDFilter('PATTauSelector',
                                                       src = cms.InputTag('slimmedTausElectronCleaned'),
                                                       cut = cms.string('pt > 8.0 && abs(eta)<2.3 && tauID(\'decayModeFinding\')> 0.5'),
                                                       )
    process.analysisTausElectronCleanedCount = cms.EDFilter("PATCandViewCountFilter",
                                                            minNumber = cms.uint32(1),
                                                            maxNumber = cms.uint32(999),
                                                            src = cms.InputTag('analysisTausElectronCleaned'),
                                                        )
    
    process.main_path_mt *= process.analysisMuonsNoIsoMTCount
    process.main_path_mt *= process.analysisTausMuonCleaned
    process.main_path_mt *= process.analysisTausMuonCleanedCount
    process.main_path_et *= process.analysisTausElectronCleaned
    process.main_path_et *= process.analysisTausElectronCleanedCount
    process.z_tau_eff_path *= process.analysisTaus
    process.z_tau_eff_path *= process.analysisTausCount 
    ############################
    ### Tau Eff requirements ###
    ############################
    
    process.mumuZTauEff = cms.EDProducer("CandViewShallowCloneCombiner",
                                         decay = cms.string("{0} {1}".format('slimmedMuons','analysisTaus')),
                                         checkCharge = cms.bool(False),
                                         cut   = cms.string("30<mass<210 && deltaR(daughter(0).eta,daughter(0).phi,daughter(1).eta,daughter(1).phi)>0.5"),
                                     )
    process.mumuZCountTauEff = cms.EDFilter("PATCandViewCountFilter",
                                            minNumber = cms.uint32(1),
                                            maxNumber = cms.uint32(999),
                                            src = cms.InputTag('mumuZTauEff'),
                                        )
    process.z_tau_eff_path *= process.mumuZTauEff
    process.z_tau_eff_path *= process.mumuZCountTauEff
     
    #################
    ### Finish up ###
    #################
    
    process.schedule.append(process.main_path)
    process.schedule.append(process.main_path_et)
    process.schedule.append(process.main_path_mt)
    #process.schedule.append(process.z_path)
    #process.schedule.append(process.z_tau_eff_path)
    
    ###################
    ### Lumi Summary ##
    ###################
    # lumi summary
    
    process.lumiSummary = cms.EDProducer("LumiSummaryProducer",
                                         genEventInfo = cms.InputTag("generator"),
                                         lheEventProduct = cms.InputTag("externalLHEProducer"),
                                    )
    process.lumiSummary_step = cms.Path(process.lumiSummary)
    process.schedule.append(process.lumiSummary_step)
    
    
def setOutputModule(mode=0):
    #mode = 0: store original MiniAOD and new selectedPatTaus 
    #mode = 1: store original MiniAOD, new selectedPatTaus, and all PFTau products as in AOD (except of unsuported ones), plus a few additional collections (charged hadrons, pi zeros, combinatoric reco taus)
    
    import Configuration.EventContent.EventContent_cff as evtContent
    output = cms.OutputModule(
        'PoolOutputModule',
        compressionAlgorithm = cms.untracked.string('LZMA'),
        compressionLevel = cms.untracked.int32(4),
        dropMetaData = cms.untracked.string('ALL'),
        eventAutoFlushCompressedSize = cms.untracked.int32(-10000),
        fileName=cms.untracked.string('miniAOD_TauReco.root'),
        fastCloning=cms.untracked.bool(False),
        dataset=cms.untracked.PSet(
            dataTier=cms.untracked.string('MINIAODSIM'),
            filterName=cms.untracked.string('')
        ),
        outputCommands = evtContent.MINIAODSIMEventContent.outputCommands,
        SelectEvents=cms.untracked.PSet(
            SelectEvents=cms.vstring('main_path_et','main_path_mt','main_path')
        )
    )
    #output.outputCommands.append('keep *_selectedPatTaus_*_*')
    if mode==1:
        for prod in evtContent.RecoTauTagAOD.outputCommands:
            if prod.find('ElectronRejection') > -1:
                continue
            if prod.find('MuonRejection') > -1:
                    continue
                    output.outputCommands.append(prod)
        output.outputCommands.append('keep *_hpsPFTauDiscriminationByLooseMuonRejectionSimple_*_*')
        output.outputCommands.append('keep *_hpsPFTauDiscriminationByTightMuonRejectionSimple_*_*')
        output.outputCommands.append('keep *_combinatoricReco*_*_*')
        output.outputCommands.append('keep *_ak4PFJetsRecoTauChargedHadrons_*_*')
        output.outputCommands.append('keep *_ak4PFJetsLegacyHPSPiZeros_*_*')
        output.outputCommands.append('keep *_patJetsPAT_*_*')

    return output

#####
