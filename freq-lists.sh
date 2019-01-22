#!/bin/bash

# Creates frequency lists for all NE categories found in input

INFILE=$1

for TAG in $( ./get-tags.sh $INFILE ) ; do
    cat $INFILE | ./lemmatized-freqs.sh $TAG > freqs_$TAG.tsv
done
