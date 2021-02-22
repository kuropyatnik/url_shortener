# URL shortener

## Overview
---

This project provides a RESTful Flask application for URL shortening and redirection. It supports 1KK of unique links at the same time.

Every real URL will have its specific short 6-symbols value. It's made with MD5 hash, based on timestamp of request and real URL string.


## Endpoints
---
1. **/create_url**

POST request for short URL creation. It receives JSON-like parameters:
```JSON
{
    "url": "<valid_url>",
    "lifeterm": <valid_lifeterm> (optional)
}
``` 
Every request should include non-empty correct `url` and _may_ include integer `lifeterm` parameter in range [1, 365] days. 

Important note: if there won't be the `lifeterm` parameter received, a short link will be create with a default value = 90 days.

Codes of responses:

* 409 – There is maximum amount of possible records.
* 400 - Request fields validation error.
* 500 – General error of shortening.
* 200 – Real url is already shortened and valid.
* 201 - Real url has been successfully shortened.

Sample of successful response:

```JSON
{
    "msg": "URL was shorted! Visit: http://127.0.0.1:5000/f60c11",
    "status": "ok"
}
```

2. **/<short_url>**

GET request for redirection. It takes `short_url` value from a request, attempts to find such key in DB and redirects to the original URL (if any).

Codes of responses:

* 404 - there is no such short URL or it's expired.
* 302 - redirection to the real URL.


## Virtual environment installation
---

There was used `Python 3.8.5`. It's highly recommended to install virtual environment to the project root with `venv` title and then install all required modules from `requirements.txt`.

```Bash
pip install -r requirements.txt
```

After that, you can run flask application from the project root with a next command:
```
python main.py
```

## Database connection
---

This project uses MySQL database with `pymysql` dialect. To provide smooth connection, please, make following steps on your server.

1. Install MySQL Server and ensure, that you have root rights.
2. Create user with password in the mysql console (or whatever way you prefer).
3. Create `.env` environment file in the root of this project with next vars.
```
DB_HOST=<YOUR_DB_HOST>
DB_USERNAME=<YOUR_DB_USERNAME>
DB_PASSWD=<YOUR_DB_PASSWD>
DB_NAME=<YOUR_DB_NAME>
```
4. Grant all priveleges to that user in the mysql console for all databases.
```SQL
GRANT ALL PRIVILEGES ON *.* TO `<YOUR_DB_USERNAME>`@`<YOUR_DB_HOST>`;
```
After that, there will be created a connection to the DB with prepared table.


## Testing
---

There are unittests to cover basic logic of projects. To execute them, call next command (under venv):
```Bash
python -m unittest tests/test_main.py 
```

They mock a Flask application and check different use cases of both endpoints (+ their integration with DB).

## Additional info
---

1. There is a scheduled task, which cleanups DB from expired records. It works every 24 hours after server start.
2. If a hash part won't be unique, then app will try to shift to the next slice and use it as a key.

## Future improvements
---

* ORM usage. In order to simplify additional models creation and testing procedure.
* Authorization. Because of security issues and specific user URL keys maintaining.
* Test coverage increasement.
* Replace encryption to another algorithm. 
* Use system cronjobs instead of built-in Flask scheduled tasks and adapt its frequency. To ensure that such task will be executed even if the server is falled.
* Count calls for each short URL to redirect.