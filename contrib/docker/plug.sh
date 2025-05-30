#!/bin/bash
pip install -e git+https://github.com/SALTED-Project/ckanext-dcat-ap-edp-mqa.git#egg=ckanext-dcat-ap-edp-mqa
ls 
pip install -r src/ckanext-dcat-ap-edp-mqa/requirements.txt
pip install ckanext-dcat
pip install anaconda  # or something similar (see below).
pip install rdflib
pip install geomet
ckan db upgrade
