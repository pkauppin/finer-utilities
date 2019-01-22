#!/bin/bash

# Flattens tabular FiNER output back into running text.
# Line breaks are inserted after certain elements such as 'paragraph' and 'h1'.

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
tr -s ' \n' ' ' |
sed -r 's# *<p> *#<p> #g' |
sed -r 's# *(</(p|h[12345]|text|body|html|paragraph)>) *# \1\
\
#g'
