#!/bin/sh

cd /root/iot_vol/scripts
service mysql start
mysql < init_mysql.sql
./docker_app.py
