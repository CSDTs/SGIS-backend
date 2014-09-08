API Output
==========
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
