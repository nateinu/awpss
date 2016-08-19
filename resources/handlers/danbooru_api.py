#!/usr/bin/env python3

import xml.etree.ElementTree as ET

try:
    from urlparse import urljoin  # Python2
    from urllib import urlopen
except ImportError:
    from urllib.parse import urljoin  # Python3
    from urllib.request import urlopen

class DanbooruAPI:
    
    conf  = dict()
    items = list()
    need_to_fetch = True
    
    url_api = 'posts.xml'
    
    def fetch(self):
        #login and api_key
        requestURL = "%s%s?tags=" % (self.conf['url'], self.url_api)
        
        if self.conf['rating'] != 'false':
            requestURL += "rating:%s+" % self.conf['rating']
        
        if self.conf['size'] != 'false':
            requestURL += "width:%s+height:%s+" % tuple(self.conf['size'].split('x'))
        
        requestURL += "%s&limit=%s&page=%s" % (self.conf['tags'], self.conf['api_limit'], self.conf['offset'])
        
        if self.conf['user'] != '' and self.conf['pass'] != '':
            requestURL += "&login=%s&api_key=%s" % (self.conf['user'], self.conf['pass'])
        
        root = ET.parse(urlopen(requestURL)).getroot()
        self.items = root.findall('post')
        
        need_to_fetch = False

    def get_file_url(self):
        for item in self.get_item():
            yield urljoin(self.conf['url'], item.find('file-url').text)

    def get_rating(self):
        for item in self.get_item():
            yield item.find('rating').text

    def get_tags(self):
        for item in self.get_item():
            yield item.find('tag-string').text

    def get_hash(self):
        for item in self.get_item():
            yield item.find('md5').text

    def get_item(self):
        if self.need_to_fetch:
            self.fetch()
        
        for item in self.items:
            yield item

    def set_conf(self, conf):
        conf['rating'] = 'safe' if conf['rating'] == 'true' else 'false'
        conf['offset'] = str( int( int(conf['offset']) / int(conf['api_limit']) ) + 1 )
        self.conf = conf


