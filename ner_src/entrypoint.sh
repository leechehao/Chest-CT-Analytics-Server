#!/bin/sh
set -e

if [ -x "$(command -v nvidia-smi)" ]; then
    export CUDA_AVAILABLE=true
else
    export CUDA_AVAILABLE=false
fi

exec python app.py