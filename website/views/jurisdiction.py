import re, math
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.localflavor.us.us_states import US_STATES
from django.contrib import messages
from django.template.loader import get_template as django_get_template
from django.template import Context, RequestContext
from website.utils.httpUtil import HttpRequestProcessor
from django.views.decorators import csrf
from dajax.core import Dajax
from django.conf import settings as django_settings
from django.core.mail.message import EmailMessage
from django.shortcuts import render
from django.db.models import Q
from django.shortcuts import render_to_response, redirect
from website.utils.mathUtil import MathUtil

from website.utils.geoHelper import GeoHelper
from website.models import Jurisdiction, Zipcode, UserSearch, Question, AnswerReference, OrganizationMember, QuestionCategory, Comment, UserCommentView, Template, ActionCategory, JurisdictionContributor, Action, UserDetail
from website.utils.messageUtil import MessageUtil,add_system_message,get_system_message
from website.utils.miscUtil import UrlUtil

from website.utils.datetimeUtil import DatetimeHelper
from django.contrib.auth.models import User
import json
import datetime
from htmlentitiesdecode import decode as entity_decode
import urllib

JURISDICTION_PAGE_SIZE = 30 #page size for endless scroll


#dispatch to either state map or listing within state
def jurisdiction_browse_improved(request):
    requestProcessor = HttpRequestProcessor(request)
    state = requestProcessor.getParameter('state')
    q_state = requestProcessor.getParameter('q')    
    if state ==None or state =='':
        if q_state !=None and q_state !='':    
            state = q_state
                
    if state ==None or state =='':
        #no state provided, go to US map
        return jurisdiction_browse_by_states(request)
    else:
        #go to state listing
        sort_by = requestProcessor.getParameter('sort_by')
        sort_dir = requestProcessor.getParameter('sort_dir')
        page_num = requestProcessor.getParameter('page')
        if sort_by == '' or sort_by == None:
            sort_by = 'name'
        else:
            if sort_by == 'name':
                sort_by = 'name'
            elif sort_by == 'last':
                sort_by = 'last_contributed'
            else:
                sort_by = 'last_contributed_by'
        return get_state_jurisdictions(request, state, sort_by, sort_dir, page_num)
    
