Social Data Analysis in GIS
===========================
#Independent Study Outline - Fall 2014
##Goal
The goal of this independent study course is to build a RESTful API behind a GIS application that will allow high school students to examine existing, publicly available datasets on a variety of subjects like food availability, income, race, obesity, pollution, etc. They will also be able to create their own datasets by marking locations in their own neighborhood overlayed on the same map. Completion of this program will require collaboration with other students who are working on the main site that will house this application and the frontend that will utilize this backend. 
##Users
High school and undergraduate students will be using this online application to explore social data in their neighborhood to other nearby neighborhoods. Teachers and professors will be using the tool to manage tags and student data.
##Technology Used
The product is an app for a *Django* website (written in *Python*) using a *PostgreSQL* with *PostGIS* database. The app takes advantage of other available Django apps, specifically *djangorestframework* (github.com/tomchristie/django-rest-framework) and *djangorestframework-gis* (github.com/djangonauts/django-rest-framework-gis).
##Semester Deliverables
* GIS backend capable of:
  * Automatic caching of existing points and polygons from remote APIs or local files
  * API allowing filtering of geometries based on bounding box, location (zip, county, etc), tags
  * API returning data in GeoJSON
  * Allow POSTing of new data with appropriate authorization only
  * Management of  classrooms by teachers, including approving student tags and geometries
  * Complete documentation of semester’s work
* Integration with community site
* Code and documentation available at: github.com/kathleentully/gis_csdt
##Accomplishment Timetable
Date | Accomplishment
----:|:--------------
Sept 15 | Allow filtering of data points by tags, Ordering results to fill center of map first, Add support for POSTing new data points from front end application or other unspecified sources (like sensors), Bring documentation up to date
Oct 6 | Go live! - initial installation into community site, resolving conflicts and bugs, Invalid requests return appropriate HTTP responses
Oct 27 | Add support for authentication, Implement user specific data (points and tags)
Nov 17 | Create admin approval interface for tags, Plan to integrate with classroom scenario
Dec 5 | Implement classroom groups using community site setup, Finalize documentation from throughout semester

