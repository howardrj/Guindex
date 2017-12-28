#!/bin/bash

timestamp="$(date +%s)"
sqlite3 /usr/share/Guindex.db ".backup '/usr/share/Guindex-${timestamp}.db'"
