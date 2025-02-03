#!/bin/bash

DATA_DIR="data"

luigi --module luigi-oda-spider GetProducts --base-url "https://oda.com/no"  --target-name "oda" --local-scheduler
 
