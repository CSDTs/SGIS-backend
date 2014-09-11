API Output
==========
The API uses Django REST Framework. Responses are returned in the format of the original request, but if you'd like to see a json response from a browser, add the parameter ```format=json```. Results are returned in pages (by default, each page is of size 10). If the request is valid, the json results will contain:
- count: a total count of the matching results
- next: URL to the next page of results
- previous: URL to the previous page of results
- results: an array of the requested JSON objects.

Here are the URLs and details about how to use them:
- [**.../api-ds/** Dataset](usage.md#Datasets)
- [**.../api-mp/** MapPoint](usage.md#MapPoints)
- [**.../api-poly/** MapPolygons](usage.md#MapPolygons)
- [**.../api-tag/** Tag](usage.md#Tags)
- [**.../api-newtag/** New Tags](usage.md#New Tags)

###Datasets
A dataset is a group of MapPoints or MapPolygons. This contains the common information for the set of geometries.
- id: The unique id of this dataset. It can be used to match a dataset with MapPoints or MapPolygons or to filter those elements.
- name: 
- cached: 
- field1_en:  
- field2_en: 
- field3_en: 
- tags:
  - tag: 
  - id: 

###MapPoints

###MapPolygons

###Tags

###New Tags
