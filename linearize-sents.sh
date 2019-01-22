#!/bin/bash

#Linearizes FiNER output into running text and outputs it one sentence per line
#The output can be limited to sentences containing the ner tags starting with TAG
#- Prints sentences containing entieties tagged as TAG
#- Sentences are linearized.
#- Nested annotations up to nesting depth of 2 are supported. 
#- Output is sentence per line.
#- If no TAG is specified, ouput all sentences.

TAG=$1

sed -r 's#^([^\t]+)(\t([^\t]*\t)*)<((Enamex|Timex|Numex)[^>]*)/>#<\4>\1</\4>\2#g' |
sed -r 's#^([^\t]+)(\t([^\t]*\t)*)<((Enamex|Timex|Numex)[^>]*)/>#<\4>\1</\4>\2#g' |
sed -r 's#^([^\t]+)(\t([^\t]*\t)*)<((Enamex|Timex|Numex)[^>]*)/>#<\4>\1</\4>\2#g' |
sed -r 's#^([^\t]+)(\t([^\t]*\t)*)<((Enamex|Timex|Numex)[^>/]*)>#<\4>\1\2#g' |
sed -r 's#^([^\t]+)(\t([^\t]*\t)*)<((Enamex|Timex|Numex)[^>/]*)>#<\4>\1\2#g' |
sed -r 's#^([^\t]+)(\t([^\t]*\t)*)<((Enamex|Timex|Numex)[^>/]*)>#<\4>\1\2#g' |
sed -r 's#^([^\t]+)(\t([^\t]*\t)*)</((Enamex|Timex|Numex)[^>/]*)>#\1</\4>\2#g' |
sed -r 's#^([^\t]+)(\t([^\t]*\t)*)</((Enamex|Timex|Numex)[^>/]*)>#\1</\4>\2#g' |
sed -r 's#^([^\t]+)(\t([^\t]*\t)*)</((Enamex|Timex|Numex)[^>/]*)>#\1</\4>\2#g' |
cut -f 1 |
tr '\n ' ' ' |
sed -r 's/  +(<\/[^>]+> *)?/ \1\
/g' |
egrep "<($TAG).*>"
