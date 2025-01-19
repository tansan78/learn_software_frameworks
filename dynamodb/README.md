
## DynamoDB

DynamoDB is the default NoSQL databased provided by AWS.

## Challenge 1
Check the [/data/Ecommerce_data.csv](/data/Ecommerce_data.csv); consider how to store the data records in DynamoDB.

The query pattern:
- given a customer id, return the customer's information like first name, last name, city
- given a customer id, return all the orders made by this customer
- given a customer id and a time frame, return all the orders made within the specified timeframe by this customer
- given a customer id and a matching word, return all the orders by this customer, for which product names contain the matching word

## How to Run?

- open one terminal tab, run the following command to start DynamoDB
```
$ docker compose up
```
- open another terminal tab, run the following command to start virtual envionment
```
$ bash start_venv.sh
```