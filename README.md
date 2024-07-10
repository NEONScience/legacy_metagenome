# legacy_metagenome

a repository to update and track issues for NEON legacy metagenome data

## ISSUE: Incorrect formatting in legacy metagenomic sequencing files 

It was discovered recently that many older NEON metagenomic samples that were sequenced in 2018 – 2019 were not formatted correctly. This issue affects many samples collected from 2014-2018. The fastq files from these sequencing runs are not in error, but the reads in the paired end files are in a different order to each other. The variable formatting prevents automated bioinformatics workflows from interleaving paired reads. The effect of this issue on other analyses, such as assembly, is not known. As we gather more information we will post it here. 

[Here is the table](https://github.com/NEONScience/legacy_metagenome/blob/main/docs/neon_samples_potentially_mispaired.tsv) that lists all samples that may be affected. When evaluating the legacy files, if a sequencing run showed at least some samples that were out of order, then we went ahead and reformatted all the samples in that run. 

Below are more details as well as suggested instructions for repairing the fastq files. These processes require a fair bit of RAM, so best to run them on a server or other HPC. The repaired files will be available with the NEON 2025 release. We can provide links to the repaired files upon request. Note that the following instructions assume that the user has some experience with the command line and using basic bash tools (e.g. `head`, `grep`, `cut`). You should also have installed [**BBMap**](https://jgi.doe.gov/data-and-tools/software-tools/bbtools/bb-tools-user-guide/bbmap-guide/). If you need any help, please [contact us](https://www.neonscience.org/about/contact-us) or create a new issue on this repository. 

### Detecting the issue 

During the affected time period the laboratory sequenced all samples in a sequencing run across all four lanes of the Illumina NextSeq machine, which resulted in four files for each sample for each strand (R1/R2). These files were then concatenated into a single file for each strand for release. For a period of time these files were concatenated in essentially a random order, so the R1 was often concatenated in a different order than the R2. Therefore, the sequence files are not in order in and of themselves, only out of sync (order) with its corresponding pair. The repair will sort both files the same way for all affected samples. 

The following code illustrates how to detect the order of the four lanes in a legacy NEON sample. It takes just the first four parts of a fastq header, which give the instrument ID, run number, flowcell ID, and lane number of the sequence (colon delimited): 

```
@<instrument>:<run number>:<flowcell ID>:<lane>
```

An example sequence header:

`@NB551228:47:HWTY2BGX7:1` in which:

`@` = all sequence identifiers start with @

`NB551228` = instrument ID

`47` = instrument run number

`HWTY2BGX7` = flow cell ID

`1` = lane number

For a complete description of fastq files and headers, [see this link](https://help.basespace.illumina.com/files-used-by-basespace/fastq-files).



```
i='BMI_HWTY2BGX7_18S_12_1111'

headCode=$(zcat  ${i}_R1.fastq.gz | head -1 | cut -f 1-3 -d ':')

zgrep "${headCode}" ${i}_R1.fastq.gz | cut -f 1-4 -d ':' | uniq 
@NB551228:47:HWTY2BGX7:1
@NB551228:47:HWTY2BGX7:3
@NB551228:47:HWTY2BGX7:2
@NB551228:47:HWTY2BGX7:4

# and with the R2 file:
zgrep "${headCode}" ${i}_R2.fastq.gz | cut -f 1-4 -d ':' | uniq 
@NB551228:47:HWTY2BGX7:3
@NB551228:47:HWTY2BGX7:1
@NB551228:47:HWTY2BGX7:2
@NB551228:47:HWTY2BGX7:4

```

In the above example, you can see that the R1 file has the lanes in order of 1,3,2,4; while the R2 file has them in the order of 3,1,2,4. These two pairs would not interleave. 


## Repairing affected files 

The [bbmap](https://jgi.doe.gov/data-and-tools/software-tools/bbtools/bb-tools-user-guide/bbmap-guide/) bioinformatics toolkit was used to repair and verify the fastq files. 

The `repair.sh` script provided by the bbmap package was used to reorient the reads of both R1 and R2 files simultaneously. 

An example for a single sample:

```
SAMPLE='BMI_HWTY2BGX7_18S_12_1111'

repair.sh \
  in1=${SAMPLE}_R1.fastq.gz \
  in2=${SAMPLE}_R2.fastq.gz \
  out1=${SAMPLE}_srt_R1.fastq.gz \
  out2=${SAMPLE}_srt_R2.fastq.gz \
  repair=t \
  tossbrokenreads=t \
  -Xmx20g \
  2> logs/${SAMPLE}_repair.log

```

Where: 

`in1` is the forward (R1) sequence file

`in2` is the reverse (R2) sequence file

`out1` is the output sorted R1 sequence file

`out2` is the output sorted R2 sequence file

The `repair=t` argument will repair out of sync reads between the files
the `tossbrokenreads=t` argument will throw out any excess reads found in one file but not the other (this will help if one of the files is truncated)

As bbmap is a Java-based tool, the `-Xmx20g` tells the program how much RAM to use. In this case 20 GB of RAM were used. I found that for most of the NEON legacy files, this was sufficient. 

Finally, the `2> logs/${SAMPLE}_repair.log` part of the command will send the text summary output to a file for later reference. This is optional. 

There are other bbmap tools that can do the same job. The tool `sortbyname.sh` can be used to sort each file individually. One useful feature of this tool is that for very large files it can split the file into several temporary files to better handle the memory demand. 

```
 sortbyname.sh \
  in=${SAMPLE}_R2.fastq.gz \
  out=${SAMPLE}_srt_R2.fastq.gz \
  -Xmx20g
```

Note that the `-Xmx20g` argument is optional, but it is a good idea to make explicit how much memory is available. 

### Creating interleaved fastq files

If you would like to create a single interleaved file from the separate R1 and R2 files for your downstream work, the bbmap tool `reformat.sh` can do that. NEON metagenomic fastq files are kept as separate R1/R2 files, but all files were interleaved as a verification check. 

Here is an example of using the `reformat.sh` tool.

```
 reformat.sh \
    in1=${SAMPLE}_R1.fastq.gz \
    in2=${SAMPLE}_R2.fastq.gz \
    verifypaired=t \
    out=${SAMPLE}_interleaved.fastq.gz \
    2> ${SAMPLE}_verify.log
```

### Processing multiple files 

Chances are you have more than one or two files that you will need to repair. The scripts folder in this repo contains the shell script `run_repair_verify_mismatches.sh`, which will repair and verify a set of samples provided by a list. This script was run with a Docker bbmap image. The following code illustrates how this script was run using the Docker image, using one of the sequencing runs as an example.

```
docker pull bryce911/bbtools:39.06

SEQRUN='HWTY2BGX7'

# get the names from the folder containing the R1 files
ls BMI_${SEQRUN}_mms_R1/ | cut -f 2 -d '/' | sed 's/_R1\.fastq\.gz//' > ${SEQRUN}_samples.txt

# make a directory for logs output
mkdir logs

# run the script through the docker container
docker run -t -i \
  -v $(pwd):/data \
  -v /tempfiles/fix_mismatched_mms/scripts:/scripts \
  -w /data \
  -e SEQRUN=${SEQRUN} \
  -e SAMPLE_LIST=${SEQRUN}_samples.txt \
  bryce911/bbtools:39.06 \
  sh /scripts/run_repair_verify_mismatches.sh

```

Note: in the `docker run` command above the first `-v` parameters transfers the present directory to the container, while the second makes the scripts available within the container. The `-w` makes `/data` the working directory. The environmental variables used in the script are transferred to the container with the `-e` parameters. 

After running the repair/verify script above, a Python script (in scripts folder: `compile_repair_logs.py`) was used to check that all reads paired and there were no excess reads in either of the paired files. This script also creates a table from the repair log files, an example of which is found in the `test` folder. 

```
SEQRUN='HWTY2BGX7'

# first make a list of all repair logs 
cd logs
ls *_repair.log | sed -e 's/_repair.log//' > ${SEQRUN}_repair_list.txt

python3 /path/to/script/compile_repair_logs.py -i ${SEQRUN}_repair_list.txt -o ../${SEQRUN}_repairlog.tsv

```

To check that all reads could be correctly paired, the logs from the verify component of the script were checked. If the forward and reverse files created an interleaved file successfully, the verify.log file will end with the phrase: "Names appear to be correctly paired". The following bit of code simply checks for the number of verified samples, which should match the number of input samples.

```
cd logs

for lg in *_verify.log; do VER=$(grep 'correctly paired' $lg); echo -e ${lg}' '${VER} >> verification1.txt  ; done

# now check how many 
grep -c 'correctly paired' verification1.txt 
# 57 was the number of samples for this sequencing run

```

