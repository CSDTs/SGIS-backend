gis_csdt
========

The Django side of the GIS Social Justice CSDT for the 3Helix program

# Installation
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
$ sudo apt-get install postgresql-9.3 postgresql-9.3-postgis-2.1 pgadmin3 postgresql-contrib```
$ sudo su - postgres
$ createdb django_test
```


#### GeoDjango
ref: https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/geolibs/

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

#### Scheduled jobs (optional)

(use sudo to add to root, without to add to user's crontab):

```(sudo) crontab -e```

then add the following line:

```0 3 * * * /(path)/manage.py runjobs daily```

(runs daily at 3 AM)

# API Output
###### Datasets:
*fields returned:*

  id : use this to access everything else related to this dataset
  
  name : dataset name 
  
  cached : date last updated
  
  field#_en : names in English of 3 custom fields. If 3 fields do not exist, field1 will be filled first, field2 2nd, etc. Empty fields will be returned as empty quotes. These field names correspond to the "field#" field in the MapPoint API. 

*example:*

.../api-ds/?format=json

```
{
    "count": 2, 
    "next": null, 
    "previous": null, 
    "results": [
        {
            "id": 1, 
            "name": "Farmers Markets", 
            "cached": "2014-07-03T15:27:30.341Z", 
            "field1_en": "Market Link", 
            "field2_en": "EBT/SNAP Status", 
            "field3_en": "Operation Season"
        }, 
        {
            "id": 11, 
            "name": "Retail Food Stores", 
            "cached": "2014-07-03T16:49:12.488Z", 
            "field1_en": "Entity Name", 
            "field2_en": "", 
            "field3_en": ""
        }
    ]
}
```

###### MapPoints:
*fields returned:*
  dataset : api address for this instance
  
  id : unique (across all datasets) database id
  
  name : name to be displayed as the name of the point
  
  lat, lon : as floats (no quotes) 
  
  street, city, state, zipcode, county : address info - state is 2 chars, zip is 5 
  
  field# : data to fill the field named in the dataset

*filters:*
  dataset - by id number or name (starts with)
  
  min_lat, max_lat, min_lon, max_lon, lat, lon - inclusive min/max
  
  exact matches on: street (not super useful), city, state, county, zip, zipcode, zip_code

*example:*

.../api-mp/?format=json&dataset=11

```
{
    "count": 28242, 
    "next": "http://127.0.0.1:8000/api-mp/?page=2&dataset=11", 
    "previous": null, 
    "results": [
        {
            "dataset": "http://127.0.0.1:8000/api-ds/11/", 
            "id": 45560, 
            "name": "RITE AID 10790", 
            "lat": 42.1117709610005, 
            "lon": -76.0588184639997, 
            "street": "511 HOOPER RD", 
            "city": "ENDWELL", 
            "state": "NY", 
            "zipcode": "13760", 
            "county": "Broome", 
            "field1": "ECKERD CORP", 
            "field2": "", 
            "field3": ""
        }, 
        {
            "dataset": "http://127.0.0.1:8000/api-ds/11/", 
            "id": 46474, 
            "name": "SUPER MART 3", 
            "lat": 42.4045721910005, 
            "lon": -73.4265663369997, 
            "street": "12816 RT 22", 
            "city": "CANAAN", 
            "state": "NY", 
            "zipcode": "12029", 
            "county": "Columbia", 
            "field1": "SUPER MART INC", 
            "field2": "", 
            "field3": ""
        }, 
        {
            "dataset": "http://127.0.0.1:8000/api-ds/11/", 
            "id": 45066, 
            "name": "HESS EXPRESS 32234", 
            "lat": 42.6166910150005, 
            "lon": -73.8372388769997, 
            "street": "146 DELAWARE AVE", 
            "city": "ELSMERE", 
            "state": "NY", 
            "zipcode": "12054", 
            "county": "Albany", 
            "field1": "HESS MART INC", 
            "field2": "", 
            "field3": ""
        }, 
...
    ]
}
```
