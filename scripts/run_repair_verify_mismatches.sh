
date
echo 'beginning repair '

cat ${SAMPLE_LIST} | while read SAMPLE
do 
echo "repairing " $SAMPLE
repair.sh \
  in1=BMI_${SEQRUN}_mms_R1/${SAMPLE}_R1.fastq.gz \
  in2=BMI_${SEQRUN}_mms_R2/${SAMPLE}_R2.fastq.gz \
  out1=BMI_${SEQRUN}_srt_R1/${SAMPLE}_srt_R1.fastq.gz \
  out2=BMI_${SEQRUN}_srt_R2/${SAMPLE}_srt_R2.fastq.gz \
  repair=t \
  tossbrokenreads=t \
  -Xmx16g \
  2> logs/${SAMPLE}_repair.log
done

date
echo 'finished repairing, now running verification'

cat ${SAMPLE_LIST} | while read SAMPLE
do 
echo "verifying repair of " $SAMPLE
reformat.sh \
  in1=BMI_${SEQRUN}_srt_R1/${SAMPLE}_srt_R1.fastq.gz \
  in2=BMI_${SEQRUN}_srt_R2/${SAMPLE}_srt_R2.fastq.gz \
  verifypaired=t \
  out=verify_${SEQRUN}/${SAMPLE}_sorted.fastq.gz \
  2> logs/${SAMPLE}_verify.log
done

echo 'ending verification' 
date 

