#Just an example
from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'MiniAOD_DYJetsToLL_MainSkim_Summer20UL17-106X_mc2017_v3'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True


config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '../rerunTauRecoOnMiniAOD_WithClean_Custom.py'
config.JobType.numCores = 4
config.JobType.maxMemoryMB = 10000

config.JobType.allowUndistributedCMSSW = True
config.Data.inputDataset ='/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v2/MINIAODSIM'
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 2
config.Data.outLFNDirBase = '/store/user/rhabibul/'
config.Data.publication = True
config.Data.outputDatasetTag = 'MiniAOD_DYJetsToLL_MainSkim_Summer20UL17-106X_mc2017_v3'
#config.Data.ignoreLocality = True
#config.Site.whitelist = ["T*_FR_*", "T*_DE_*", "T*_CH_*"]
config.Site.storageSite = 'T2_US_Florida'
#config.Site.blacklist = ['T3_KR_KNU', 'T3_FR_IPNL', 'T2_TR_METU', 'T2_TW_NCHC', 'T2_BE_IIHE', 'T3_US_Baylor']
config.Site.blacklist = ['T3_KR_KNU', 'T3_FR_IPNL', 'T2_TR_METU', 'T2_TW_NCHC', 'T2_BE_IIHE', 'T3_US_Baylor']
