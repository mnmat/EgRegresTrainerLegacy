#!/usr/bin/env python

import argparse
import subprocess
import os

# INPUTDIR = "s4Flat"
# INPUTFILE= "HLTAnalyzerTree_IDEAL_Flat_test.root"
# GBRDIR = "s4Reg_HLT"
# GBREEFILE = "Run3HLT_IdealIC_IdealTraining_stdVar_stdCuts_EE_ntrees1500_results.root"
# GBREBFILE = GBREEFILE.replace("_EE_","_EB_")

if __name__ =='__main__':

    arch = os.getenv('SCRAM_ARCH')
    parser = argparse.ArgumentParser(description='makes a list of files to run over')
    # parser.add_argument('--baseDir')
    # parser.add_argument('--trainOnSample')
    # parser.add_argument('--testOnSample')

    parser.add_argument('--input_file',help='input filename')
    parser.add_argument('--output_file',help='output filename')
    parser.add_argument('--gbrEE', help='')
    parser.add_argument('--gbrEB', help='')
    parser.add_argument('--ebName', default = "egRegDataEcalHLTV1", help='')
    parser.add_argument('--eeName', default = "egRegDataHGCALHLTV1", help='')
    args = parser.parse_args()
    #base_cmd = "bin/"+arch+"/RegressionApplier_newExe",args.input_file,args.output_file,"--gbrForestFileEE",args.gbrForestFileEE,"--gbrForestFileEB",args.gbrForestFileEB,"--nrThreads","4","--ebName",args.ebName,"--eeName",args.eeName,"--writeFullTree",args.writeFullTree,"--regOutTag",args.regOutTag

    print(os.getcwd())

    base_cmd = [
        f"./bin/el9_amd64_gcc11/RegressionApplier_newExe", 
        args.input_file, 
        args.output_file,
        "--gbrForestFileEE", args.gbrEE,
        "--gbrForestFileEB", args.gbrEB,
        "--nrThreads", "4",
        "--ebName", args.ebName,
        "--eeName", args.eeName,
        "--writeFullTree", "1",  # Corrected to "True" as string for the command line
        "--regOutTag", "Ideal"
    ]
    print(f"Running command: {' '.join(base_cmd)}")
    
    # Make outdir
    print(args.output_file)
    outdir = "/".join(args.output_file.split("/")[:-1])
    if not os.path.exists(outdir):
        print("Created", outdir)
        os.makedirs(outdir)

    os.chdir("EgRegresTrainerLegacy")
    env = os.environ.copy()
    env["PATH"] = env.get("PATH", "") + f":./bin/{arch}"
    env["ROOT_INCLUDE_PATH"] = env.get("ROOT_INCLUDE_PATH", "") + ":./include"
    

    #cmd1 = "cd EgRegresTrainerLegacy"
    #cmd2 = "export PATH=$PATH:./bin/$SCRAM_ARCH"
    #cmd3 = "export ROOT_INCLUDE_PATH=$ROOT_INCLUDE_PATH:$PWD/include"
    #os.system("%s;%s;%s"%(cmd1, cmd2, cmd3))
    subprocess.Popen(base_cmd,env=env).communicate()