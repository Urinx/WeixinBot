#!/bin/sh
pip freeze |grep -v wheel | gawk -F"==" ' { print $1 } ' > requirements.txt
