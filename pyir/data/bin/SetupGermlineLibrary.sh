#!/bin/bash

PWD=`pwd`
BASEDIR=$1
OUTDIR=$2
MAIN=$PWD

echo $BASEDIR
echo $OUTDIR
echo $MAIN


#####################################
# CREATE IMGT DIRECTORY (TEMPORARY) #
#####################################
if [ ! -d $MAIN/IMGT ]; then
   mkdir $MAIN/IMGT
else
   rm -r $MAIN/IMGT
   mkdir $MAIN/IMGT
fi

mkdir $MAIN/IMGT/human
mkdir $MAIN/IMGT/mouse
mkdir $MAIN/IMGT/rabbit
mkdir $MAIN/IMGT/rat
mkdir $MAIN/IMGT/rhesus_monkey

unameOut="$(uname -s)"
echo $unameOut
case "${unameOut}" in
    Linux*)     machine=linux;;
    Darwin*)    machine=darwin;;
esac

###############################
# GRAB FILES FROM IMGT SERVER #
###############################
cd $MAIN/IMGT/human
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

cd ../mouse
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/IG/IGHV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/IG/IGHD.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/IG/IGHJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/IG/IGKV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/IG/IGLV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/IG/IGKJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/IG/IGLJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/TR/TRAJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/TR/TRAV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/TR/TRBD.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/TR/TRBJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/TR/TRBV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/TR/TRDD.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/TR/TRDJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/TR/TRDV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/TR/TRGJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Mus_musculus/TR/TRGV.fasta

cd ../rabbit
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/IG/IGHV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/IG/IGHD.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/IG/IGHJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/IG/IGKV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/IG/IGLV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/IG/IGKJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/IG/IGLJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/TR/TRAJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/TR/TRAV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/TR/TRBD.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/TR/TRBJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/TR/TRBV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/TR/TRDD.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/TR/TRDJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/TR/TRDV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/TR/TRGJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Oryctolagus_cuniculus/TR/TRGV.fasta

cd ../rat
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Rattus_norvegicus/IG/IGHV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Rattus_norvegicus/IG/IGHD.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Rattus_norvegicus/IG/IGHJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Rattus_norvegicus/IG/IGKV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Rattus_norvegicus/IG/IGLV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Rattus_norvegicus/IG/IGKJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Rattus_norvegicus/IG/IGLJ.fasta

cd ../rhesus_monkey
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/IG/IGHV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/IG/IGHD.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/IG/IGHJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/IG/IGKV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/IG/IGLV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/IG/IGKJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/IG/IGLJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/TR/TRAJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/TR/TRAV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/TR/TRBD.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/TR/TRBJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/TR/TRBV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/TR/TRDD.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/TR/TRDJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/TR/TRDV.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/TR/TRGJ.fasta
wget -A fasta -r -l 1 -nd http://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/Macaca_mulatta/TR/TRGV.fasta

cd ../../

######################
# FORMAT FASTA FILES #
######################
#if [ -d $MAIN/pyir_data ]; then
#    rm -rf $MAIN/pyir_data
#fi

mkdir -p $OUTDIR/Ig/human
mkdir -p $OUTDIR/Ig/mouse
mkdir -p $OUTDIR/Ig/rabbit
mkdir -p $OUTDIR/Ig/rat
mkdir -p $OUTDIR/Ig/rhesus_monkey
mkdir -p $OUTDIR/TCR/human
mkdir -p $OUTDIR/TCR/mouse
mkdir -p $OUTDIR/TCR/rabbit
mkdir -p $OUTDIR/TCR/rat
mkdir -p $OUTDIR/TCR/rhesus_monkey

#mkdir -p $MAIN/pyir_data/Ig/human
#mkdir -p $MAIN/pyir_data/TCR/human

cd $OUTDIR

# Download igblast internal and aux_data data
# All data can be manually downloaded here ftp://ftp.ncbi.nih.gov/blast/executables/igblast/release or use the following convenience commands
wget -mnH --cut-dirs=4 ftp://ftp.ncbi.nih.gov/blast/executables/igblast/release/internal_data ./
wget -mnH --cut-dirs=5 --directory-prefix=aux_data ftp://ftp.ncbi.nih.gov/blast/executables/igblast/release/optional_file/ ./

cd $MAIN

