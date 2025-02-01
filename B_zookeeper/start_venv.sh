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
pip install -r requirements.txt


echo 'Ready to run example code. For example:'
echo '  $ python3 consistent_hashing.py'
echo ''

bash