#@csrf.csrf_protect
def get_state_jurisdictions(request, state='', sort_by='', sort_dir='', page_num=''):
    data = {}
    data['get_state_jurisdiction'] = True
    requestProcessor = HttpRequestProcessor(request)
    search_str = requestProcessor.getParameter('text_2') 
    if search_str == None or search_str == 'Search':
        search_str = ''       
    filter = requestProcessor.getParameter('filter')
    if filter == None:
        filter = 'all'
        
    only_jurisditions_with_data = requestProcessor.getParameter('only_jurisditions_with_data')        
    if only_jurisditions_with_data != None:
        data['only_jurisditions_with_data'] = int(only_jurisditions_with_data)
    else:
        ajax = requestProcessor.getParameter('ajax')
        if ajax == 'filter':
            data['only_jurisditions_with_data'] = 0
        else:
            if 'only_jurisditions_with_data' in request.session:
                data['only_jurisditions_with_data'] = request.session['only_jurisditions_with_data']
            else:
                data['only_jurisditions_with_data'] = 1
    request.session['only_jurisditions_with_data'] = data['only_jurisditions_with_data']          

    if sort_by == '' or sort_by == None:
        sort_by = 'name'
    elif sort_by == 'last':
        sort_by = 'last_contributed'

    if sort_dir == '' or sort_dir == None:
        sort_dir = 'asc'
    if sort_dir == 'asc':
        order_by_str = sort_by
    else:
        order_by_str = '-'+sort_by

    data['sort_by'] = sort_by
    data['sort_dir'] = sort_dir

    data['secondary_search_str'] = search_str
    data['filter'] = filter
        
    user = request.user
    if user.is_authenticated():
        data['nav'] = 'yes'
        data['breadcrum'] = 'no'
    else:
        data['nav'] = 'no'    
        data['breadcrum'] = 'yes'  
        #return HttpResponseRedirect("/sign_in/?next=/jurisdiction_browse/"+state+"/name/asc/1_1/")  
            
    sort_desc_img = django_settings.SORT_DESC_IMG
    sort_asc_img = django_settings.SORT_ASC_IMG
    sort_class = django_settings.SORT_CLASS
    sort_columns = {}
    sort_columns['name'] = 'asc'
    sort_columns['county'] = 'asc'
    sort_columns['last_contributed'] = 'asc'
    sort_columns['last_contributed_by'] = 'asc'
   
    data['current_nav'] = 'browse'
    href = '/jurisdiction/browse/?state=' + state

    search_params = {}

    #data['page_title'] = "Browse Jurisdiction: " + state

    if state == '':
        state = 'CA'
        
    data['state'] = state
    data['state_long_name'] = dict(US_STATES)[state]
    #type = 'S'
    #data['state_list'] = Jurisdiction.objects.filter(state__iexact=state, jurisdiction_type__iexact=type)     
    
    if filter == 'county':
        type = ['CO', 'CONP', 'SC' ]
    elif filter == 'city':
        type = ['CI', 'CINP', 'SCFO', 'U']
    elif filter == 'state':
        type = ['S']        
    else:
        type = ''

    page = requestProcessor.getParameter('page')
    if page != None and page != '':
        page_number = int(page)
    else:
        page_number = 1
    range_start = (page_number - 1) * JURISDICTION_PAGE_SIZE
    range_end = page_number * JURISDICTION_PAGE_SIZE
    data['next_page_param'] = 'page='+str(page_number + 1)
    
    objects = Jurisdiction.objects.none() 
        
        
    if search_str == '':
        if filter == 'all' or filter == '' or filter == None:
            if data['only_jurisditions_with_data'] == 1:
                objects |= Jurisdiction.objects.filter(last_contributed__isnull = False, state__iexact=state)     
                objects |= Jurisdiction.objects.filter(state__iexact=state, jurisdiction_type__in=('U', 'SCFO'), parent__last_contributed__isnull=False)   
            else:
                objects |= Jurisdiction.objects.filter(last_contributed__isnull = True, state__iexact=state)       
                    
        elif filter == 'county' or filter == 'city' or filter == 'state':
            if data['only_jurisditions_with_data'] == 1:
                objects |= Jurisdiction.objects.filter(last_contributed__isnull = False, state__iexact=state, jurisdiction_type__in=type)     
                objects |= Jurisdiction.objects.filter(state__iexact=state, jurisdiction_type__in=('U', 'SCFO'), parent__last_contributed__isnull=False)   
            else:
                objects |= Jurisdiction.objects.filter(last_contributed__isnull = True, state__iexact=state, jurisdiction_type__in=type)                  
            
            
    else:
        if filter == 'all' or filter == '' or filter == None:
            if data['only_jurisditions_with_data'] == 1:
                objects |= Jurisdiction.objects.filter(name__icontains=search_str, last_contributed__isnull = False, state__iexact=state)     
                objects |= Jurisdiction.objects.filter(name__icontains=search_str, state__iexact=state, jurisdiction_type__in=('U', 'SCFO'), parent__last_contributed__isnull=False)   
            else:
                objects |= Jurisdiction.objects.filter(name__icontains=search_str, state__iexact=state, last_contributed__isnull = True)                
                    
        elif filter == 'county' or filter == 'city' or filter == 'state':
            if data['only_jurisditions_with_data'] == 1:
                objects |= Jurisdiction.objects.filter(name__icontains=search_str, last_contributed__isnull = False, state__iexact=state, jurisdiction_type__in=type)     
                objects |= Jurisdiction.objects.filter(name__icontains=search_str, state__iexact=state, jurisdiction_type__in=('U', 'SCFO'), parent__last_contributed__isnull=False)   
            else:
                objects |= Jurisdiction.objects.filter(name__icontains=search_str, state__iexact=state, jurisdiction_type__in=type, last_contributed__isnull = True)  
                            
    if sort_by == '' or sort_by == None:
        objects = objects.order_by('name', 'county')
    else:                        
        objects = objects.order_by(order_by_str) 
    
    data['count'] = len(objects)    
    data['list'] = objects[range_start:range_end]


    #data['system_message_type'] = 'success'
    #data['system_message_text'] = 'A lot of data found for your consumption'    
    
    data['action'] = "/jurisdiction/browse/?state="+state
    data['home'] = '/'
    data['user'] = request.user 
    
    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data
    
    dajax = Dajax()
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):
        #handle ajax calls
        if ajax == 'filter':
            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/jurisdiction_list.html', data, '') 
            dajax.assign('#jurisdiction_list','innerHTML', body)
            if page_number == 1: #initialize jscroll if page 1
                script = requestProcessor.decode_jinga_template(request, 'website/jurisdictions/jurisdiction_list.js', data, '')
                dajax.script(script)
                
            if int(data['only_jurisditions_with_data'])  == 1:
                message = 'Jurisdictions without data are hidden. Uncheck to show.'
            else:
                message = 'Jurisdictions without data are visible. Check to hide.'
                
            dajax.assign('#only_jurisdictions_with_data_message','innerHTML', message)
            
            return HttpResponse(dajax.json())
        
        return HttpResponse(dajax.json())
    #data['user'] = request.user
    if page_number != 1:
        #for endless scroll next page, only render the list
        return requestProcessor.render_to_response(request,'website/jurisdictions/jurisdiction_list.html', data, '')      
    else:
        return requestProcessor.render_to_response(request,'website/jurisdictions/jurisdiction_by_state.html', data, '')      

