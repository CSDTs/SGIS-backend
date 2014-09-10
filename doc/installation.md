Installation
============
(on Ubuntu)
First you need pip and virtualenv:

```
$ sudo apt-get install python-pip python-dev build-essential
$ sudo pip install virtualenv
```
#### Install pip libraries (including django)
Needed for pycurl:

```$ sudo apt-get install libcurl4-openssl-dev```

Needed for psycog2:

```$ sudo apt-get install libpq-dev```

Everything else:

```$ . activate```

#### PostgreSQL and PostGIS
Install all postgres things needed:

```
$ sudo apt-get install postgresql-9.3 postgresql-9.3-postgis-2.1 pgadmin3 postgresql-contrib
$ sudo su - postgres
$ createdb django_test
$ exit
```


GeoDjango (ref: https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/geolibs/)

Install GEOS

```
$ wget http://download.osgeo.org/geos/geos-3.4.2.tar.bz2
$ tar xjf geos-3.4.2.tar.bz2
$ cd geos-3.4.2
$ ./configure
$ make
$ sudo make install
$ cd ..
```

Install PROJ.4

```
$ wget http://download.osgeo.org/proj/proj-4.8.0.tar.gz
$ wget http://download.osgeo.org/proj/proj-datumgrid-1.5.tar.gz
$ tar xzf proj-4.8.0.tar.gz
$ cd proj-4.8.0/nad
$ tar xzf ../../proj-datumgrid-1.5.tar.gz
$ cd ..
$ ./configure
$ make
$ sudo make install
$ cd ..
```

Set up PostGIS

```
$ sudo su - postgres
$ psql django_test
```

```
> CREATE USER django_user WITH PASSWORD 'dj4ng0_t3st';
> CREATE EXTENSION adminpack;
> CREATE EXTENSION postgis;
> CREATE EXTENSION postgis_topology;
> \q
```

```
$ exit
```

#### Scheduled jobs (optional)

(use sudo to add to root, without to add to user's crontab):

```(sudo) crontab -e```

then select an editor and add the following line:

```0 3 * * * /(path)/manage.py runjobs daily```

(runs daily at 3 AM)