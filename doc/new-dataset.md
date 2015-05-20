#How to Import a New Dataset

1. To begin, go to Django admin, and find _Datasets_ under _Gis_Csdt_. Click _Add Dataset_.
2. Give a name to the dataset. If the data is available via an API, enter the base URL for the API. It's been tested with the SODA API from [OpenNY](data.ny.gov) data sets. It may also work with other APIs.
3. Under the _Field Mapping_ header, map the API's field names to your database's field names. For a description of each field, [see below for field descriptions](#field-descriptions). [See below for information on formatting field mappings](#formatting-field-mappings).
4. Additional fields can be customized for each dataset. These are under the heading _Custom fields_. Give the field name on the remote server in _Field# name_. _Field# en_ is the name for this field in plain English and what will be displayed as the label for this field. The same nesting and concatenation rules apply.
5. Check _Needs geocoding_ if the existing latitude and longitude fields are inaccurate. This will run the address against Google's geocoding service. A limited number of requests can be made per day, so this will be done in nightly batches as described in #6.
6. The data points will be loaded during the daily job. If this has been scheduled, it will occur when scheduled. Otherwise, it can be manually triggered on the server using the command `python manage.py runjobs daily`. This may need to be repeated over several days to geocode a large batch, due to the Google Maps quota.

##Field Descriptions
 - **Column name of the key field on the remote server** If available, enter the name of the field representing a unique ID on the server. This will be used to recache the data.
 - **Name** This field gives the name of the location to be displayed.
 - **Lat, Lon** These fields hold the latidude and longitude locations of the points.
 - **Street, City, State, Zipcode, County** Basic address fields
 
##Formatting Field Mappings
###A basic mapping
For example, if the API has a field called ```zip```, type "zip" in the "zipcode" field.

###Nested fields
For nested fields, use a comma to denote both fields. For example, if the JSON response is formatted as follows:
 ```json
{
  "location": {
    "latitude": 45.0234,
    "longitude": -73.2984
  },
}
```

This would be mapped as follows:
 - **Lat field:** location,latitude
 - **Lon field:** location,longitude
 
###Concatenated fields
To concatenate two fields into one on importing, use a `+` to denote the concatenation. For example, if the JSON response is formatted as follows:
 ```json
{
  "house number": 4,
  "street": "Main St"
}
```

This would be mapped as follows:
 - **Street field:** house number+street
 
###An example using both concatenation and nesting
These can be used together, as in the following example:
 ```json
{
  "address":{
    "house number": 4,
    "street": "Main St"
  }
}
```

This would be mapped as follows:
 - **Street field:** address,house number+street
 
##
 
