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

aws configure set region fakeRegion || { echo "Failed to consigure region"; exit 1; }
aws configure set aws_access_key_id fakeMyKeyId || { echo "Failed to consigure access key id"; exit 1; }
aws configure set aws_secret_access_key fakeSecretAccessKey || { echo "Failed to access key"; exit 1; }

# echo 'done with setip'

laws () {
    aws --endpoint-url http://localhost:8000 "$@"
}
export -f laws

echo ""
echo ""
echo "Ready to run example code. Note 'laws' is created to replace 'aws'"
echo ""

bash