
## Resources

### Python SQL client:
- [PyMySQL](https://pymysql.readthedocs.io/en/latest/modules/connections.html) for MySQL; very simple; not very useful
- [psycopg 3](https://www.psycopg.org/psycopg3/docs/basic/usage.html) for PostGres; detailed

Key points:
- by default, connection does not commit automatically (though we can change this behavior by setting `autocommit=True`); we have to call `conn.commit()` to make it visible to others (or, persistent in storage), or `conn.rollback()` to rollback;
- any pending operations before `conn.commit()` are handled as one transaction;

A typical usage:
```
conn = pymysql.connect(host='localhost',...)
with conn.cursor() as cursor:
  # the following SQL1 and SQL2 are executed as one transaction
  try:
    cursor.execute(SQL1)
    cursor.execute(SQL2)
    conn.commit()
  except DB_ERROR:
    conn.rollback()
```


### Excellent introduction about indexing
[Use the Index Luke](https://use-the-index-luke.com/).

Key points:
- indexing comes with the tax of maintaining indices during update operations; do not over index;
- there are two steps for execution: index reads and table reads;
- do not use index on fields with sparse/broad values (like department ID); using index on broad values alone leads to many table reads (and potentially many index reads);
- do not apply functions (like UPPER, or time operations) on indexed fields in WHERE condition, because it effectively disables indexing. We may apply the function (a.k.a function-based index) when creating the index;
- if there are multi indexed fields involved in WHERE conditions, only one of them can be used. It might be helpful (not always true) to put the most specific/selective index as the first (or, left most) condition in the WHERE clause. We may use concatinated index which uses multi fields as one index;
- LIKE clause disables indexing; some DB may use prefix of the wildcard string for index searching






- step 1:
```
$ docker compose up
```

- step 2: from browser, access [http://localhost:8080/](http://localhost:8080/), login using
  - user name: name@example.com
  - password: admin

- step 3: click to start a new connection, with
  - server/host: postgres
  - user: postgres
  - password: admin


Now, feel free to create tables, insert data, etc
