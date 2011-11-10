Change Log
===========

0.2.5 released ???
-------------------------

 - ???

0.2.4 released 2011-11-09
-------------------------
 - **BC BREAK**: changing LookupMixin.test_create() to .testing_create()
 - convert sql processing to use generators
 - add lib/helpers.py:clear_db_data(), only postgres supported currently

0.2.3 released 2011-07-16
-----------------------------
 - Facilitate use by non-default SA engine.  Enables a project to have two
    DB connections and hence two SA sessions, and still be able to use this lib.

0.2.2 released 2011-05-19
-----------------------------
 - same as 0.2.1 (accidental release bump)

0.2.1 released 2011-05-19
-----------------------------
 - remove explicit SQLAlchemy version since savalidation will install it
