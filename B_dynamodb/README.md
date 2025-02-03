
## DynamoDB

DynamoDB is a fully managed NoSQL database service by AWS that offers high scalability, low latency, and seamless performance for key-value and document data models.

### Strength
- **Scalability**: Automatically scales to handle massive workloads without manual intervention.
- **Performance**: Delivers consistently low latency, making it ideal for real-time applications.
- **Managed Service**: Reduces operational overhead by handling maintenance, backups, and scaling.
Flexible Data Model: Supports key-value and document structures, offering adaptability for various application needs.

### Weakness Compared to SQL Databases:

- **Limited Query Capabilities**: Lacks support for complex queries, joins, and ad-hoc reporting common in SQL databases.
Transaction Support: While it offers transactional capabilities, they are not as extensive as those in traditional relational databases.
- **Schema Flexibility Tradeoffs**: Although schema-less design provides flexibility, it requires careful planning to ensure data consistency and efficient access patterns.
- **Cost Complexity**: High throughput requirements can lead to complex cost management and potential expense spikes.

Overall, DynamoDB is best suited for applications that require high performance and scalability with a flexible data model, while traditional SQL databases are preferable when complex queries, multi-row transactions, and relational data integrity are priorities.

## Code Challenges

### URL Shortener
Given a full URL, encode it as a shortened URL; and given a shortened URL, return the original full URL.

The sample data is from 
https://github.com/ada-url/url-various-datasets/blob/main/top100/top100.txt


### ECommerce
Check the [/data/Ecommerce_data.csv](/data/Ecommerce_data.csv); consider how to store the data records in DynamoDB.

The query pattern:
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
$ python challenge_url_shortener.py
```

## DynamoDB Coding Reference
[official guide: DynamoDB examples using SDK for Python (Boto3)](https://docs.aws.amazon.com/code-library/latest/ug/python_3_dynamodb_code_examples.html)

