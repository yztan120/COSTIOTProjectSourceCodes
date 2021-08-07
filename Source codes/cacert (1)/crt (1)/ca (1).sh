#!/bin/bash

rm *.crt && rm *.csr && rm *.srl && rm *.key
./docker_generate-CA.sh
