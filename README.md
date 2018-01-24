# Guindex
Below are the instructions to run the Guindex web app locally.

1. First ensure you have python 2.7 and django 1.11 installed on your system (other versions of django may work but I have only tested with 1.11.7).

2. You will also need to install the following django apps:

   rest_framework (http://www.django-rest-framework.org/#installation)

   coreapi (http://www.django-rest-framework.org/api-guide/schemas/#install-core-api)

   corsheaders (https://github.com/ottoyiu/django-cors-headers)

3. Clone the repository:

   git clone https://github.com/howardrj/Guindex

4. Pull updates from the UserProfile and TelegramUser submodules:

   git submodule update --init --recursive
   
5. Create secrets.py in GuindexProject/GuindexProject (i.e. same level as settings.py).
   Copy below file and add your own email and password:
   
   EMAIL = <email_address_to_send_automated_emails_from>
   
   PASSWORD = <above_email_password>
   
   KEY = '3u6cs5sx1z*oa_@+k1thb0gw=dixl(sj2b&r&ih!s%vfvlzi$a'
   
   BOT_HTTP_API_TOKEN = '197671869:AAH8dNkBfoz1CqQEIjXAvGt2HN2YA2QxfUw'

   GOOGLE_MAPS_API_KEY = 'AIzaSyBv5uZT5FVK1ASoYXhnlheDrjLR_EMxSaU'
   
6. Make migrations. Converts models.py to SQL statements:

   sudo python manage.py makemigrations
   
   Note if you don't have a sudo password you will need to change the log file locations at the end of settings.py
   to not be in /var/log/ (i.e. somewhere where you have read/write access).
   
7. Migrate. Create database with models tables:

   sudo python manage.py migrate
   
   Note if you don't have a sudo password you will need to change the database location in settings.py to not be in /usr/share/ (i.e somewhere you have read/write access).
   
8. Run django development server:

   python manage.py runserver
   
9. Open 127.0.0.1:8000 in a web browser to see the index page.
   Note you can change the IP address and port combination the server runs on by using:
   python manage.py runserver IP:port
