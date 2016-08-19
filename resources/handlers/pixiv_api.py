#!/usr/bin/env python3

#from pixivpy.pixivpy3 import *

class PixivAPI:
    
    conf  = dict()
    items = list()
    need_to_fetch = True
    
    url_api = 'api/danbooru/find_posts'
    
    #aapi = AppPixivAPI()
    #json_result = aapi.illust_ranking()
    #for illust in json_result.illusts[:3]:
    #    aapi.download(illust.image_urls.large)
    
    def fetch(self):
        requestURL = "%s%s?tags=" % (self.conf['url'], self.url_api)
        
        if self.conf['rating'] != 'false':
            requestURL += "rating:%s+" % self.conf['rating']
        
        if self.conf['size'] != 'false':
            requestURL += "size:%s+" % self.conf['size']
        
        requestURL += "%s&limit=%s&page=%s" % (self.conf['tags'], self.conf['api_limit'], self.conf['offset'])
        
        print(requestURL)
        root = ET.parse(urlopen(requestURL)).getroot()
        self.items = root.findall('post')
        
        need_to_fetch = False

    def get_file_url(self):
        for item in self.get_item():
            yield urljoin(self.conf['url'], item.attrib['file_url'])

    def get_rating(self):
        for item in self.get_item():
            yield item.attrib['rating']

    def get_tags(self):
        for item in self.get_item():
            yield item.attrib['tags']

    def get_hash(self):
        for item in self.get_item():
            yield item.attrib['md5']

    def get_item(self):
        if self.need_to_fetch:
            self.fetch()
        
        for item in self.items:
            yield item

    def set_conf(self, conf):
        conf['rating'] = 's' if conf['rating'] == 'true' else 'false'
        conf['offset'] = str( int( int(conf['offset']) / int(conf['api_limit']) ) + 1 )
        self.conf = conf


