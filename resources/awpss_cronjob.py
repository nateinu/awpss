#!/usr/bin/env python3

import os
import json
import random
from handlers import *
from subprocess import call
from collections import defaultdict
from set_wallpaper import set_wallpaper

try:
    from urlparse import urljoin  # Python2
    from urllib import urlopen
except ImportError:
    from urllib.parse import urljoin  # Python3
    from urllib.request import urlopen

hist = defaultdict(bool)

conf_dir  = os.path.join(os.path.expanduser('~'), '.awpss')
conf_file = os.path.join(conf_dir, 'config')
hist_file = os.path.join(conf_dir, 'history')

conf = {
    'api'        :'gelbooru_api',
    'url'        :'http://gelbooru.com/',
    'tags'       :'ore_no_imouto_ga_konna_ni_kawaii_wake_ga_nai',
    'timeout'    :'60',
    'rating'     :'true',
    'size'       :'true',
    'enabled'    :'true',
    'api_limit'  :'10',
    'cache_size' :'500', # Number of images
    'offset'     :'0',
    'user'       :'',
    'pass'       :''
}



def delete_cache(hist):
    for key in hist:
        os.remove(os.path.join(conf_dir, key))
    hist = defaultdict(bool)
    return hist



def get_pic_url(conf, hist, times):
    if len(hist) > 1:
        for key in hist:
            if hist[key] == 'false':
                hist[key] = 'true'
                return key
    
    if times == 1:
        return get_more_pic_urls(conf, hist) # Evil inu is evil~~~
    else:
        return random.choice(list(hist.keys())) # Ran into infinite loop already @_@, so added this

def get_more_pic_urls(conf, hist):
    
    if len(hist) > int(conf['cache_size']):
        hist = delete_cahce(hist)
    
    if   conf['api'] == 'pixiv_api':
        api = pixiv_api.PixivAPI()
    elif conf['api'] == 'gelbooru_api':
        api = gelbooru_api.GelbooruAPI()
    elif conf['api'] == 'danbooru_api':
        api = danbooru_api.DanbooruAPI()
    elif conf['api'] == 'shimmie2_danbooru_api':
        api = shimmie2_danbooru_api.Shimmie2DanbooruAPI()
    else:
        raise Error("Unknown API")
    
    conf['offset'] = str(len(hist))
    
    api.set_conf(conf)
    
    for item in api.get_file_url():
        if not item in hist:
            hist[item] = 'false'
    
    return get_pic_url(conf, hist, 2) # Evil inu is evil~~~



def read_hist_file():
    if not os.path.exists(hist_file):
        return defaultdict(bool)

    with open(hist_file, 'r') as handle:
        hist = json.loads(handle.read())

    if hist is None:
        return defaultdict(bool)

    return hist

def write_hist_file(hist):
    with open(hist_file, 'w') as handle:
        json.dump(hist, handle, indent=3)



if os.path.exists(conf_file):
    with open(conf_file, 'r') as handle:
        conf = json.loads(handle.read())

hist = read_hist_file()

pic_url  = get_pic_url(conf, hist, 1)
pic_name = os.path.basename(pic_url)

'''
"eCryptFS which uses part of the lower file name to keep metadata and limits the file name to a maximum length of 143 characters."
https://bugs.launchpad.net/ecryptfs/+bug/344878
'''
if len(pic_name) > 120:
    pic_name = pic_name[:120]

pic_file = os.path.join(conf_dir, pic_name)

write_hist_file(hist)

if not os.path.exists(pic_file):
    f = open(pic_file,'wb')
    f.write(urlopen(pic_url).read())
    f.close()

#call("DISPLAY=:0 GSETTINGS_BACKEND=dconf gsettings set org.gnome.desktop.background picture-uri %s" % pic_file, shell=True)
set_wallpaper(pic_file)


