#!/bin/bash   

TAG=$1
./lemmatize-matches.py $TAG | cut -f 2 | sort | uniq -c | sort -nr | sed -r 's/^( +[0-9]+) /\1\t/g' 
