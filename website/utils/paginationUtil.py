from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class PaginationUtil():
    current_page = 1
    max_rec_per_page = 20
    objs = []
    start_page = 1
    end_page = 20
    href = ""
    request_method = ''
    fist_page = 1
    end = 10
    max_num_pages = 10
    a_onclick = ''
    
    sort_column = ''
    sort_dir = 'asc'
    sort_columns = []
    sort_asc_img = ''
    sort_desc_img = ''
    sort_class = ''
    
    search_params = {}
    
    def __init__(self, request_method, search_params, href):
        self.request_method = request_method
        self.href = href  
        self.search_params = search_params                           
    
    def set_up_pagination(self, objs=[], page_num='1_1', max_rec_per_page=20, a_onclick=''):
        if page_num == '' or page_num == None:
            page_num = '1_1'
        page_num_values = page_num.split('_')

        if len(page_num_values) == 2:
            current_page = page_num_values[0]
            first_page = page_num_values[1]
        else:
            current_page = 1
            first_page = 1
        
        self.max_rec_per_page = max_rec_per_page    
        self.current_page = current_page 
        self.objs = objs 
        self.objs = objs
        self.first_page = first_page
        self.a_onclick = a_onclick
        
    def getCurrentPageItems(self):
        paginator = self.getPages()
        try:
            page = paginator.page(self.getCurrentPage())
        except:
            #if current page is out of range, set it to 1
            page = paginator.page(1)
            self.current_page = 1
        return page.object_list
    
    def getPages(self):
        return Paginator(self.objs, self.max_rec_per_page) 
    
    def getPaginationData(self):
        pages = self.getPages()
        cpage = self.getCurrentPage()    
        if int(cpage) > pages.num_pages: 
            cpage= 1    
            
            
        if self.sort_column != '':
            sort = '/' + self.sort_column + '/' + self.sort_dir
        else:
            sort = ''
        self.page = pages.page(cpage)        
        page_range = self.getPageRange()
        data = {}

        data['href'] = self.href
   
        data['href_first'] = self.href + sort + "/" +  str("1_") + str(page_range[0]) + "/"
        data['href_prev'] = self.href  + sort + "/" +  str(int(cpage)-1) + str("_") + str(page_range[0]) + "/"
        #data['href_paging'] = self.href + "/" +  str(1 - self.getPageRange()[0])         
        data['href_next'] = self.href + sort + "/" +  str(int(cpage)+1) + str("_") + str(page_range[0]) + "/"
        data['href_last'] = self.href + sort + "/" +  str(pages.num_pages) + str("_") + str(page_range[0]) + "/"
                
                                  
        data['page_num_first'] = str("1_") + str(page_range[0])                          
        data['page_num_prev'] = str(int(cpage)-1) + str("_") + str(page_range[0])  
        data['page_num_next'] = str(int(cpage)+1) + str("_") + str(page_range[0])  
        data['page_num_last'] = str(pages.num_pages) + str("_") + str(page_range[0]) 
        
        data['a_onclick'] = self.a_onclick 
        data['a_onclick_first'] = self.a_onclick.replace('xxx', str("1_") + str(page_range[0]) )    
        data['a_onclick_prev'] = self.a_onclick.replace('xxx',  str(int(cpage)-1) + str("_") + str(page_range[0]))    
        data['a_onclick_next'] = self.a_onclick.replace('xxx',  str(int(cpage)+1) + str("_") + str(page_range[0]))   
        data['a_onclick_last'] = self.a_onclick.replace('xxx',  str(pages.num_pages) + str("_") + str(page_range[0]))
        
        data['pages'] = {}
        page_num = int(page_range[0])
    
        while (page_num <= page_range[1] + 1):
            
            if self.request_method == 'get' :
                data['pages'][page_num] = self.href  + sort + '/' + str(page_num) + str("_") + str(page_range[0]) + "/"
            elif self.request_method == 'post':
                data['pages'][page_num] = str(page_num) + str("_") + str(page_range[0])
            elif self.request_method == 'ajax':
                data['pages'][page_num] = self.a_onclick.replace('xxx', str(page_num) + str("_") + str(page_range[0]))
                 
            page_num = page_num + 1


        data['request_method'] = self.request_method
        data['current_page'] = cpage
        data['num_pages'] = pages.num_pages
        data['page_range'] = page_range
        
        data['search_params'] = self.search_params
        data['sort_by'] = self.sort_column
        data['sort_dir'] = self.sort_dir
        
        return data
    
    def getCurrentPage(self):
        if self.current_page:
            return self.current_page
        else:
            if self.current_page == "":
                return 1

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False 
        
    def getPageRange(self):
        # get current page
        cpage = self.getCurrentPage()
       
        # if current page equal first in page list
        if int(self.first_page) == 1:
            adjustment = 1
        else:
            adjustment = 0
        if int(cpage) <= int(self.first_page) or int(cpage) >= int(self.first_page) + self.max_num_pages - adjustment:
        # determine the new first and new last, and the new page list
            first_page = int(cpage) - (self.max_num_pages / 2)
            last_page = int(cpage) + (self.max_num_pages / 2)
           
            if first_page < 1:
                first_page = 1
                last_page = self.max_num_pages
        elif int(cpage) < int(self.first_page):
            if int(cpage) == 1:
                adjustment = 1
            else:
                adjustment = 0            
            first_page = cpage
            last_page = int(cpage) + self.max_num_pages - adjustment
        else:    
            first_page = self.first_page
            last_page = int(self.first_page) + self.max_num_pages - adjustment
            
  
        
        if first_page < 1:
            first_page = 1       
           
        pages = self.getPages() 
        
        if last_page > pages.num_pages:
            last_page = pages.num_pages     
        
        return (first_page, last_page)   
    
    
    def set_up_sorting_by_columns(self, sort_columns, sort_desc_img, sort_asc_img, sort_class):
        self.sort_columns = sort_columns
        self.sort_asc_img = sort_asc_img
        self.sort_desc_img = sort_desc_img
        self.sort_class = sort_class
        
        return True
    
    def get_order_by_str(self, column_key, sort_dir):
        self.sort_column = column_key
        self.sort_dir = sort_dir

        order_by_str = ''
        if self.sort_columns and column_key in self.sort_columns.keys():
            if sort_dir != '':
                if sort_dir == 'asc':
                    sign = ''
                else:
                    sign = '-'
            else:
                if self.sort_columns[column_key] == 'asc':
                    sign = ''
                else:
                    sign = '-'
            
            order_by_str += sign+column_key
            
        return order_by_str
    
    def get_sorting_html_all_columns(self):
        html_str = {}
        for column_key in self.sort_columns.keys():
            html_str[column_key] = self.get_sorting_html_by_column(column_key)
            
        return html_str
    
    def get_sorting_html_by_column(self, column_key):
        html_str = ''
        if column_key in self.sort_columns.keys():
            if column_key == self.sort_column:
                if self.sort_dir == 'asc':
                    image_src = self.sort_asc_img
                    sort_dir = 'desc'
                    sort_dir_txt = 'ascending'
                else:
                    image_src = self.sort_desc_img
                    sort_dir = 'asc'
                    sort_dir_txt = 'descending'
            else:
                if self.sort_columns[column_key] == 'asc':
                    sort_dir = 'asc'
                else:
                    sort_dir = 'desc'                 
                
            href = self.href + '/' + column_key + '/' + sort_dir + '/1_1/'
            if self.request_method == 'post':
                onclick = "return submit_form('"+str(column_key)+"', '"+str(sort_dir)+"');"
            else:
                onclick = ""
                
            if column_key == self.sort_column:                
                html_str = "<span id='"+str(column_key)+"' class='"+str(self.sort_class)+"'><a href='"+href+"' onClick=\""+str(onclick)+"\" > " + column_key.capitalize()+ " </a><img alt='{{sort_dir_text}}' style='vertical-align:middle' heigh='20' width='20' src='"+str(image_src) +"' title='"+str(sort_dir_txt)+"' > <span>"
            else:
                html_str = "<span id='"+str(column_key)+"' class='"+str(self.sort_class)+"'><a href='"+href+"' onClick=\""+str(onclick)+"\" > " + column_key.capitalize()+ " </a><span>"
                

        return html_str