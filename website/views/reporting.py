#
# code is function but needs enhancement to conform to DRY methodology
#

# django components
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import Context
from website.utils.httpUtil import HttpRequestProcessor
from django.conf import settings as django_settings
from django.template.loader import get_template
from django.template import Context, RequestContext, Template
from django.conf import settings
from jinja2 import FileSystemLoader, Environment
import hashlib

# specific to api
import MySQLdb # database
import MySQLdb.cursors

valid_questions = [8,9,10,14,15,16,52,53,54,55,56,61,69,71,76,84,91,96,97,105,106,107,111,282,283]
## add additionals seperately to not mix op required and optional
optional_questions = [19,20,21,23,24,26,28,29,31,32,37,38,39,45,46,47,59,60,63,65,66,67,68,72,73,75,77,78,79,80,83,86,88,109,277]
#optioanl_questions = list(optional_questions + [])
valid_questions = list(set(valid_questions + optional_questions))


# define table headers, fields, and queries
reports = {
                14 : { # (comment here, on subsequent definitions, indicates all similar cases are covered
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '14' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%available"%"yes%') as `Yes`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '14' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%available"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '14' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as `Total` FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes','No','Total'],
                },
                15 : { #
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%value"%"yes%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%value"%"no%' ) as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                52 : {
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '52' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '52' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '52' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '52' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                ### similar questions to 52 that were not declared mandatory
                19 : {
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '19' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '19' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '19' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '19' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                20 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '20' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '20' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '20' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '20' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                21 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '21' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '21' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '21' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '21' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                23 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '23' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '23' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '23' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '23' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                24 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '24' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '24' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '24' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '24' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                26 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '26' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '26' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '26' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '26' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                28 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '28' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '28' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '28' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '28' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                29 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '29' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '29' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '29' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '29' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                31 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '31' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '31' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '31' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '31' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                32 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '32' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '32' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '32' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '32' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                37 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '37' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '37' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '37' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '37' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                38 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '38' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '38' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '38' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '38' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                39 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '39' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '39' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '39' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '39' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                45 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '45' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '45' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '45' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '45' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                46 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '46' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '46' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '46' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '46' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                47 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '47' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '47' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '47' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '47' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                59 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '59' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '59' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '59' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '59' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                60 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '60' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '60' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '60' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '60' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                63 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '63' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '63' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '63' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '63' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                65 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '65' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '65' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '65' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '65' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                66 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '66' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '66' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '66' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '66' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                67 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '67' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '67' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '67' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '67' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                68 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '68' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '68' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '68' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '68' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                72 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '72' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '72' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '72' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '72' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                73 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '73' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '73' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '73' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '73' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                75 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '75' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '75' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '75' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '75' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                77 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '77' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '77' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '77' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '77' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                78 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '78' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '78' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '78' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '78' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                79 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '79' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '79' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '79' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '79' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                80 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '80' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '80' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '80' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '80' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                83 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '83' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '83' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '83' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '83' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                86 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '86' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '86' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '86' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '86' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                88 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '88' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '88' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '88' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '88' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                109 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '109' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '109' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '109' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '109' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                277 :{
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '277' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '277' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '277' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as `No`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '277' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                ### EO similar questions to 52 that were not declared mandatory 
                53 : {
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '53' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '53' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '53' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '53' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'Yes, with exceptions', 'No', 'Total'],
                },
                55 : {
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '55' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '55' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '55' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '55' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'Yes, with exceptions', 'No', 'Total'],
                },
                56 : {
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '56' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '56' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '56' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%' ) as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '56' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'Yes, with exceptions', 'No', 'Total'],
                },
                69 : {
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '69' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%enforced"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '69' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '69' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%enforced"%"no%'  AND value NOT LIKE '%enforced"%"yes%') as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '69' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'Yes, with exceptions', 'No', 'Total'],
                },
                91 : {
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '91' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '91' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '91' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%'  AND value NOT LIKE '%required"%"yes%') as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '91' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'Yes, with exceptions', 'No', 'Total'],
                },
                76 : {
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '76' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%required"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '76' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '76' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%required"%"no%'  AND value NOT LIKE '%required"%"yes%') as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '76' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'Yes, with exceptions', 'No', 'Total'],
                    },
                84 : { #
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '84' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%available"%"yes%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '84' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%available"%"no%' ) as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '84' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                96 : {
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '96' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%available"%"yes%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '96' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%available"%"no%' ) as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '96' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                97 : {
                      'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '97' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%plan_check_service_type"%"over the counter%') as `Over the Counter`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '97' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%plan_check_service_type"%"in-house%' ) as `In-House (not same day)`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '97' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%plan_check_service_type"%"outsourced%' ) as Outsourced, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '97' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                      'keys_in_order' : ['Over the Counter', 'In-House (not same day)', 'Outsourced', 'Total'],
                },
                105 : {
                       'query' : '''SELECT (SELECT count(*) FROM `website_answerreference` WHERE question_id ='105'  AND jurisdiction_id NOT IN ('1','101105') AND (value LIKE '%value"%"Yes%' OR value LIKE '%value"%"http%')) as Yes, (SELECT count(*) FROM `website_answerreference` WHERE question_id ='105'  AND jurisdiction_id NOT IN ('1','101105') AND value NOT LIKE '%value"%"Yes%' AND value NOT LIKE '%value"%"http%') as No, (SELECT count(*) FROM `website_answerreference` WHERE question_id ='105'  AND jurisdiction_id NOT IN ('1','101105')) as Total FROM website_answerreference LIMIT 1''',
                       'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                111 : {
                       'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '111' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%value"%"yes%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '111' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%value"%"no%' ) as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '111' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                       'keys_in_order' : ['Yes', 'No', 'Total'],
                },
                283 : {
                       'query' : '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '283' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%compliant"%"yes%' AND value NOT LIKE '%yes, with exceptions%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '283' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%yes, with exceptions%') as `Yes, with exceptions`, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '283' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%compliant"%"no%'  AND value NOT LIKE '%compliant"%"yes%') as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '283' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
                       'keys_in_order' : ['Yes', 'Yes, with exceptions', 'No', 'Total'],
                },
           }

