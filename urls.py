from django.http import HttpResponseRedirect
from django.conf.urls.defaults import patterns, include, handler404, handler500, url
from django.conf import settings
from website.views import home, test_view, account, unittest, info, jurisdiction, organization, custom_field, maintenance, siteadmin
from website.views.news import *

from django.contrib import admin
admin.autodiscover()
handler404 = 'website.views.info.page_404'

#for maintenance mode
if settings.MAINTENANCE_MODE == True:
    urlpatterns = patterns('',
        url( # TODO: replace with django.conf.urls.static ?
            r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT.replace('\\','/')},
        ),  
        (r'^.*/$', maintenance.maintenace_mode), #catch all
    )
else:
    urlpatterns = patterns('',
        # Examples:
        # url(r'^$', 'solarpermit.views.home', name='home'),
        # url(r'^solarpermit/', include('solarpermit.foo.urls')),
    
        # Uncomment the admin/doc line below to enable admin documentation:
        # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
        # Uncomment the next line to enable the admin:
        # url(r'^admin/', include(admin.site.urls)),
        
        (r'^$', home.home),     
        (r'^admin/', include(admin.site.urls)), 
        #(r'^jurisdiction_browse/(?P<state>.*)/(?P<sort_by>.*)/(?P<sort_dir>.*)/(?P<page_num>.*)/$', jurisdiction.get_state_jurisdictions),     
        #(r'^browse/', 'website.views.jurisdiction.jurisdiction_browse_by_states'),  
        (r'^jurisdiction/browse/$', 'website.views.jurisdiction.jurisdiction_browse_improved'),
        (r'^jurisdiction_comment/$', 'website.views.AHJ.jurisdiction_comment'),
        (r'^jurisdiction/search/$', 'website.views.jurisdiction.jurisdiction_search_improved'),
        (r'^jurisdiction/autocomplete/$', 'website.views.jurisdiction.jurisdiction_autocomplete'),
        (r'^jurisdiction/answer_uploadfile/$', 'website.views.AHJ.answer_uploadfile'),  
        (r'^jurisdiction/migration/result/(?P<id>.*)/$', 'website.views.data_migration.jurisdiction_migration_result'),
    
        #(r'^jurisdiction/(?P<id>.*)/(?P<category>.*)/$', 'website.views.AHJ.view_AHJ'),    
        #(r'^jurisdiction/(?P<id>.*)/$', 'website.views.AHJ.view_AHJ'),
        (r'^jurisdiction/(?P<name>.*)/(?P<category>.*)/$', 'website.views.AHJ.view_AHJ_by_name'),    
        (r'^jurisdiction/(?P<name>.*)/$', 'website.views.AHJ.view_AHJ_by_name'),          
        #(r'^jurisdiction_id/(?P<id>.*)/(?P<category>.*)/$', 'website.views.AHJ.view_AHJ'), 
        #(r'^jurisdiction_id/(?P<id>.*)/$', 'website.views.AHJ.view_AHJ'), 
              
        #(r'^set_up_data_sprint_19', 'website.views.data_migration.set_up_data_sprint_19'),
                
        #(r'^test_newsite/', test_view.test_newsite),
        #(r'^test_add/', test_view.test_add),
        #(r'^test_edit/', test_view.test_edit),    
        #(r'^test_ie/', test_view.test_ie),    
            
        url( # TODO: replace with django.conf.urls.static ?
            r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT.replace('\\','/')},
        ),  
        (r'^account/', account.account), 
        (r'^change_password/', account.change_password),         
        (r'^organization/logo/org_uploadfile/$', 'website.views.organization.org_uploadfile'),           
        (r'^organization/search/', 'website.views.organization.organization_search'),             
        (r'^organization/user/search/', 'website.views.organization.organization_user_search'),
        (r'^organization/members/', 'website.views.organization.organization_members'),
        (r'^organization/', 'website.views.organization.organization'),             
        (r'^whitepapers/', 'website.views.whitepaper.papers'),   
        (r'^logout', account.log_out),      
        (r'^reset_password/(?P<reset_password_key>.*)/$', home.reset_password),       
        (r'^info/', info.get_info),  
        (r'^news/', info.news_static),
        (r'^news2/', info.news_dynamic),
        (r'^about/', info.about),
        (r'^getting-started/', info.getting_started_page),  
        
        #data migrations
        #(r'^util/import/unincorporated/$', 'website.views.data_migration.migrate_unincorporated'),
        (r'^util/import/jurisdictions/$', 'website.views.data_migration.migrate_jurisdiction_data'),
        #(r'^util/import/users/', 'website.views.data_migration.migrate_users'),       
        #(r'^correct_fee/', 'website.views.data_migration.correct_fee'),         
        
        #services
        (r'^s/search/general/$', 'website.services.jurisdiction_services.search_general'),
        url(r'^runCron/(?P<forceRun>.*)/$', 'website.cron.cron.run_cron'),
        #unit tests and other tests
        #(r'^test/search/$', test_view.test_search),  
        #(r'^test/org/$', test_view.test_org),  
        #(r'^test/timezone/$', test_view.test_timezone),  
        #(r'^test/ahj/(?P<id>.*)/$', jurisdiction.view_AHJ),      
        #(r'^unittest/(?P<test>.*)/$', unittest.run_test),  
        #(r'^unittest/$', unittest.run_test),  
        (r'^test/cron_validate_answers/', test_view.test_cron_validate_answers),    
                
        (r'^sign_in', account.sign_in_shell),     
    
        (r'^profile/(?P<id>.*)/$', account.user_profile),
        (r'^profile/$', account.user_profile_full), 
        (r'^user_favorite/$', 'website.views.account.user_favorite'),  
        (r'^recent_updates/search/$', 'website.views.account.updates_search'),   
        
        (r'^custom_field/', custom_field.custom_field),
        
        (r'^sitemap/states/$', 'website.views.info.states'),
        (r'^sitemap/state/(?P<abbreviation>.*)/$', 'website.views.info.state_jurisdictions'),
        (r'^sitemap/', 'website.views.info.site_map'),
        
        
        #### static info pages
        (r'^about/', info.about),   
        (r'^privacy-policy/', info.privacy_policy),        
        (r'^information-accuracy-disclaimer/', info.information_accuracy_disclaimer),   
        (r'^grant-info/', info.grant_info), 
        (r'^tou/', info.terms_of_use), 
            
        #### api calls
        (r'^api1/', 'website.views.api.searchState'))
    ## admin
    urlpatterns += patterns('',
                            url(r'^siteadmin/',
                                include(patterns('',
                                                 (r'^$', siteadmin.task_list),
                                                 (r'^user_page_views/$', siteadmin.user_page_views)))))
    if 'rosetta' in settings.INSTALLED_APPS:
        urlpatterns += patterns('',
                                url(r'^rosetta/', include('rosetta.urls')))