def jurisdiction_browse_by_states(request):
    data = {}
    requestProcessor = HttpRequestProcessor(request)
    
    #message_key = requestProcessor.getParameter('message_key')
    #messageUtil = MessageUtil(message_key)
    #data['system_message_type'] = messageUtil.get_system_message_type()   # optional
    #data['system_message_text'] = messageUtil.get_system_message_text()   
    
    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data
            
    data['page_title'] = "Browse Jurisdictions"
      
    #data['state_list'] = US_STATES
    return requestProcessor.render_to_response(request,'website/jurisdictions/jurisdiction_state_browse.html', data, '')
    #return render(request, 'website/jurisdictions/jurisdiction_state_browse.html', data)

def check_search_level(search_str):
    search_str = search_str.lower()
    if search_str.find('county') > -1 or search_str.find('parish') > -1: 
        search_level = 'county' 
    elif search_str.find('city') > -1:  
        search_level = 'city'
    else:
        search_level = ''
    
    return search_level

def exclude(search_str):
    search_str = search_str.lower()
    if search_str.find('city') > -1:  
        exclude = 'unincorporated'
    else:
        exclude = ''
    
    return exclude

def scrub_text_search_str(search_str):
    search_str_only_a_z = re.sub("[^A-Za-z]", ' ', search_str).lower()
    search_str_only_a_z = search_str_only_a_z.replace('borough of', '')
    search_str_only_a_z = search_str_only_a_z.replace('borough', '')
    search_str_only_a_z = search_str_only_a_z.replace('parish of', '')
    search_str_only_a_z = search_str_only_a_z.replace('parish', '')
    search_str_only_a_z = search_str_only_a_z.replace('county of', '')
    search_str_only_a_z = search_str_only_a_z.replace('county', '')
    search_str_only_a_z = search_str_only_a_z.replace('city and county of', '')
    search_str_only_a_z = search_str_only_a_z.replace('state of', '')
    search_str_only_a_z = search_str_only_a_z.replace('state', '')
    search_str_only_a_z = search_str_only_a_z.replace('city', '')
    return search_str_only_a_z.strip()

#get the nearby jurisdictions given a center point and starting distance range
def getNearbyJs(geoHelper, center, distance, iteration):
    range = geoHelper.getSquare(center, distance)
    nearbyJs = Jurisdiction.objects.filter(latitude__gt=range['latMin'], latitude__lt=range['latMax'], longitude__gt=range['lonMin'], longitude__lt=range['lonMax']).order_by('name')
    
    #if already reached max iteration, just return results
    if iteration >= geoHelper.maxIteration:
        return nearbyJs
    #see if result count is already within target +/- margin
    margin = len(nearbyJs) - geoHelper.targetCount
    if margin <= geoHelper.targetMargin and margin >= -geoHelper.targetMargin:
        return nearbyJs
    #already at max distance and still less than targetCount, just return result
    if distance >= geoHelper.maxDistance and len(nearbyJs) <= geoHelper.targetCount:
        return nearbyJs
        
    newDistance = geoHelper.reviseDistance(distance, len(nearbyJs))
    return getNearbyJs(geoHelper, center, newDistance, iteration + 1)

