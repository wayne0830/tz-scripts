#!/bin/bash
mongodump -h 192.168.130.93 --port 27017 -d usercenter -u tzuser -p asdf -c $1 -o /tmp/
