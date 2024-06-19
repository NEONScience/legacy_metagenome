# legacy_metagenome

a repository to update and track issues for NEON legacy metagenome data

## ISSUE: Incorrect formatting in legacy metagenomic sequencing files 

It was discovered recently that many older NEON metagenomic samples that were sequenced in 2018 – 2019 were not formatted correctly. This issue affects many samples collected from 2014-2018. The fastq files from these sequencing runs are not in error, but the reads in the paired end files are in a different order to each other. Here is the table that lists all samples that may be affected. When evaluating the legacy files, if a sequencing run showed at least some samples that were out of order, then we went ahead and reformatted all the samples in that run. 

Below are more details as well as suggested instructions for repairing the fastq files. These processes require a fair bit of RAM, so best to run them on a server or other HPC. The repaired files will be available with the NEON 2025 release. We can provide links to the repaired files upon request. 

### Detecting the issue 

During the affected time period the laboratory sequenced all samples in a sequencing run across all four lanes of the Illumina NextSeq machine, which resulted in four files for each sample for each strand (R1/R2). These files were then concatenated into a single file for each strand for release. For a period of time these files were concatenated in essentially a random order, so the R1 was often concatenated in a different order than the R2. Therefore, the sequence files are not in order in and of themselves, only out of sync (order) with its corresponding pair. The repair will sort both files the same way for all affected samples. 

The following code illustrates how to detect the order of the four lines for a NEON sample. It takes just the first four parts of a fastq header, which describe: 



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


### Repairing affected files 

The [bbmap](https://jgi.doe.gov/data-and-tools/software-tools/bbtools/bb-tools-user-guide/bbmap-guide/) bioinformatics toolkit was used to repair and verify the fastq files. 

The `repair.sh` script provided by the bbmap package was used to reorient the reads of both R1 and R2 files simultaneously. 

An example for a single sample:

```
SAMPLE='BMI_HWTY2BGX7_18S_12_1111'

repair.sh \
  in1=BMI_${SEQRUN}_mms_R1/${SAMPLE}_R1.fastq.gz \
  in2=BMI_${SEQRUN}_mms_R2/${SAMPLE}_R2.fastq.gz \
  out1=BMI_${SEQRUN}_srt_R1/${SAMPLE}_srt_R1.fastq.gz \
  out2=BMI_${SEQRUN}_srt_R2/${SAMPLE}_srt_R2.fastq.gz \
  repair=t \
  tossbrokenreads=t \
  -Xmx16g \
  2> logs/${SAMPLE}_repair.log


```