def sortNearbyJs(geoHelper, center, nearbyJs):
    j_list = []
    for jurisdiction in nearbyJs:
        j_obj = {}
        j_obj['jurisdiction'] = jurisdiction
        j_point = {
            'lat': jurisdiction.latitude,
            'lon': jurisdiction.longitude
        }
        j_obj['distance'] = geoHelper.getDistance(center, j_point)
        j_list.append(j_obj)
    
    j_list.sort(key=lambda j_obj: j_obj['distance'])
    
    sortedJs = []
    for j_obj in j_list:
        jurisdiction = j_obj['jurisdiction']
        jurisdiction.distance = j_obj['distance']
        jurisdiction.unit = 'mi'
        sortedJs.append(jurisdiction)
    return sortedJs
    
def jurisdiction_autocomplete(request):
    MAX_RESULT_COUNT = 7
    
    requestProcessor = HttpRequestProcessor(request)
    output = ''
    
    text = requestProcessor.getParameter('q')
    if text == None or text == '': 
        return HttpResponse(output)
    
    output += '<div>' #a div to enclose everything
    output += '<ul id="search_results">'
    
    jurisdictions = []
    
    mathUtil = MathUtil()
    if mathUtil.is_number(text) == False:
        jurisdictions = jurisdiction_text_search(text,
                                                 scrub_text_search_str(text),
                                                 "",
                                                 check_search_level(text) or 'all',
                                                 'name',
                                                 0,
                                                 MAX_RESULT_COUNT,
                                                 exclude(text),
                                                 '')
    else:
        #is number, so zipcode based search
        zipcodes = Zipcode.objects.filter(zip_code__startswith=text)[0:1]
        
        #if zip code not found, look for next zip code up
        if len(zipcodes) < 1:
            zipcodes = Zipcode.objects.filter(zip_code__gt=text)[0:1]
        
        if len(zipcodes) > 0:
            zipcode = zipcodes[0] #should be only one anyway
            
            geoHelper = GeoHelper()
            geoHelper.targetCount = MAX_RESULT_COUNT #target number of nearby items to get
            geoHelper.targetMargin = 2 #+ and - this number of items from the target number to stop
            
            center = {}
            center['lat'] = zipcode.latitude
            center['lon'] = zipcode.longitude
            #zip code data problem - longitude needs to be inverted:
            center['lon'] = float(-center['lon'])
            
            jurisdictions = getNearbyJs(geoHelper, center, geoHelper.initialDistance, 1)
            jurisdictions = sortNearbyJs(geoHelper, center, jurisdictions)
            jurisdictions = jurisdictions[:MAX_RESULT_COUNT]
    
    for jurisdiction in jurisdictions:
        output += '<li><a href="/jurisdiction/'+str(jurisdiction.id)+'">'+jurisdiction.show_jurisdiction()+'</a></li>'
    
    output += '</ul>'
    output += '</div>'
    
    return HttpResponse(output)
        

def save_recent_search(user, jurisdiction):
    try:
        user_search = UserSearch(user=user)
        user_search.entity_name = 'Jurisdiction'
        user_search.entity_id = jurisdiction.id
        user_search.label = jurisdiction.show_jurisdiction()
        user_search.save()
    except:
        pass
    
    
