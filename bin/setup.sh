config.vm.provision "shell", path: "bin/setup.sh"

sudo apt-get install python-dev build-essential
sudo apt-get install python-pip
sudo pip install virtualenv
sudo apt-get install libcurl4-openssl-dev
sudo apt-get install libpq-dev

. activate

pip install https://github.com/djangonauts/django-rest-framework-gis/tarball/master
sudo apt-get install postgresql-9.3 postgresql-9.3-postgis-2.1 pgadmin3 postgresql-contrib
sudo su - postgres
createdb django_test
exit

wget http://download.osgeo.org/geos/geos-3.4.2.tar.bz2
tar xjf geos-3.4.2.tar.bz2
cd geos-3.4.2
./configure
make
sudo make install
cd ..

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

sudo su - postgres
psql django_test

CREATE USER django_user WITH PASSWORD 'dj4ng0_t3st';
CREATE EXTENSION adminpack;
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
\q

exit
