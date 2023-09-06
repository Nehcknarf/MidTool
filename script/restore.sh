#!/bin/bash

tmp=$1

option=${tmp: 0: 4}${tmp: 5: 2}${tmp: 8: 2}${tmp: 11: 2}${tmp: 14: 2}${tmp: 17: 2}

echo $option

mv /nubomed/midpkg/db /nubomed/midpkg/db_bak
mv /nubomed/midpkg/drug-middleware/ /nubomed/midpkg/drug-middleware_bak

cp -r /nubomed/mid_bakup/$option/db /nubomed/midpkg/
cp -r /nubomed/mid_bakup/$option/drug-middleware /nubomed/midpkg/

rm -rf /nubomed/midpkg/db_bak
rm -rf /nubomed/midpkg/drug-middleware_bak
