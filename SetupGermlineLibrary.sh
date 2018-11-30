#!/bin/bash

MAIN=`pwd`

#####################################
# CREATE IMGT DIRECTORY (TEMPORARY) #
#####################################
if [ ! -d $MAIN/IMGT ]; then
   mkdir $MAIN/IMGT
else
   rm -r $MAIN/IMGT
   mkdir $MAIN/IMGT
fi

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=linux;;
    Darwin*)    machine=darwin;;
esac

###############################
# GRAB FILES FROM IMGT SERVER #
###############################
cd $MAIN/IMGT
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/IG/IGHV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/IG/IGHD.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/IG/IGHJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/IG/IGKV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/IG/IGLV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/IG/IGKJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/IG/IGLJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/TR/TRAV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/TR/TRAJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/TR/TRBV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/TR/TRBJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Homo_sapiens/TR/TRBD.fasta

cd $MAIN

######################
# FORMAT FASTA FILES #
######################
if [ -d $MAIN/pyir_data ]; then
    rm -rf $MAIN/pyir_data
fi


mkdir -p $MAIN/pyir_data/Ig/human
mkdir -p $MAIN/pyir_data/TCR/human

cd $MAIN/pyir_data

# Download igblast internal and aux data
# All data can be manually downloaded here ftp://ftp.ncbi.nih.gov/blast/executables/igblast/release or use the following convenience commands
wget -mnH --cut-dirs=4 ftp://ftp.ncbi.nih.gov/blast/executables/igblast/release/internal_data ./
wget -mnH --cut-dirs=5 --directory-prefix=aux ftp://ftp.ncbi.nih.gov/blast/executables/igblast/release/optional_file/ ./

cd $MAIN

###########
# Ig DATA #
###########
cat $MAIN/IMGT/IGHV.fasta  > $MAIN/pyir_data/Ig/human/human_gl_V.fasta
cat $MAIN/IMGT/IGKV.fasta >> $MAIN/pyir_data/Ig/human/human_gl_V.fasta
cat $MAIN/IMGT/IGLV.fasta >> $MAIN/pyir_data/Ig/human/human_gl_V.fasta

cat $MAIN/IMGT/IGHJ.fasta  > $MAIN/pyir_data/Ig/human/human_gl_J.fasta
cat $MAIN/IMGT/IGKJ.fasta >> $MAIN/pyir_data/Ig/human/human_gl_J.fasta
cat $MAIN/IMGT/IGLJ.fasta >> $MAIN/pyir_data/Ig/human/human_gl_J.fasta

cat $MAIN/IMGT/IGHD.fasta  > $MAIN/pyir_data/Ig/human/human_gl_D.fasta

perl $MAIN/edit_imgt_file.pl $MAIN/pyir_data/Ig/human/human_gl_V.fasta > $MAIN/pyir_data/Ig/human/human_gl_V
perl $MAIN/edit_imgt_file.pl $MAIN/pyir_data/Ig/human/human_gl_J.fasta > $MAIN/pyir_data/Ig/human/human_gl_J
perl $MAIN/edit_imgt_file.pl $MAIN/pyir_data/Ig/human/human_gl_D.fasta > $MAIN/pyir_data/Ig/human/human_gl_D


############
# TCR DATA #
############
cat $MAIN/IMGT/TRBV.fasta  > $MAIN/pyir_data/TCR/human/human_gl_V.fasta
cat $MAIN/IMGT/TRAV.fasta >> $MAIN/pyir_data/TCR/human/human_gl_V.fasta

cat $MAIN/IMGT/TRBJ.fasta  > $MAIN/pyir_data/TCR/human/human_gl_J.fasta
cat $MAIN/IMGT/TRAJ.fasta >> $MAIN/pyir_data/TCR/human/human_gl_J.fasta

cat $MAIN/IMGT/TRBD.fasta  > $MAIN/pyir_data/TCR/human/human_gl_D.fasta

perl $MAIN/edit_imgt_file.pl $MAIN/pyir_data/TCR/human/human_gl_V.fasta > $MAIN/pyir_data/TCR/human/human_gl_V
perl $MAIN/edit_imgt_file.pl $MAIN/pyir_data/TCR/human/human_gl_J.fasta > $MAIN/pyir_data/TCR/human/human_gl_J
perl $MAIN/edit_imgt_file.pl $MAIN/pyir_data/TCR/human/human_gl_D.fasta > $MAIN/pyir_data/TCR/human/human_gl_D


############################################
# SET UP IGBLAST DATABASE (LINUX SPECIFIC) #
# CHANGE BINARY TO DARWIN FOR MAC          #
############################################

###########
# IG DATA #
###########
$MAIN/bin/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $MAIN/pyir_data/Ig/human/human_gl_V
$MAIN/bin/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $MAIN/pyir_data/Ig/human/human_gl_J
$MAIN/bin/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $MAIN/pyir_data/Ig/human/human_gl_D

############
# TCR DATA #
############
$MAIN/bin/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $MAIN/pyir_data/TCR/human/human_gl_V
$MAIN/bin/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $MAIN/pyir_data/TCR/human/human_gl_J
$MAIN/bin/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $MAIN/pyir_data/TCR/human/human_gl_D

#########
# TEST  #
#########
cd $MAIN

###########
# TEST IG #
###########
pyir ./testing/1K_Seqs.fasta -d pyir_data -o foobar.json.gz --pretty -f json -r Ig

############
# TEST TCR #
############
#pyir ./testing/1K_Seqs-TCR.fasta -d pyir_data -o foobar.json.gz --pretty -f json -r TCR
