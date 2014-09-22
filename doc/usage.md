API Output
==========
The API uses Django REST Framework. Responses are returned in the format of the original request, but if you'd like to see a json response from a browser, add the parameter ```format=json```. Results are returned in pages (by default, each page is of size 10). If the request is valid, the json results will contain:
- count: a total count of the matching results
- next: URL to the next page of results
- previous: URL to the previous page of results
- results: an array of the requested JSON objects.

Here are the URLs and details about how to use them:
- **.../api-ds/** [Datasets](usage.md#datasets)
- **.../api-mp/** [MapPoints](usage.md#mappoints)
- **.../api-poly/** [MapPolygons](usage.md#mappolygons)
- **.../api-tag/** [Tag](usage.md#tags)
- **.../api-newtag/** [New Tags](usage.md#new-tags)

###Datasets
A Dataset is a group of MapPoints or MapPolygons. This contains the common information for the set of geometries.

A response includes the following elements:
- ```id``` is the unique id of this Dataset. It can be used to match a dataset with MapPoints or MapPolygons or to filter those elements.
- ```name``` is the name of the set of points. 
- ```cached``` is the date the Dataset was last updated (excluding updates to Dataset information or tags alone).
- ```field1_en```, ```field2_en```, ```field3_en``` are the English names of the data included in each MapPoint or MapPolygon as ```field1```, ```field2```, ```field3```. This is the name you should use for display.
- ```tags``` is an array of JSON objects of all approved tags that appear on any MapPoint or MapPolygon in this Dataset. The array contains:
  - ```tag``` is the text of the tag.
  - ```id``` is the id of the tag.

###MapPoints
A MapPoint is an individual location on the map.

A response includes the following elements:
- ```dataset``` is a link to the information about the dataset to which this MapPoint belongs
- ```id``` is a unique system id for this MapPoint
- ```name``` is the name of the MapPoint 
- ```latitude```, ```longitude``` are the latitude and longitude location of the MapPoint 
- ```street```, ```city```, ```state```, ```zipcode```, ```county``` are elements of the street address of the MapPoint 
- ```field1```, ```field2```, ```field3``` are the data matching the field description in the corresponding Dataset
- ```tags``` is an array of JSON objects of all approved tags for this MapPoint. The array contains:
  - ```tag``` is the text of the tag.
  - ```id``` is the id of the tag.

MapPoints can be filtered using the following parameters:
- ```tag```, ```tags``` These can be used interchangably. Accepts a tag, a tag id number, a list of tags or a list of tag ids. By default, MapPoints that match *any* of the tags will be included in the results (OR Boolean result).
- ```match``` If this parameter is ```all```, only MapPoints matching *all* of the tags will be included (AND Boolean result)
- ```dataset``` Using the Dataset id, return only those MapPoints matching a specific Dataset.
- ```max_lat```, ```min_lat```, ```max_lon```,```min_lon``` Create a bounding box and return only MapPoints within that box.
- ```city```, ```state```, ```county``` Match any of these exactly using string matching on these fields.
- ```zipcode```, ```zip```, ```zip_code``` Match the ```zip_code``` exactly. Only the first five characters will be matched.

###MapPolygons
A MapPolygon is a polygon on a map. The response is in GeoJSON format. For more information, see the [GeoJSON spec](http://geojson.org/geojson-spec.html).
- ```type``` should always be ```Feature```
- ```geometry``` is an object with the geometric details in it.
  - ```type``` should always be ```MultiPolygon``` when requesting a MapPolygon
  - ```coordinates``` is an array of polygon coordinate arrays.
- ```properties``` In GeoJSON format, addition information is contained inside the ```properties``` element.
  - ```id``` is a unique system id for this MapPolygon.
  - ```dataset``` The id of the Dataset to which this MapPolygon belongs. Note: this is different that the same field for MapPoints.
  - ```remote_id``` is the id of the MapPolygon used by the original source of the data. This can be used to match MapPolygons with outside data sources.
  - ```name``` is the English name of this MapPolygon.
  - ```latitude```, ```longitude``` are the latitude and longitude location of the rough center of the MapPolygon
  - ```field1```, ```field2``` are the data matching the field description in the corresponding Dataset
  - ```tags```An array of JSON objects of all approved tags for this MapPoint. The array contains:
    - ```tag``` The text of the tag.
    - ```id``` The id of the tag.

MapPolygons can be filtered using similar parameters to MapPoints:
- ```tag```, ```tags``` These can be used interchangably. Accepts a tag, a tag id number, a list of tags or a list of tag ids. By default, MapPolygons that match *any* of the tags will be included in the results (OR Boolean result).
- ```match``` If this parameter is ```all```, only MapPolygons matching *all* of the tags will be included (AND Boolean result)
- ```dataset``` Using the Dataset id, return only those MapPolygons matching a specific Dataset.
- ```max_lat```, ```min_lat```, ```max_lon```,```min_lon``` Create a bounding box and return only MapPolygons at leasst partially within that box.

###Tags
GET and POST are allowed for this URL, but GET is only intended to be used for debugging purposes. This URL is for linking an existing tag with an existing approved MapPoint *or* MapPolygon. A POST request with a defined MapPoint and a defined MapPolygon will fail. A POST request with neither will also fail.

Currently, no authentication is required to POST.

A POST request should include:
- ```mappoint``` **OR** ```mappolygon``` by id number
- ```tag``` by id number


###New Tags
GET and POST are allowed for this URL, but GET is only intended to be used for debugging purposes. This URL is for linking an existing tag *or a new tag* with an existing approved MapPoint *or* MapPolygon. A POST request with a defined MapPoint and a defined MapPolygon will fail. A POST request with neither will also fail.

Currently, no authentication is required to POST. Eventually, a logged in user will be required to POST. A new tag will not be approved until done manually.

A POST request should include:
- ```mappoint``` **OR** ```mappolygon``` by id number
- ```tag``` by tag text
