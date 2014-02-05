from urlparse import urlparse

class UrlUtil():
    website = ''
    
    def __init__(self, website):
        self.website = website   
            
    def get_display_website(self):
        url_components = urlparse(self.website)
        if url_components.scheme == '':
            return str(url_components.path)
        else:
            return str(url_components.netloc)
    
    def get_href(self):
        url_components = urlparse(self.website)
        if url_components.scheme == '':
            return 'http://' + str(self.website)
        else:
            return self.website  