"""Application Service Layer.

Its job is to handle requests from the outside world and to orchestrate an operation. What we
mean is that the service layer drives the application by following a bunch of simple steps:

* Get some data from the database

* Update the domain model

* Persist any changes

This is the kind of boring work that has to happen for every operation in your system, and keeping it separate from
business logic helps to keep things tidy.
 """
