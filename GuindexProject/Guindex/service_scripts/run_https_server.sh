#!/usr/bin/bash
python manage.py runserver_plus --cert-file /etc/letsencrypt/live/guindex.ie/cert.crt --key-file /etc/letsencrypt/live/guindex.ie/key.key 45.79.148.4:8000
