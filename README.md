solarpermit-1.3.50
===============

Web Based Tool for Tracking Solar Permitting Requirements in The United States

Please see the wiki for additional documentaiton - [https://github.com/solarpermit/solarpermit/wiki](https://github.com/solarpermit/solarpermit/wiki)

Getting Involved
================

[WIP]

[intro comment]

1. Data
  1. Web User Interface
  2. API
  3. Raw Data Dumps
2. Source Code
  1. Forks and Merge Requests
3. Sharing Ideas and Feature Requests
  1. Forums for Ideas
  2. Github for feature requests

Initial Source Release
================
We will be merging the previous development trunk here.  If you would like to participate in development, please join us on github or start a conversation in our forums.


Install Instructions
================

1.  Install Dependencies
  1. Apache 2
  2. MySQL Server, version 5.5 or newer
    1. Install the mysql_json UDF
    1. git submodule update --init    (checks out the source code)
    2. cd deps/mysql_json
    3. make
    4. make install
  3. mod_wsgi
  4. Please See dependencies.txt
    1.  This file is written to be used with pip for easily handling python requirements - i.e. "pip install -r dependencies.txt"
  5. Optional Items
    1.  Closure JS compiler, for JS minification
2.  Setup Apache to allow vhosts
3.  Setup the specific vhost
  1.  See apache/solarpermit_apache_inc.conf
  2.  Replace "mydomain.com" with the domain that you want to use
  3.  Lines 9, 35, 36
  4.  Replace "/path/to/software" with the folder that contains this file
  5.  Lines 37, 39, 44, 45, 46, 51, 52
  6.  Replace "/path/to/this/vhost/logs" with the location of the folder you want to use for vhost specific logs.
    1.  make sure the user specified in the apache include has write privileges for this folder, and the log files.
    2.  I use "/path/to/software/logs" so that all my vhosts are separated
  7.  Move apache/solarpermit_apache_inc.conf to your apache Includes folder
4. Configure Software
  1. edit apache/django.wsgi
    1.  replace "/path/to/software" on line 3.
  2. Change settings... do not edit settings.py, use settings_local.py to override
5. Configure Database
  1. CREATE DATABASE solarpermit CHARACTER SET utf8mb4 COLLATE utf8_unicode_ci;
  2. ./manage.py syncdb (if this fails due to a missing SQL table, run migrate website)
  3. Optionally import an SQL dump
  4. ./manage.py migrate website
  5. ./manage.py migrate tracking
  6. ./manage.py migrate compress_jinja
6. Restart Apache
7. Set up Cron jobs
  1. periodically run ./manage.py validate_answers -- this can be done every hour.
  2. there are other cron jobs, but omitting them will not prevent deployment.
      
Need help?  Have questions?

Forum: http://solarpermit.org/forum/

IRC: #solarpermit on freenode
