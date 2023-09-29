# Guindex
Once the Guindex source code has been cloned please follow the below steps to
get the Guindex development web server up and running:

Note 1: Guindex requires python >= 3.7

Note 2: These steps have only been tested on Ubuntu 16.04.7 LTS.

Note 3: Ubuntu 16.04 LTS uses python3.5 by default. Use the following commands to install python3.7:
 
        - sudo add-apt-repository -y ppa:jblgf0/python
        - sudo apt update
        - sudo apt install python3.7
        - unlink /usr/bin/python3
        - ln -fs /usr/bin/python3.7 /usr/bin/python3
	
Note 4: pip3 version 21.3.1 was used.
        Use the get-pip.py script provided in this repo to install this version of pip (i.e. python3 get-pip.py).

1) Install python requirements: `pip install -r requirements.txt`
2) Get guin_secrets.py file from howardrj@tcd.ie and place in GuindexProject/GuindexProject directory.
3) Set GUINDEX_DB_LOCATION variable in guin_secrets.py.
   This will be the location of your development Guindex database (/usr/share/Guindex.db for example).
4) Run database migrations: `sudo env "PATH=$PATH" python3 manage.py migrate`
5) Create map: `sudo env "PATH=$PATH" python3 manage.py GuindexMap`
6) Start django server: `sudo env "PATH=$PATH" python3 manage.py runserver <ip>:<port>` 
7) Open a browser and go to `http://<ip>:<port>`
8) Happy Guindexing! :)
