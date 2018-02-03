#!/bin/bash

# Essentials
echo "Getting essentials"
echo
echo
sudo apt-get install python-dev build-essential

# Pip and Virtualenv
echo "Getting pip, virtualenv, and pip libraries"
echo
echo
sudo apt-get install python-pip
sudo pip install virtualenv
sudo apt-get install libcurl4-openssl-dev
sudo apt-get install libpq-dev
. activate
pip install https://github.com/djangonauts/django-rest-framework-gis/tarball/master

# Install Postgre and PostGIS
echo "Getting PostgreSQL and PostGIS"
echo
echo
# sudo apt-get install postgresql-9.3 postgresql-9.3-postgis-2.1 pgadmin3 postgresql-contrib
# WEIRD ERROR OCCURING BUT POSTGRE IS ALREADY INSTALLED
sudo su - postgres -c createdb django_test exit

# Install GEOS
echo "Installing GEOS"
echo
echo
wget http://download.osgeo.org/geos/geos-3.4.2.tar.bz2
tar xjf geos-3.4.2.tar.bz2
cd geos-3.4.2
./configure
make
sudo make install
cd ..

# Install PROJ.4
echo "Installing PROJ.4"
echo
echo
wget http://download.osgeo.org/proj/proj-4.8.0.tar.gz
wget http://download.osgeo.org/proj/proj-datumgrid-1.5.tar.gz
tar xzf proj-4.8.0.tar.gz
cd proj-4.8.0/nad
tar xzf ../../proj-datumgrid-1.5.tar.gz
cd ..
./configure
make
sudo make install
cd ..

# Set up PostGIS
echo "Setting up PostGIS"
echo
echo
sudo su - postgres -c psql django_test < psqlCommands.sql

echo "All done"

