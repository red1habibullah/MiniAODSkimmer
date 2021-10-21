# MiniAODSkimmerThis package re-runs tau reconstruction on miniAOD samples using miniAOD inputs.We do the Electron/Muon Cleaning in this step and store results for the tau  collections cleaned.A single skim is performed and LumiSummary information is stored within the output .root file rather than creating an additional file.# Setting up the environment:```bash$ setenv SCRAM_ARCH slc7_amd64_gcc900 $ cmsrel CMSSW_12_0_0_pre4$ cd CMSSW_12_0_0_pre4/src$ git cms-init$ cmsenv$ git clone --recursive git@github.com:red1habibullah/MiniAODSkimmer.git -b UL_12X_2017$ git cms-addpkg PhysicsTools/PatAlgos$ rm PhysicsTools/PatAlgos/plugins/PATTauSlimmer.cc $ cp /uscms_data/d3/rhabibul/MiniAODCleaner/CMSSW_10_6_20/src/PhysicsTools/PatAlgos/plugins/PATTauSlimmer.cc PhysicsTools/PatAlgos/plugins/PATTauSlimmer.cc$ scram b -j8```# Running the code:```bash$ cd CMSSW_12_0_0_pre4/src$ scram b clean$ scram b -j8$ cd MiniAODCleaner/test/$ cmsRun rerunTauRecoOnMiniAOD_WithClean_Custom.py```# CRAB submission:```bash$ cd test/crabConfig/```## Background Sample Submission:In the config file, uncomment the relevant string variable and comment out others:```bashrunType = 'background'```Next submit the CRAB job using a CRAB config file:```bashcrab-dev submit -c crabConfig_DYJetstoLL.py```The Input dataset should be changed according to the given samples.## Signal MC sample Submission:In the config file, uncomment the relevant string variable and comment out others:```bashrunType = 'signal'```Next submit the CRAB job using a CRAB config file (as an example):```bashcrab-dev submit -c crabConfig_H125AA10.py```**NOTE**: The command is different form the usual 'crab' command as CRAB is still under-development in CMSSW_12and some packages are python 3 compatible but not python 2. So using 'crab' rather than 'crab-dev' causes failed jobs.https://hypernews.cern.ch/HyperNews/CMS/get/cernCompAnnounce/1488.html