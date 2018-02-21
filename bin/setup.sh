#!/bin/bash

# Essentials
echo "Getting essentials"
echo
echo
sudo apt-get -y update
sudo apt-get -y install python-dev build-essential

# Pip and Virtualenv
echo "Getting pip, virtualenv, and pip libraries"
echo
echo
sudo apt-get -y install python-pip
sudo pip install --upgrade pip
sudo pip install virtualenv
sudo apt-get -y install libcurl4-openssl-dev
sudo apt-get -y install libpq-dev
pip install https://github.com/djangonauts/django-rest-framework-gis/tarball/master
sudo pip install --upgrade -r /vagrant/requirements.txt

# Install Postgre and PostGIS
echo "Getting PostgreSQL and PostGIS"
echo
echo
sudo apt-get -y install postgresql-9.5 postgresql-9.5-postgis-2.2 pgadmin3 postgresql-contrib
sudo apt-get -y install libxml2-dev
sudo apt-get -y install libgdal1-dev
sudo apt-get -y install postgresql-server-dev-9.5
sudo su - postgres -c "createdb django_test;exit"

# Install GEOS
echo "Installing GEOS"
echo
echo
sudo apt-get -y install build-essential
sudo apt-get -y install gcc build-essential
sudo apt-get -y install g++ build-essential
wget http://download.osgeo.org/geos/geos-3.6.2.tar.bz2
tar xjf geos-3.6.2.tar.bz2
cd geos-3.6.2
./configure
make
sudo make install
cd ..

# Install PROJ.4
echo "Installing PROJ.4"
echo
echo
wget http://download.osgeo.org/proj/proj-4.9.3.tar.gz
wget http://download.osgeo.org/proj/proj-datumgrid-1.5.tar.gz
tar xzf proj-4.9.3.tar.gz
cd proj-4.9.3/nad
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
sudo -u postgres psql django_test -c "CREATE USER django_user WITH PASSWORD 'dj4ng0_t3st';CREATE EXTENSION adminpack; CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"
echo "All done"

