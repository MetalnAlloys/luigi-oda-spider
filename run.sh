#!/bin/bash

DATA_DIR="data"
mkdir -p $DATA_DIR

luigi --module luigi-oda-spider GetProducts --base-url "https://oda.com/no"  --target-name "oda" --local-scheduler
