from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'MiniAOD_SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-125_M-10_MainSkim_Summer20UL17-106X_mc2017_v2'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True


config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '../rerunTauRecoOnMiniAOD_WithClean_Custom.py'
config.JobType.numCores = 4
config.JobType.maxMemoryMB = 10000

config.JobType.allowUndistributedCMSSW = True
config.Data.inputDataset ='/SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-125_M-10_TuneCP5_13TeV_madgraph_pythia8/RunIISummer20UL17MiniAOD-106X_mc2017_realistic_v6-v3/MINIAODSIM'
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 2
config.Data.outLFNDirBase = '/store/user/rhabibul/'
config.Data.publication = True
config.Data.outputDatasetTag = 'MiniAOD_SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-125_M-10_MainSkim_Summer20UL17-106X_mc2017_v2'
config.Site.storageSite = 'T2_US_Florida'
config.Site.blacklist = ['T3_KR_KNU', 'T3_FR_IPNL', 'T2_TR_METU', 'T2_TW_NCHC', 'T2_BE_IIHE', 'T3_US_Baylor']
