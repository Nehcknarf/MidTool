#!/bin/bash

tmp=$1

option=${tmp: 0: 4}${tmp: 5: 2}${tmp: 8: 2}${tmp: 11: 2}${tmp: 14: 2}${tmp: 17: 2}

echo $option

if [ -d /nubomed/midpkg/drug-middleware/ ]; then
   echo "Cleaning..."
   rm -rf /nubomed/midpkg/db
   rm -rf /nubomed/midpkg/drug-middleware
   echo "Restore Backup..."
   cp -r /nubomed/mid_bakup/$option/db /nubomed/midpkg/
   cp -r /nubomed/mid_bakup/$option/drug-middleware /nubomed/midpkg/
elif [ -d /nubomed/consumable-cabinet-service/ ]; then
   project_name=$(ls /nubomed/mid_bakup/$option/)
   echo "Cleaning..."
   rm -rf /nubomed/$project_name
   echo "Restore Backup..."
   cp -r /nubomed/mid_bakup/$option/$project_name /nubomed/
elif [ -d /nubomed/ecart-service/ ]; then
   echo "Cleaning..."
   rm -rf /nubomed/ecart-service
   rm -rf /nubomed/data
   rm -rf /nubomed/libs
   echo "Restore Backup..."
   cp -r /nubomed/mid_bakup/$option/ecart-service /nubomed/
   cp -r /nubomed/mid_bakup/$option/data /nubomed/
   cp -r /nubomed/mid_bakup/$option/libs /nubomed/
else
   echo "type error"
   exit 1
fi