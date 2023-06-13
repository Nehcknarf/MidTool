#!/bin/bash

path=$1

pm2 start $path -m
pm2 save -m