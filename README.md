# Guindex
Once the Guindex source code has been cloned please follow the below steps to
get the Guindex development web server up and running:

1) Install python requirements: `pip install -r requirements.txt`
2) Get secrets.py file from howardrj@tcd.ie and place in GuindexProject/GuindexProject directory.
3) Set GUINDEX_DB_LOCATION variable in secrets.py.
   This will be the location of your development Guindex database.
4) Run database migrations: `python manage.py migrate`
5) Create cache tables: `python manage.py createcachetable guindex_cache`
6) Start django server: `python manage.py runserver <ip>:<port>` 
   where `ip` is the IP address of your machine and `port` is any valid, available TCP port.
7) Open a browser and go to `http://<ip>:<port>`
8) Happy Guindexing! :)
