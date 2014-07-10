solarpermit-1.3.50
===============

Web Based Tool for Tracking Solar Permitting Requirements in The United States

Please see the wiki for additional documentaiton - [https://github.com/solarpermit/solarpermit/wiki](https://github.com/solarpermit/solarpermit/wiki)

Initial Source Release
================
We will be merging the previous development trunk here.  If you would like to participate in development, please join us on github or start a conversation in our forums.


Install Instructions
================

1.  Install Dependencies
    A. Apache 2
    B. MySQL Server, version 5.5 or newer
        a. Install the mysql_json UDF
            1. git submodule update --init    (checks out the source code)
            2. cd deps/mysql_json
            3. make
            4. make install
    C. mod_wsgi
    D. Please See dependencies.txt
        a.  This file is written to be used with pip for easily handling python requirements - i.e. "pip install -r dependencies.txt"
    E. Optional Items
        a.  Closure JS compiler, for JS minification
2.  Setup Apache to allow vhosts
3.  Setup the specific vhost
    A.  See apache/solarpermit_apache_inc.conf
    B.  Replace "mydomain.com" with the domain that you want to use
        a.  Lines 9, 35, 36
    C.  Replace "/path/to/software" with the folder that contains this file
        a.  Lines 37, 39, 44, 45, 46, 51, 52
    D.  Replace "/path/to/this/vhost/logs" with the location of the folder you
        want to use for vhost specific logs.
        a.  make sure the user specified in the apache include has write
            privileges for this folder, and the log files.
        b.  I use "/path/to/software/logs" so that all my vhosts are separated
    E.  Move apache/solarpermit_apache_inc.conf to your apache Includes folder
4. Configure Software
    A. edit apache/django.wsgi
        a.  replace "/path/to/software" on line 3.
    B. Change settings... do not edit settings.py, use settings_local.py to
       override
5. Configure Database
    A. CREATE DATABASE solarpermit CHARACTER SET utf8mb4 COLLATE utf8_unicode_ci;
    B. ./manage.py syncdb (if this fails due to a missing SQL table, run migrate website)
    C. Optionally import an SQL dump
    D. ./manage.py migrate website
    E. ./manage.py migrate tracking
    F. ./manage.py migrate compress_jinja
6. Restart Apache
7. Set up Cron jobs
    A. periodically run ./manage.py validate_answers -- this can be done every hour.
    B. there are other cron jobs, but omitting them will not prevent deployment.
      
Need help?  Have questions?

Forum: http://solarpermit.org/forum/

IRC: #solarpermit on freenode
