# URL shortener

## Database connection

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