def jurisdiction_search_improved(request):    
    requestProcessor = HttpRequestProcessor(request)

    data = {'page_class': 'meta'}
    data['breadcrum'] = 'no'
    data['nav'] = 'yes'         
    data['current_nav'] = 'browse'
    #handle ajax near the end since it needs the same query in most cases
    #but need to know if it is ajax to prevent redirect to jurisdiction page
    dajax = Dajax()
    ajax = requestProcessor.getParameter('ajax')

    caller = requestProcessor.getParameter('caller')             
    if caller == '' or caller == None:
        caller = 'general_search'   
        
    data['caller'] = caller     
   
    form = None    

    primary_search_str = requestProcessor.getParameter('q')
    text_primary_search_str = requestProcessor.getParameter('text')    

    if primary_search_str == None:        
        primary_search_str = ''
        
    if text_primary_search_str == None:        
        text_primary_search_str = ''   
        
    # replace primary_search_str with q_primary_search_str if q_primary_search_str is available
    if primary_search_str == '':
        if text_primary_search_str != '':
            primary_search_str = text_primary_search_str
                                  
    data['primary_search_str'] = primary_search_str   
    
    if caller == 'state_jurisdictions':
        data['state_long_name'] = dict(US_STATES)[primary_search_str]     
    
    
    secondary_search_str = requestProcessor.getParameter('text_2') 
    if secondary_search_str == None or secondary_search_str=='Search':
        secondary_search_str = ''                                  
    data['secondary_search_str'] = secondary_search_str      

    search_level = check_search_level(primary_search_str)
    
    primary_exclude = exclude(primary_search_str)
        
    filter = requestProcessor.getParameter('filter')
    if filter == None:
        if search_level != '':
            filter = search_level
        else:
            filter = 'all'

    data['filter'] = filter   

    sort_by = requestProcessor.getParameter('sort_by')
    if sort_by == None:
        sort_by = ''                               
    data['sort_by'] = sort_by   
    
    sort_dir = requestProcessor.getParameter('sort_dir') 
    if sort_dir == None:
        sort_dir = ''                                  
    data['sort_dir'] = sort_dir   

    #order_by_str = pagingation_obj.get_order_by_str(sort_by, sort_dir)   
    if sort_by == '' or sort_by == None:
        sort_by = 'name'
    else:
        if sort_by == 'name':
            sort_by = 'name'
        elif sort_by == 'last':
            sort_by = 'last_contributed'
        else:
            sort_by = 'last_contributed_by'
    if sort_dir == '' or sort_dir == None:
        sort_dir = 'asc'
  
    sort_desc_img = django_settings.SORT_DESC_IMG
    sort_asc_img = django_settings.SORT_ASC_IMG
           
    if sort_dir == 'asc':           
        order_by_str = sort_by
        data['image_src'] = sort_asc_img
        data['sort_dir_txt'] = 'ascending' 
        data['sort_dir'] = 'asc'       
    else:
        order_by_str = '-'+sort_by
        data['image_src'] = sort_desc_img
        data['sort_dir_txt'] = 'descending'
        data['sort_dir'] = 'desc'
        
    
    page = requestProcessor.getParameter('page')
    if page != None and page != '':
        page_number = int(page)
    else:
        page_number = 1
    range_start = (page_number - 1) * JURISDICTION_PAGE_SIZE
    range_end = page_number * JURISDICTION_PAGE_SIZE
    data['next_page_param'] = 'page='+str(page_number + 1)
    
    data['message'] = ''
    mathUtil = MathUtil()
    if mathUtil.is_number(primary_search_str) == False:
        data['search_by'] = 'search_by_name';
        scrubbed_primary_search_str = scrub_text_search_str(primary_search_str)
        
        sec_exclude = exclude(secondary_search_str)
            
        if primary_search_str.__len__() >= 2:
            objects_all_types = jurisdiction_text_search(primary_search_str, scrubbed_primary_search_str, secondary_search_str,filter, order_by_str, range_start, range_end, primary_exclude, sec_exclude)
            redirect_url = '/jurisdiction/'
                
            if len(objects_all_types) == 1 and ajax == None: #don't redirect if ajax
                redirect_url = redirect_url + str(objects_all_types[0].get_name_for_url()) + '/'
                return redirect(redirect_url)
            else:
                data['list'] = objects_all_types
        else:
            data['message'] = 'This search field requires at least 2 alphabetic (a-z) characters.';
    else:
        data['search_by'] = 'search_by_zip'
        if page_number != 1:
            #for zip search, currently doesn't have endless scroll next page, return blank
            data['list'] = []
            return requestProcessor.render_to_response(request,'website/jurisdictions/jurisdiction_list.html', data, '')
        nearbyJs = {}
        #geo based approach
        zipcodes = Zipcode.objects.filter(zip_code=primary_search_str)
        
        #TODO: if zip code not found, look for next zip code up
        if len(zipcodes) < 1:
            zipcodes = Zipcode.objects.filter(zip_code__gt=primary_search_str)[0:1]
        
        if len(zipcodes) > 0:
            zipcode = zipcodes[0] #should be only one anyway
            
            geoHelper = GeoHelper()
            center = {}
            center['lat'] = zipcode.latitude
            center['lon'] = zipcode.longitude
            #zip code data problem - longitude needs to be inverted:
            center['lon'] = float(-center['lon'])
            
            nearbyJs = getNearbyJs(geoHelper, center, geoHelper.initialDistance, 1 )
                
            #sort by distance
            nearbyJs = sortNearbyJs(geoHelper, center, nearbyJs)
                    
            data['list'] = nearbyJs
        
    request.session['primary_search_str'] = primary_search_str 
    data['user'] = request.user 
    
    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data
       
    if (ajax != None):
        #handle ajax calls
        if ajax == 'filter':
            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/jurisdiction_list.html', data, '') 
            dajax.assign('#jurisdiction_list','innerHTML', body)
            if page_number == 1: #initialize jscroll if page 1
                script = requestProcessor.decode_jinga_template(request, 'website/jurisdictions/jurisdiction_list.js', data, '')
                dajax.script(script)
            return HttpResponse(dajax.json())
        
        return HttpResponse(dajax.json())

    if page_number != 1:
        #for endless scroll next page, only render the list
        return requestProcessor.render_to_response(request,'website/jurisdictions/jurisdiction_list.html', data, '')      
    else:
        return requestProcessor.render_to_response(request,'website/jurisdictions/jurisdiction_search_results.html', data, '')      
    
