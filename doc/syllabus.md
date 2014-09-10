Social Data Analysis in GIS
===========================
##Independent Study Outline - Fall 2014
###Goal
The goal of this independent study course is to build a RESTful API behind a GIS application that will allow high school students to examine existing, publicly available datasets on a variety of subjects like food availability, income, race, obesity, pollution, etc. They will also be able to create their own datasets by marking locations in their own neighborhood overlayed on the same map. Completion of this program will require collaboration with other students who are working on the main site that will house this application and the frontend that will utilize this backend. 
###Users
High school and undergraduate students will be using this online application to explore social data in their neighborhood to other nearby neighborhoods. Teachers and professors will be using the tool to manage tags and student data.
###Technology Used
The product is an app for a *Django* website (written in *Python*) using a *PostgreSQL* with *PostGIS* database. The app takes advantage of other available Django apps, specifically *djangorestframework* (http://github.com/tomchristie/django-rest-framework) and *djangorestframework-gis* (http://github.com/djangonauts/django-rest-framework-gis).
###Semester Deliverables
* GIS backend capable of:
  * Automatic caching of existing points and polygons from remote APIs or local files
  * API allowing filtering of geometries based on bounding box, location (zip, county, etc), tags
  * API returning data in GeoJSON
  * Allow POSTing of new data with appropriate authorization only
  * Management of  classrooms by teachers, including approving student tags and geometries
  * Complete documentation of semester’s work
* Integration with community site
* Code and documentation available at: http://github.com/kathleentully/gis_csdt

###Accomplishment Timetable
Date | Accomplishment
----:|:--------------
Sept&nbsp;15 | Allow filtering of data points by tags,<br />Ordering results to fill center of map first,<br />Add support for POSTing new data points from front end application or other unspecified sources (like sensors),<br />Bring documentation up to date
Oct&nbsp;6 | Go live! - initial installation into community site,<br />resolving conflicts and bugs,<br />Invalid requests return appropriate HTTP responses
Oct&nbsp;27 | Add support for authentication,<br />Implement user specific data (points and tags)
Nov&nbsp;17 | Create admin approval interface for tags,<br />Plan to integrate with classroom scenario
Dec&nbsp;5 | Implement classroom groups using community site setup,<br />Finalize documentation from throughout semester