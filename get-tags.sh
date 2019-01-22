#!/bin/bash

sed -r 's/^([^\t]+\t)[^\t]+\t\[POS=[^\t]\t[^\t]\t/\1/g' $1 |
egrep -o '<[^ >]+>' | tr -d '<>/' |
sort | uniq |
sed -r '/^Exc[0-9]/d' 