def jurisdiction_text_search(primary_search_str, scrubbed_primary_search_str, secondary_search_str, filter, order_by_str, range_start=0, range_end=JURISDICTION_PAGE_SIZE, primary_exclude='', sec_exclude=''):
    state_filter_list = []

    if scrubbed_primary_search_str != '':
        search_terms = scrubbed_primary_search_str.lower().split(' ')
        state_abbrevs = dict([(s.lower(), s) for s in dict(US_STATES).keys()])
        state_names = dict([(s[1].lower(), s[0]) for s in US_STATES])

        words = []
        for word in search_terms:
            if state_abbrevs.has_key(word):
                state_filter_list.append(state_abbrevs[word])
            elif state_names.has_key(word):
                state_filter_list.append(state_names[word])
                # this state name might actually be a city name, so
                # add it to the search list
                words.append(word)
            elif word:
                words.append(word)

        search_words = [" ".join(words), scrubbed_primary_search_str, primary_search_str]
        return query(state_filter_list, search_words, secondary_search_str, filter, order_by_str, range_start, range_end, primary_exclude, sec_exclude)
    return Jurisdiction.objects.none()

def query(state_list, search_words, secondary_search_str, filter,
          order_by_str, range_start=0,
          range_end=JURISDICTION_PAGE_SIZE,
          primary_exclude='',sec_exclude=''):
    query = reduce(lambda q, word:
                       q | Q(name__icontains = word.strip()) if word.strip() else q,
                   search_words, Q())
    objects = Jurisdiction.objects.filter(query)
    if secondary_search_str:
        objects = objects.filter(name__icontains = secondary_search_str)

    if filter == 'county':  
        objects = objects.filter(jurisdiction_type__in=('CO', 'CC'))
    elif filter == 'city':
        objects = objects.filter(jurisdiction_type__in=('CI', 'U', 'CC'))
    elif filter == 'state':
        objects = objects.filter(jurisdiction_type__in=('S'))
    
    if state_list:
        objects = objects.filter(state__in=state_list)

    if primary_exclude == 'unincorporated' or sec_exclude == 'unincorporated':        
        objects = objects.exclude(jurisdiction_type__in='U')

    return objects.order_by(order_by_str, 'state')[range_start:range_end]
    
