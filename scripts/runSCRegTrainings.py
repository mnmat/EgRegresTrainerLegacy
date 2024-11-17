#!/usr/bin/env python

import subprocess
import os
import sys

# added python directory to path so that it will find regtools
sys.path.insert(1, 'python')
from regtools import RegArgs

import time
import argparse
def main():

    parser = argparse.ArgumentParser(description='runs the SC regression trainings')
    parser.add_argument('--era',required=True,help='year to produce for, 2016, 2017, 2018 are the options')
    parser.add_argument('--input_dir','-i',default='/eos/user/r/rasharma/post_doc_ihep/EGamma/HLT/regression/MainNtuples_v2/',help='input directory with the ntuples')
    # parser.add_argument('--input_dir','-i',default='/afs/cern.ch/user/r/rasharma/work/EGamma-POG/HLT_tasks/CPUtoGPUTransition/analyzer/CMSSW_12_0_1/src',help='input directory with the ntuples')
    parser.add_argument('--output_dir','-o',default="/eos/user/r/rasharma/post_doc_ihep/EGamma/HLT/regression/MainNtuples_v2/results/resultsSC_MainNtuples_FullSelection_FlatNtuple",help='output dir')
    args = parser.parse_args()

    #step 1, run calo only regression on the ideal IC to get the mean
    #step 2, apply the mean to the real IC sample and save the result in a tree
    #step 3, retrain the resolution for the real IC on the corrected energy
    run_step1 = True
    run_step2 = False
    run_step3 = False

    #setup the selection (event number cuts come later)
    cuts_name = "stdCuts"
    #base_ele_cuts = "(eg_gen_energy>0 && eg_sigmaIEtaIEta>0 && eg_sigmaIPhiIPhi>0 && {extra_cuts})" # Full selection for Run-3
    base_ele_cuts = "" # Full selection for Run-3


    # base_ele_cuts = "(eg_gen_energy>0 && eg_sigmaIEtaIEta>0 && {extra_cuts})"
    # base_ele_cuts = "(1)"

    #prefixes all the regressions produced
    if args.era=='2021Run3':
        base_reg_name = "2021Run3"
        input_ideal_ic  = "{}/DoubleElectron_FlatPt-1To500_FlatPU0to70IDEALGT_120X_mcRun3_2021_realistic_v6_ECALIdealIC-v2_AODSIM.root".format(args.input_dir)
        input_real_ic  = "{}/DoubleElectron_FlatPt-1To500_FlatPU0to70_120X_mcRun3_2021_realistic_v6-v1_AODSIM.root".format(args.input_dir)
        ideal_eventnr_cut = "evt.eventnr%5==0"
        real_eventnr_cut = "evt.eventnr%5==1"
    elif args.era=='Run3':
        base_reg_name = "Run3HLT"
        # input_ideal_ic  = "{}/HLTAnalyzerTree_IDEAL.root".format(args.input_dir)
        # input_real_ic = "{}/HLTAnalyzerTree_REAL.root".format(args.input_dir)
        # input_ideal_ic  = "{}/HLTAnalyzerTree_IDEAL_Flat.root".format(args.input_dir)
        # input_real_ic = "{}/HLTAnalyzerTree_REAL_Flat.root".format(args.input_dir)
        input_ideal_ic_train = "{}/HLTAnalyzerTree_IDEAL_Flat_train.root".format(args.input_dir)
        input_ideal_ic_test = "{}/HLTAnalyzerTree_IDEAL_Flat_test.root".format(args.input_dir)

        input_real_ic_train = "{}/HLTAnalyzerTree_IDEAL_Flat_train.root".format(args.input_dir)
        input_real_ic_test = "{}/HLTAnalyzerTree_IDEAL_Flat_test.root".format(args.input_dir)


        # input_ideal_ic  = "{}/HLTAnalyzerTree_IDEAL_Flat_Small.root".format(args.input_dir)
        # input_real_ic = "{}/HLTAnalyzerTree_REAL_Flat_Small.root".format(args.input_dir)

        # input_ideal_ic  = "{}/ideal.root".format(args.input_dir)
        # input_real_ic = "{}/real.root".format(args.input_dir)

        # ideal_eventnr_cut = "(1)"  #4million electrons (we determined 4 million was optimal but after the 2017 was done)
        # real_eventnr_cut = "(1)" #4million electrons (we determined 4 million was optimal but after the 2017 was done)

        ideal_eventnr_cut = "(eventnr%1==0)"  #4million electrons (we determined 4 million was optimal but after the 2017 was done)
        real_eventnr_cut = "(eventnr%1==1)" #4million electrons (we determined 4 million was optimal but after the 2017 was done)
    else:
        raise ValueError("era {} is invalid, the only available option is 2021Run3/Run3".format(era))


    regArgs = RegArgs()
    #regArgs.input_training =  str(input_ideal_ic)
    #regArgs.input_testing = str(input_ideal_ic)

    regArgs.input_training =  str(input_ideal_ic_train)
    regArgs.input_testing = str(input_ideal_ic_test)

    #regArgs.set_sc_default()
    #regArgs.tree_name = "egHLTRun3Tree"
    regArgs.set_sc_default_new()
    #regArgs.set_sc_extended_new()
    regArgs.tree_name = "egRegDataHGCALV1"
    regArgs.cfg_dir = "configs"
    regArgs.out_dir = args.output_dir
    regArgs.cuts_name = cuts_name
    regArgs.base_name = "{}_IdealIC_IdealTraining".format(base_reg_name)
    regArgs.cuts_base = base_ele_cuts.format(extra_cuts = ideal_eventnr_cut)
    regArgs.ntrees = 1500
    print("regArgs.cuts_base: {}".format(regArgs.cuts_base))

    print ("""about to run the supercluster regression with:
    name: {name}
    ideal ic input: {ideal_ic}
    real ic input: {real_ic}
    output dir: {out_dir}
steps to be run:
    step 1: ideal training for mean       = {step1}
    step 2: apply ideal training to real  = {step2}
    step 3: real training for sigma       = {step3}""".format(name=base_reg_name,ideal_ic=input_ideal_ic_train,real_ic=input_real_ic_train,out_dir=args.output_dir,step1=run_step1,step2=run_step2,step3=run_step3))
    time.sleep(20)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    print("===> Running step - 1")
    if run_step1: regArgs.run_eb_and_ee_new()

    regArgs.do_eb = True
    forest_eb_file = regArgs.output_name()
    regArgs.do_eb = False
    forest_ee_file = regArgs.output_name()

    regArgs.base_name = "{}_RealIC_IdealTraining".format(base_reg_name)
    input_for_res_training = str(regArgs.applied_name()) #save the output name before we change it
    #input_for_input_for_res_training = str(input_real_ic)
    input_for_input_for_res_training = str(input_real_ic_train)

    # Set scram arch
    arch = os.getenv('SCRAM_ARCH')

    print("===> Running step - 2")
    if run_step2: subprocess.Popen(["bin/"+arch+"/RegressionApplierExe",input_for_input_for_res_training,input_for_res_training,"--gbrForestFileEE",forest_ee_file,"--gbrForestFileEB",forest_eb_file,"--nrThreads","4","--treeName",regArgs.tree_name,"--writeFullTree","1","--regOutTag","Ideal"]).communicate()

    regArgs.base_name = "{}_RealIC_RealTraining".format(base_reg_name)
    regArgs.input_training = input_for_res_training
    regArgs.input_testing = input_for_res_training
    regArgs.target = "eg_gen_energy/(eg_rawEnergy*regIdealMean)"
    regArgs.fix_mean = True
    regArgs.cuts_base = base_ele_cuts.format(extra_cuts = real_eventnr_cut)

    print("===> Running step - 3")
    if run_step3: regArgs.run_eb_and_ee()

if __name__ =='__main__':
    main()


