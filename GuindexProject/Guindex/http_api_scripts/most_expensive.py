# -*- coding: utf-8 -*-
import pycurl
import json
from StringIO import StringIO

GUINDEX_URL = 'http://guindex.ie'

def main():

    # Create buffer to write returned content into
    buffer = StringIO() 

    # Create pyCurl object
    c = pycurl.Curl()

    # Set target URL
    c.setopt(c.URL, '%s/guinness/' % GUINDEX_URL)

    # Follow redirects (i.e http -> https)
    c.setopt(pycurl.FOLLOWLOCATION, 1)

    # Write returned data to our buffer
    c.setopt(c.WRITEDATA, buffer)

    # Perform HTTP GET request
    c.perform()

    # Parse JSON list of Guinness objects into python object
    guinness_json = json.loads(buffer.getvalue())

    # Loop through Guinness objects and store dearest
    dearest_guinness = None
    for loop_index, guinness in enumerate(guinness_json):

        # If first guinness
        if loop_index == 0:
            dearest_guinness = guinness
        elif float(guinness['price']) > float(dearest_guinness['price']):
            dearest_guinness = guinness

    # Get pub id from dearest Guinness object
    pub_id = dearest_guinness['pub']

    # Set new target URL
    c.setopt(c.URL, '%s/pubs/%d/' % (GUINDEX_URL, pub_id))

    # Reset buffer
    buffer = StringIO() 
    c.setopt(c.WRITEDATA, buffer)

    # Perform request
    c.perform()

    # Parse json response
    pub_json = json.loads(buffer.getvalue())

    print(u"Most expensive pub is %s - €%s" % (pub_json['name'], dearest_guinness['price']))

    # Close pyCurl object 
    c.close()

if __name__ == '__main__':
    main()
