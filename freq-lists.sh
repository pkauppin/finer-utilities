#!/bin/bash

INFILE=$1

for TAG in $( ./get-tags.sh $INFILE ) ; do
    cat $INFILE | ./lemmatized-freqs.sh $TAG > freqs_$TAG.tsv
done
