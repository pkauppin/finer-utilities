#!/bin/bash

# Extract all unique tags from FiNER output
# - Any morphological analyses in input are filtered out
# - Exception tags are also excluded
# - Output contains all remaining XML-style tags

sed -r 's/^([^\t]+\t)[^\t]+\t\[POS=[^\t]\t[^\t]\t/\1/g' $1 |
egrep -o '<[^ >]+>' | tr -d '<>/' |
sort | uniq | sed -r '/^Exc[0-9]/d' 
