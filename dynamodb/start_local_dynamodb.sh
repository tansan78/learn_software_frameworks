#!/bin/bash

if [ ! -n `which java` ]; then
  echo "Java NOT installed! Please install JAVA first"
  exit 1
fi


cur_dir=$(basename "$PWD")
if [ $cur_dir != "dynamodb_local_server" ]; then
    if [ ! -d "dynamodb_local_server" ]; then
        mkdir "dynamodb_local_server"
    fi
    cd "dynamodb_local_server"
fi


if [ ! -f DynamoDBLocal.jar ]; then
    if [ ! -f dynamodb_local_latest.zip ]; then
        curl -O https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.zip || {
            echo "Failed to download dynamodb_local_latest.zip"
            exit 2
        }
    fi
    unzip dynamodb_local_latest.zip
fi

java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb || {
    echo "Failed to start dynamodb local server"
    exit 3
}