##############################################################################
#
# Display Index of Reports
#
##############################################################################
def report_index(request):
    # get question data
    from website.models import Question, QuestionCategory
    # get category data
    
    
    data = {}
    data['current_nav'] = 'reporting'
    
    conn = MySQLdb.connect (host=settings.DATABASES['default']['HOST'],
                           user=settings.DATABASES['default']['USER'],
                           passwd=settings.DATABASES['default']['PASSWORD'],
                           db=settings.DATABASES['default']['NAME'],
                           cursorclass=MySQLdb.cursors.DictCursor)
    cursor = conn.cursor()

    query = "SELECT website_question.id as id, website_question.display_order as display_order, website_question.label as label, website_question.category_id as category_id, website_questioncategory.name as category FROM website_question, website_questioncategory WHERE website_question.id IN ("
    #8,9,10,14,15,16,52,53,54,55,56,61,69,71,91,76,84,96,97,105,106,107,111,282,283
    first_run = True
    for id in valid_questions:
        if first_run:
            first_run = False
        else:
            query += ','
        query += "'" + str(id) + "'"
    query += ") AND website_question.accepted = '1' AND website_question.form_type NOT LIKE 'CF' AND website_questioncategory.id = website_question.category_id ORDER BY website_question.category_id ASC, display_order ASC"
    #data['query'] = query

    cursor.execute(query)
    rows = cursor.fetchall()
    
    reports_index = []
    category_last_encountered = ''
    first_run = True
    for row in rows:
        if row['category'] != category_last_encountered:
            category_last_encountered = row['category']
            # the category level does not exist create it.
            reports_index.append({})
            reports_index[-1]['category'] = row['category'].replace('_',' ').title()
            reports_index[-1]['reports_in_category'] = []
        # append this report's data to the list - with a link if it exists
        reports_index[-1]['reports_in_category'].append(row)
        if row['id'] in reports:
            reports_index[-1]['reports_in_category'][-1]['link_to'] = True
        else:
            reports_index[-1]['reports_in_category'][-1]['link_to'] = False

    data['reports_index'] = reports_index
             

            
           
    
    #finish up
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/reports/report_index.html', data, '')
    
    
    
    
##############################################################################
#
# Display an individual report on a question_id
#
##############################################################################
def report_on(request,question_id):
    # Check request for validity
    question_id = int(question_id)
    if question_id not in reports:
            raise Http404
    
    # get question data
    from website.models.questionAnswer import Question
    
    data = {}
    data['current_nav'] = 'reporting'
    
    
    
    #data['query'] = table_data[question_id]['query']
    
    conn = MySQLdb.connect (host=settings.DATABASES['default']['HOST'],
                           user=settings.DATABASES['default']['USER'],
                           passwd=settings.DATABASES['default']['PASSWORD'],
                           db=settings.DATABASES['default']['NAME'],
                           cursorclass=MySQLdb.cursors.DictCursor)
    cursor = conn.cursor()
    
    cursor.execute(reports[question_id]['query'])
    row = cursor.fetchone()
    
    table_values = []
    for key in reports[question_id]['keys_in_order']:
        table_values.append({'key':key,'value':row[key]})
        
    data['table'] = table_values
    
    question = Question.objects.get(id=question_id)
    
    data['report_name'] = question.question
    data['question_instruction'] = question.instruction
    
    
    #finish up
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/reports/report_on.html', data, '')
