
## Flask Introduction

Flask is a lightweight and flexible Python web framework that allows developers to quickly build web applications with minimal overhead. It provides essential tools for routing, templating, and handling HTTP requests.

In production environments, multiple Flask processes run concurrently to handle a high volume of user requests. Since each Flask process is stateless, the application can be easily scaled horizontally by adding more processes or servers to distribute the load. Database (like MySQL) needs to be used to store user states.

Read [the Flask user guide](https://flask.palletsprojects.com/en/stable/) if you like.

### Routing

Use the `@app.route` decorator to associate a URL path with a function. Each function returns the content that will be displayed when someone visits that URL. You can read more at [Flask Routing](https://flask.palletsprojects.com/en/stable/quickstart/#routing)

For example, if you define the following code, you can access the page at http://localhost:8080/about
```
# Route for an about page
@app.route('/about')
def some_function():
    return "This is the About Page."
```

## How to Use?

1. In terminal, enter the current directory, then start the Flask container by running:
```
$ docker compose up
```
2. Open browser, and type http://localhost:8080/ to access the main page.
3. Feel free to edit the code in `app/app.py` and save your changes. The Flask container will automatically sync the updated code (you can monitor the sync process in the terminal tab from step 1). Once the sync is complete, refresh your browser to see the changes take effect.