#################
# Human Ig and TCR DATA #
#################
cat $MAIN/IMGT/human/IGHV.fasta  > $OUTDIR/Ig/human/human_gl_V.fasta
cat $MAIN/IMGT/human/IGKV.fasta >> $OUTDIR/Ig/human/human_gl_V.fasta
cat $MAIN/IMGT/human/IGLV.fasta >> $OUTDIR/Ig/human/human_gl_V.fasta

cat $MAIN/IMGT/human/IGHJ.fasta  > $OUTDIR/Ig/human/human_gl_J.fasta
cat $MAIN/IMGT/human/IGKJ.fasta >> $OUTDIR/Ig/human/human_gl_J.fasta
cat $MAIN/IMGT/human/IGLJ.fasta >> $OUTDIR/Ig/human/human_gl_J.fasta

cat $MAIN/IMGT/human/IGHD.fasta  > $OUTDIR/Ig/human/human_gl_D.fasta

perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/human/human_gl_V.fasta > $OUTDIR/Ig/human/human_gl_V
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/human/human_gl_J.fasta > $OUTDIR/Ig/human/human_gl_J
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/human/human_gl_D.fasta > $OUTDIR/Ig/human/human_gl_D

cat $MAIN/IMGT/human/TRAV.fasta >> $OUTDIR/TCR/human/human_TCR_V.fasta
cat $MAIN/IMGT/human/TRBV.fasta  > $OUTDIR/TCR/human/human_TCR_V.fasta

cat $MAIN/IMGT/human/TRAJ.fasta >> $OUTDIR/TCR/human/human_TCR_J.fasta
cat $MAIN/IMGT/human/TRBJ.fasta  > $OUTDIR/TCR/human/human_TCR_J.fasta

cat $MAIN/IMGT/human/TRBD.fasta  > $OUTDIR/TCR/human/human_TCR_D.fasta

perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/human/human_TCR_V.fasta > $OUTDIR/TCR/human/human_TCR_V
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/human/human_TCR_J.fasta > $OUTDIR/TCR/human/human_TCR_J
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/human/human_TCR_D.fasta > $OUTDIR/TCR/human/human_TCR_D

$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/human/human_gl_V
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/human/human_gl_J
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/human/human_gl_D
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/human/human_TCR_V
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/human/human_TCR_J
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/human/human_TCR_D

#################
# Mouse Ig and TCR DATA #
#################
cat $MAIN/IMGT/mouse/IGHV.fasta  > $OUTDIR/Ig/mouse/mouse_gl_V.fasta
cat $MAIN/IMGT/mouse/IGKV.fasta >> $OUTDIR/Ig/mouse/mouse_gl_V.fasta
cat $MAIN/IMGT/mouse/IGLV.fasta >> $OUTDIR/Ig/mouse/mouse_gl_V.fasta

cat $MAIN/IMGT/mouse/IGHJ.fasta  > $OUTDIR/Ig/mouse/mouse_gl_J.fasta
cat $MAIN/IMGT/mouse/IGKJ.fasta >> $OUTDIR/Ig/mouse/mouse_gl_J.fasta
cat $MAIN/IMGT/mouse/IGLJ.fasta >> $OUTDIR/Ig/mouse/mouse_gl_J.fasta

cat $MAIN/IMGT/mouse/IGHD.fasta  > $OUTDIR/Ig/mouse/mouse_gl_D.fasta

perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/mouse/mouse_gl_V.fasta > $OUTDIR/Ig/mouse/mouse_gl_V
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/mouse/mouse_gl_J.fasta > $OUTDIR/Ig/mouse/mouse_gl_J
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/mouse/mouse_gl_D.fasta > $OUTDIR/Ig/mouse/mouse_gl_D

cat $MAIN/IMGT/mouse/TRAV.fasta > $OUTDIR/TCR/mouse/mouse_TCR_V.fasta
cat $MAIN/IMGT/mouse/TRBV.fasta >> $OUTDIR/TCR/mouse/mouse_TCR_V.fasta
cat $MAIN/IMGT/mouse/TRDV.fasta >> $OUTDIR/TCR/mouse/mouse_TCR_V.fasta
cat $MAIN/IMGT/mouse/TRGV.fasta >> $OUTDIR/TCR/mouse/mouse_TCR_V.fasta

