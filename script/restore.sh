#!/bin/bash

tmp=$1

option=${tmp: 0: 4}${tmp: 5: 2}${tmp: 8: 2}${tmp: 11: 2}${tmp: 14: 2}${tmp: 17: 2}

echo $option

if [ -d /nubomed/midpkg/drug-middleware/ ]; then
   rm -rf /nubomed/midpkg/db
   rm -rf /nubomed/midpkg/drug-middleware
   cp -r /nubomed/mid_bakup/$option/db /nubomed/midpkg/
   cp -r /nubomed/mid_bakup/$option/drug-middleware /nubomed/midpkg/
elif [ -d /nubomed/consumable-cabinet-service/ ]; then
   project_name=$(ls /nubomed/mid_bakup/$option/)
   rm -rf /nubomed/$project_name
   cp -r /nubomed/mid_bakup/$option/$project_name /nubomed/
elif [ -d /nubomed/ecart-service/ ]; then
   rm -rf /nubomed/ecart-service
   cp -r /nubomed/mid_bakup/$option/ecart-service /nubomed/
else
   echo "type error"
   exit 1
fi