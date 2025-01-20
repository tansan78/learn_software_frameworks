#!/bin/bash

if [ -d venv ]; then
    echo 'Virtual Environment at ./venv already exists'
else
    echo 'make Virtual Environment at ./venv' 
    python3 -m venv venv
fi


# activiate virtual envrionment
echo 'Activate Virtual Environment at ./venv' 
source venv/bin/activate


# install dependency
pip install -r requirements.txt || { echo 'Failed to install packages'; exit 1; }

echo ""
echo ""
echo "Ready to run example code."
echo ""

bash