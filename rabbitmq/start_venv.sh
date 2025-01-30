#!/bin/bash

if [ -d venv ]; then
    echo 'Virtual Environment at ./venv already exists'
else
    echo 'make Virtual Environment at ./venv' 
    python3 -m venv venv || { echo 'Failed to make virtual environment'; exit 1; }
fi


# activiate virtual envrionment
echo 'Activate Virtual Environment at ./venv' 
source venv/bin/activate  || { echo 'Failed to load virtual environment'; exit 2; }


# install dependency
pip install -r requirements.txt || { echo 'Failed to install dependencies'; exit 2; }


echo ""
echo ""
echo "Ready to run example code. "
echo ""

bash