def jurisdiction_comment(request):
    requestProcessor = HttpRequestProcessor(request)
    user = request.user
    data = {}
    dajax = Dajax()
    ajax = requestProcessor.getParameter('ajax')
    comments_changed = requestProcessor.getParameter('comments_changed')
    if comments_changed == 'yes':
        data['comments_changed'] = 'yes'
    else:
        data['comments_changed'] = 'no'
    if (ajax != None):
        if ajax == 'open_jurisdiction_comment':
            entity_id = requestProcessor.getParameter('entity_id')
            entity_name = requestProcessor.getParameter('entity_name')
            jid = requestProcessor.getParameter('jurisdiction_id')
            try:
                jurisdiction = Jurisdiction.objects.get(id = jid)
            except:
                jurisdiction = None
            comments = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id, parent_comment__isnull = True).order_by('-create_datetime')
  
            userviews = UserCommentView.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id, user = user)
            
            temp_comments = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).order_by('-create_datetime')
            last_comment = None
            if len(temp_comments) > 0 :
                last_comment = temp_comments[0]
            
            has_userview = False
            if len(userviews) > 0:
                userview = userviews[0]
                if userview.last_comment != None:
                    data['userview_last_comment'] = userview.last_comment.id
                    data['userview'] = userviews[0]
                    userview.comments_count = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).count()
                    userview.last_comment = last_comment
                    userview.view_datetime = datetime.datetime.now()
                    userview.save()
                    has_userview = True
            if has_userview == False:
                userview = None
                data['userview'] = userview
                data['userview_last_comment'] = 0
                userview = UserCommentView()
                userview.user = user
                userview.jurisdiction = jurisdiction
                userview.entity_name = entity_name
                userview.entity_id = entity_id
                userview.comments_count = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).count()
                userview.last_comment = last_comment
                userview.view_datetime = datetime.datetime.now()
                userview.save()
            
            af = AnswerReference.objects.get(id = entity_id)
            aa = ValidationUtil()
            data['answer'] = af
            data['answer_text'] = aa.get_formatted_value(af.value, af.question)
            data['jurisdiction'] = jurisdiction
            label = af.question.question
            if len(af.question.question) > 75:
                label = af.question.question[:78]+ '...'
            data['label'] = label
            
            data['commnets'] = comments
            
            others_afs = AnswerReference.objects.filter(jurisdiction = jurisdiction, question = af.question, approval_status='A').exclude(id = entity_id).order_by('-create_datetime')
            if len(others_afs) > 0 :
                old_answer = others_afs[0]
                if old_answer.id < af.id:
                    data['old_answer'] = old_answer
                    data['old_answer_text'] = aa.get_formatted_value(old_answer.value, old_answer.question)
                else:
                    data['old_answer'] = None
                    data['old_answer_text'] = ''
            else:
                data['old_answer'] = None
                data['old_answer_text'] = ''
  
            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/jurisdiction_comment.html', data, '') 
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/jurisdiction_comment.js', data, '')
            dajax.script(script)
            #script = requestProcessor.decode_jinga_template(request,'website/blocks/comments_list.js', data, '')
            #dajax.script(script)
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')
        
        if ajax =='create_jurisdiction_comment':
            answer_id = requestProcessor.getParameter('answer_id')
            jid = requestProcessor.getParameter('jurisdiction_id')
            comment_type = 'JC'
            
            data['answer_id'] = answer_id
            data['jurisdiction_id'] = jid
            data['comment_type'] = comment_type
            data['parent_comment'] = ''
            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/create_comment.html', data, '')
            script =  requestProcessor.decode_jinga_template(request,'website/jurisdictions/create_comment.js', data, '')
            dajax.assign('#secondDialogDiv','innerHTML', body) 
            dajax.script(script)
            dajax.script('controller.showSecondDialog("#secondDialogDiv");')
        
        if ajax =='comment_create_submit':
            entity_id = requestProcessor.getParameter('entity_id')
            entity_name = requestProcessor.getParameter('entity_name')
            jurisdiction_id = requestProcessor.getParameter('jurisdiction_id')
            comment_type = requestProcessor.getParameter('comment_type')
            comment_text = requestProcessor.getParameter('comment')
            parent_comment = requestProcessor.getParameter('parent_comment')
            try:
                jurisdiction = Jurisdiction.objects.get(id = jurisdiction_id)
            except:
                jurisdiction = None
                
            comment = Comment()
            comment.jurisdiction = jurisdiction
            comment.entity_name = entity_name
            comment.entity_id = entity_id
            comment.user = user
            comment.comment_type = comment_type
            comment.comment = comment_text
            if parent_comment != '':
                parent = Comment.objects.get(id = parent_comment)
                comment.parent_comment = parent
            comment.save()
            
            userviews = UserCommentView.objects.filter(user = user, jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id)
            userview = userviews[0]
            userview.last_comment = comment
            userview.comments_count = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).count()
            userview.view_datetime = datetime.datetime.now()
            userview.save()
            
            
            dajax.script('controller.closeSecondDialog();')
            dajax.script('controller.postRequest("/jurisdiction_comment/", {ajax: "open_jurisdiction_comment", jurisdiction_id:'+str(jurisdiction_id)+', entity_id: "'+str(entity_id)+'", entity_name: "'+str(entity_name)+'", comments_changed: "yes"});')

            data = {}
            data['action'] = 'refresh_ahj_qa'
            answer = AnswerReference.objects.get(id=entity_id) 
            validation_util_obj = ValidationUtil()                  
            body = validation_util_obj.get_question_answers_display_data(request, answer.jurisdiction, answer.question, data)      
            dajax.assign('#div_'+str(answer.question_id),'innerHTML', body)      
                
        if ajax =='reply_comment':
            cid = requestProcessor.getParameter('cid')
            comment = Comment.objects.get(id = cid)            
            data['comment'] = comment
            body = requestProcessor.decode_jinga_template(request,'website/blocks/reply_comment_form.html', data, '')
            script = requestProcessor.decode_jinga_template(request,'website/blocks/reply_comment_form.js', data, '')
            dajax.assign('#button-div-'+str(cid),'innerHTML', body) 
            dajax.script(script)
            
        
        if ajax == 'cancel_reply':
            cid = requestProcessor.getParameter('cid')
            body = '<a class="smallbutton" href="#" onClick="controller.postRequest(\'/jurisdiction_comment/\', {ajax: \'reply_comment\', cid: '+str(cid)+'});return false;">Reply</a><a class="smallbutton" href="#">Flag</a>'
            dajax.assign('#button-div-'+str(cid),'innerHTML', body) 
            
        if ajax == 'flag_comment':
            cid = requestProcessor.getParameter('cid')
            comment = Comment.objects.get(id = cid) 
            comment.approval_status = 'F'
            comment.save()
            
            af = AnswerReference.objects.get(id = comment.entity_id)
            to_mail = [django_settings.ADMIN_EMAIL_ADDRESS]
            data['comment'] = comment
            data['user'] = user
            data['question'] = af.question.question
 
            data['site_url'] = django_settings.SITE_URL
            data['requestProcessor'] = requestProcessor
            data['request'] = request
            send_email(data, to_mail)
            
            dajax.assign('#comment_'+str(cid), 'innerHTML', '<p>This comment had been flagged as inappropriate and is hidden pending review.</p>')
        
        if ajax == 'show_old_comments':
            entity_id = requestProcessor.getParameter('answer_id')
            entity_name = 'AnswerReference'
            jid = requestProcessor.getParameter('jurisdiction_id')
            try:
                jurisdiction = Jurisdiction.objects.get(id = jid)
            except:
                jurisdiction = None
            comments = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id, parent_comment__isnull = True).order_by('-create_datetime')
            
            userviews = UserCommentView.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id, user = user)
            
            temp_comments = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).order_by('-create_datetime')
            last_comment = None
            if len(temp_comments) > 0 :
                last_comment = temp_comments[0]
            if len(userviews) > 0:
                userview = userviews[0]
                data['userview'] = userview
                userview.comments_count = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).count()
                userview.last_comment = last_comment
                userview.view_datetime = datetime.datetime.now()
                userview.save()
            else:
                userview = None
                data['userview'] = userview
                userview = UserCommentView()
                userview.user = user
                userview.jurisdiction = jurisdiction
                userview.entity_name = entity_name
                userview.entity_id = entity_id
                userview.comments_count = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).count()
                userview.last_comment = last_comment
                userview.view_datetime = datetime.datetime.now()
                userview.save()
            data['commnets'] = comments
            
            body = requestProcessor.decode_jinga_template(request,'website/blocks/comments_list.html', data, '')
            dajax.assign('#old_list ul', 'innerHTML', body)
            dajax.assign('#show_commnet_div', 'innerHTML', '<a id="id_a_hide" href="#"><img src="/media/images/arrow_down.png" style="vertical-align:bottom;" alt="Hide old comments" >Hide old comments </a>')
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/jurisdiction_comment.js', data, '')
            dajax.script(script)
            
        return HttpResponse(dajax.json())
    return

def send_email(data, to_mail, subject='Flag Comment', template='flag_comment.html'): 
    #tp = django_get_template('website/emails/' + template)
    #c = Context(data)
    #body = tp.render(c)
    
    requestProcessor = data['requestProcessor']
    request = data['request']
    body = requestProcessor.decode_jinga_template(request, 'website/emails/' + template, data, '')

    from_mail = django_settings.DEFAULT_FROM_EMAIL

    msg = EmailMessage( subject, body, from_mail, to_mail)
    msg.content_subtype = "html"   
    msg.send()
    
    
