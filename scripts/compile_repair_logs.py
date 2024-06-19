

import argparse 
import sys 
import os 
import re 

parser = argparse.ArgumentParser(description='compile repair logs into table')

parser.add_argument('-i', '--input_list', dest='inputSample',
type=str,
help='input list of samples')

parser.add_argument('-o', '--output_table', dest='outtab',
type=str,
help='output table with all samples')

args = parser.parse_args()

# variables
fields=["Input:","Result:","Pairs","Singletons","Time:","Reads Processed:","Bases Processed:"]
fieldList = ['input_reads', 'input_bases', 'output_reads', 'output_reads_pct', 'output_bases', 'output_bases_pct', 'paired_reads', 'paired_reads_pct', 'paired_bases', 'paired_bases_pct', 'single_reads', 'single_reads_pct', 'single_bases', 'single_bases_pct', 'time', 'reads_processed', 'reads_per_sec', 'bases_processed', 'bases_per_sec']

# 
def procRepairLog(logFileName):
    G11 = open(logFileName)
    repairDict = {}
    for line in G11:
        res = list(filter(line.startswith, fields)) != []
        if res == True:
            line = line.strip('\n')
            # replace(".","")
            line = line.replace("reads","").replace("bases","").replace("(","").replace("%)","").replace("seconds.","").replace("Reads Processed","Reads_Processed").replace("Bases Processed","Bases_Processed").replace(":","").replace("/sec","")
            line = re.sub(' +', ' ',line)
            line = line.replace(" ","\t")
            line = re.sub('\t+','\t',line)
            parts = line.split("\t")
            fld = parts[0]
            repairDict[fld]=parts[1:]
    #print(len(g11dict))
    G11.close()
    return repairDict

# now process the dict 
def getSortDict(fileDict):
    sortDict = {}
    for k,v in fileDict.items():
        values = v
        if k == "Input":
            sortDict["input_reads"]=values[0]
            sortDict["input_bases"]=values[1]
        elif k == "Result":
            sortDict["output_reads"]=values[0]
            sortDict["output_reads_pct"]=values[1]
            sortDict["output_bases"]=values[2]
            sortDict["output_bases_pct"]=values[3]
        elif k == "Pairs":
            sortDict["paired_reads"]=values[0]
            sortDict["paired_reads_pct"]=values[1]
            sortDict["paired_bases"]=values[2]
            sortDict["paired_bases_pct"]=values[3]
        elif k == "Singletons":
            sortDict["single_reads"]=values[0]
            sortDict["single_reads_pct"]=values[1]
            sortDict["single_bases"]=values[2]
            sortDict["single_bases_pct"]=values[3]
        elif k == "Time":
            sortDict["time"]=values[0]
        elif k == "Reads_Processed":
            sortDict["reads_processed"]=values[0]
            sortDict["reads_per_sec"]=values[1]
        elif k == "Bases_Processed":
            sortDict["bases_processed"]=values[0]
            sortDict["bases_per_sec"]=values[1]
    return sortDict

# check for singletons
def checkSingletons(bigDict, sampleList):
    singles = []
    for samp in sampleList:
        if samp in bigDict:
            if float(bigDict[samp]['single_reads']) > 0:
                singles.append(samp)
        else:
            print(samp,' is missing from dictionary')
    return singles

def checkPairs(bigDict, sampleList):
    unpaired = []
    for samp in sampleList:
        if samp in bigDict:
            if float(bigDict[samp]['paired_reads_pct']) < 100:
                unpaired.append(samp)
        else:
            print(samp,' is missing from dictionary')
    return unpaired

def main():
    samplelistOpen = open(args.inputSample, 'r')
    samplelist = []
    for line in samplelistOpen:
        line = line.strip('\n')
        samplelist.append(line)
    samplelistOpen.close()
    masterDict = {}
    for sample in samplelist:
        sampleRepair = procRepairLog(sample+'_repair.log')
        sampleSort = getSortDict(sampleRepair)
        masterDict[sample]=sampleSort
    finalDict = {}
    errorList = []
    for k,v in masterDict.items():
        if len(v) == 0:
            print("Warning, an error has occurred in sample: ", k)
            errorList.append(k)
        else:
            finalDict[k]=v
    if len(errorList) > 0:
        errorFile = open("samples_with_errors.txt", 'w')
        for i in errorList:
            errorFile.write(i+'\n')
        errorFile.close()
    checkSingles = checkSingletons(finalDict,samplelist)
    if len(checkSingles) > 0:
        print("some samples had singletons: ")
        for i in checkSingles:
            print(i)
    else:
        print("no singletons found in any sample")

    checkingPairs = checkPairs(finalDict,samplelist)
    if len(checkingPairs) > 0:
        print("some samples have unequal pairing:")
        for i in checkingPairs:
            print(i)
    else:
        print("all reads paired successfully")
    # output to table 
    outfile = open(args.outtab,'w')
    outfile.write('sample\t')
    for field in fieldList:
        if field == fieldList[-1]:
            outfile.write(field+'\n')
        else:
            outfile.write(field+'\t')
    for sample in samplelist:
        if sample in finalDict:
            vals = finalDict[sample]
            outfile.write(sample+'\t')
            for field in fieldList:
                if field == fieldList[-1]:
                    outfile.write(vals[field]+'\n')
                else:
                    outfile.write(vals[field]+'\t')
    outfile.close()
    print(args.outtab," table output")


if __name__ == "__main__":
    main()