cat $MAIN/IMGT/mouse/TRAJ.fasta > $OUTDIR/TCR/mouse/mouse_TCR_J.fasta
cat $MAIN/IMGT/mouse/TRBJ.fasta >> $OUTDIR/TCR/mouse/mouse_TCR_J.fasta
cat $MAIN/IMGT/mouse/TRDJ.fasta >> $OUTDIR/TCR/mouse/mouse_TCR_J.fasta
cat $MAIN/IMGT/mouse/TRGJ.fasta >> $OUTDIR/TCR/mouse/mouse_TCR_J.fasta

cat $MAIN/IMGT/mouse/TRBD.fasta  > $OUTDIR/TCR/mouse/mouse_TCR_D.fasta
cat $MAIN/IMGT/mouse/TRDD.fasta >> $OUTDIR/TCR/mouse/mouse_TCR_D.fasta

perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/mouse/mouse_TCR_V.fasta > $OUTDIR/TCR/mouse/mouse_TCR_V
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/mouse/mouse_TCR_J.fasta > $OUTDIR/TCR/mouse/mouse_TCR_J
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/mouse/mouse_TCR_D.fasta > $OUTDIR/TCR/mouse/mouse_TCR_D

$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/mouse/mouse_gl_V
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/mouse/mouse_gl_J
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/mouse/mouse_gl_D
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/mouse/mouse_TCR_V
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/mouse/mouse_TCR_J
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/mouse/mouse_TCR_D

#################
# Rabbit Ig and TCR DATA #
#################
cat $MAIN/IMGT/rabbit/IGHV.fasta  > $OUTDIR/Ig/rabbit/rabbit_gl_V.fasta
cat $MAIN/IMGT/rabbit/IGKV.fasta >> $OUTDIR/Ig/rabbit/rabbit_gl_V.fasta
cat $MAIN/IMGT/rabbit/IGLV.fasta >> $OUTDIR/Ig/rabbit/rabbit_gl_V.fasta

cat $MAIN/IMGT/rabbit/IGHJ.fasta  > $OUTDIR/Ig/rabbit/rabbit_gl_J.fasta
cat $MAIN/IMGT/rabbit/IGKJ.fasta >> $OUTDIR/Ig/rabbit/rabbit_gl_J.fasta
cat $MAIN/IMGT/rabbit/IGLJ.fasta >> $OUTDIR/Ig/rabbit/rabbit_gl_J.fasta

cat $MAIN/IMGT/rabbit/IGHD.fasta  > $OUTDIR/Ig/rabbit/rabbit_gl_D.fasta

perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/rabbit/rabbit_gl_V.fasta > $OUTDIR/Ig/rabbit/rabbit_gl_V
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/rabbit/rabbit_gl_J.fasta > $OUTDIR/Ig/rabbit/rabbit_gl_J
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/rabbit/rabbit_gl_D.fasta > $OUTDIR/Ig/rabbit/rabbit_gl_D

cat $MAIN/IMGT/rabbit/TRAV.fasta > $OUTDIR/TCR/rabbit/rabbit_TCR_V.fasta
cat $MAIN/IMGT/rabbit/TRBV.fasta >> $OUTDIR/TCR/rabbit/rabbit_TCR_V.fasta
cat $MAIN/IMGT/rabbit/TRDV.fasta >> $OUTDIR/TCR/rabbit/rabbit_TCR_V.fasta
cat $MAIN/IMGT/rabbit/TRGV.fasta >> $OUTDIR/TCR/rabbit/rabbit_TCR_V.fasta

cat $MAIN/IMGT/rabbit/TRAJ.fasta > $OUTDIR/TCR/rabbit/rabbit_TCR_J.fasta
cat $MAIN/IMGT/rabbit/TRBJ.fasta >> $OUTDIR/TCR/rabbit/rabbit_TCR_J.fasta
cat $MAIN/IMGT/rabbit/TRDJ.fasta >> $OUTDIR/TCR/rabbit/rabbit_TCR_J.fasta
cat $MAIN/IMGT/rabbit/TRGJ.fasta >> $OUTDIR/TCR/rabbit/rabbit_TCR_J.fasta

cat $MAIN/IMGT/rabbit/TRBD.fasta  > $OUTDIR/TCR/rabbit/rabbit_TCR_D.fasta
cat $MAIN/IMGT/rabbit/TRDD.fasta >> $OUTDIR/TCR/rabbit/rabbit_TCR_D.fasta

perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/rabbit/rabbit_TCR_V.fasta > $OUTDIR/TCR/rabbit/rabbit_TCR_V
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/rabbit/rabbit_TCR_J.fasta > $OUTDIR/TCR/rabbit/rabbit_TCR_J
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/rabbit/rabbit_TCR_D.fasta > $OUTDIR/TCR/rabbit/rabbit_TCR_D

$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/rabbit/rabbit_gl_V
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/rabbit/rabbit_gl_J
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/rabbit/rabbit_gl_D
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/rabbit/rabbit_TCR_V
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/rabbit/rabbit_TCR_J
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/rabbit/rabbit_TCR_D

#################
# Rat Ig DATA #
#################
cat $MAIN/IMGT/rat/IGHV.fasta  > $OUTDIR/Ig/rat/rat_gl_V.fasta
cat $MAIN/IMGT/rat/IGKV.fasta >> $OUTDIR/Ig/rat/rat_gl_V.fasta
cat $MAIN/IMGT/rat/IGLV.fasta >> $OUTDIR/Ig/rat/rat_gl_V.fasta

cat $MAIN/IMGT/rat/IGHJ.fasta  > $OUTDIR/Ig/rat/rat_gl_J.fasta
cat $MAIN/IMGT/rat/IGKJ.fasta >> $OUTDIR/Ig/rat/rat_gl_J.fasta
cat $MAIN/IMGT/rat/IGLJ.fasta >> $OUTDIR/Ig/rat/rat_gl_J.fasta

cat $MAIN/IMGT/rat/IGHD.fasta  > $OUTDIR/Ig/rat/rat_gl_D.fasta

perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/rat/rat_gl_V.fasta > $OUTDIR/Ig/rat/rat_gl_V
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/rat/rat_gl_J.fasta > $OUTDIR/Ig/rat/rat_gl_J
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/rat/rat_gl_D.fasta > $OUTDIR/Ig/rat/rat_gl_D

$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/rat/rat_gl_V
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/rat/rat_gl_J
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/rat/rat_gl_D

#################
# Rhesus Monkey Ig and TCR DATA #
#################
cat $MAIN/IMGT/rhesus_monkey/IGHV.fasta  > $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_V.fasta
cat $MAIN/IMGT/rhesus_monkey/IGKV.fasta >> $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_V.fasta
cat $MAIN/IMGT/rhesus_monkey/IGLV.fasta >> $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_V.fasta

cat $MAIN/IMGT/rhesus_monkey/IGHJ.fasta  > $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_J.fasta
cat $MAIN/IMGT/rhesus_monkey/IGKJ.fasta >> $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_J.fasta
cat $MAIN/IMGT/rhesus_monkey/IGLJ.fasta >> $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_J.fasta

cat $MAIN/IMGT/rhesus_monkey/IGHD.fasta  > $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_D.fasta

perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_V.fasta > $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_V
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_J.fasta > $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_J
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_D.fasta > $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_D

cat $MAIN/IMGT/rhesus_monkey/TRAV.fasta > $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_V.fasta
cat $MAIN/IMGT/rhesus_monkey/TRBV.fasta >> $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_V.fasta
cat $MAIN/IMGT/rhesus_monkey/TRDV.fasta >> $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_V.fasta
cat $MAIN/IMGT/rhesus_monkey/TRGV.fasta >> $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_V.fasta

cat $MAIN/IMGT/rhesus_monkey/TRAJ.fasta > $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_J.fasta
cat $MAIN/IMGT/rhesus_monkey/TRBJ.fasta >> $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_J.fasta
cat $MAIN/IMGT/rhesus_monkey/TRDJ.fasta >> $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_J.fasta
cat $MAIN/IMGT/rhesus_monkey/TRGJ.fasta >> $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_J.fasta

cat $MAIN/IMGT/rhesus_monkey/TRBD.fasta  > $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_D.fasta
cat $MAIN/IMGT/rhesus_monkey/TRDD.fasta >> $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_D.fasta

perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_V.fasta > $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_V
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_J.fasta > $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_J
perl $BASEDIR/edit_imgt_file.pl $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_D.fasta > $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_D

$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_V
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_J
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/Ig/rhesus_monkey/rhesus_monkey_gl_D
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_V
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_J
$BASEDIR/makeblastdb_${machine} -dbtype nucl -hash_index -parse_seqids -in $OUTDIR/TCR/rhesus_monkey/rhesus_monkey_TCR_D

rm -r $MAIN/IMGT