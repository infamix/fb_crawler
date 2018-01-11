# -*- coding: utf-8 -*-
import scrapy
import json
import os
import re
import urlparse
import urllib
import datetime
import time

from datetime import datetime
from scrapy import Request
from bs4 import BeautifulSoup
from scrapy.shell import inspect_response
from scrapy.http import FormRequest



class FacebookSpider(scrapy.Spider):
    
    name = 'facebook'
    
    access_token='154222325302815|Ny6vy6OnheSr1omJ0w7BjW1EkGw'
        
    def __init__(self, ap_id=None, access_token='154222325302815|Ny6vy6OnheSr1omJ0w7BjW1EkGw', *args, **kwargs):
         super(FacebookSpider, self).__init__(*args, **kwargs)
         self.ap_id = ap_id
         self.start_urls = ["https://graph.facebook.com/v2.11/{AP_ID}/photos/uploaded?limit=40&access_token={TOKEN}".format(AP_ID=ap_id,
                      TOKEN=access_token)]
         

    def parse(self, response):
      img_dir = "./downloads/" + self.ap_id
      if not os.path.exists(img_dir):
        os.makedirs(img_dir, mode=0o777)
      jsonresponse = json.loads(response.body.decode('utf-8'))
      for photo in jsonresponse['data']:
        photo_id = photo['id']
        photo_url = "https://graph.facebook.com/v2.11/{PHOTO_ID}?fields=images&access_token={TOKEN}".format(PHOTO_ID=photo_id,TOKEN=self.access_token)
        date_str = photo['created_time']
        dt_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S+0000")
        unixdt = time.mktime(dt_obj.timetuple())
        yield Request(photo_url, callback=self.parse_image, meta={'DT': unixdt})
      next_photos_url = "https://graph.facebook.com/v2.11/{AP_ID}/photos/uploaded?limit=40&access_token={TOKEN}&after={NEXT}".format(AP_ID=self.ap_id, TOKEN=self.access_token, NEXT=jsonresponse['paging']['cursors']['after'])
      yield Request(next_photos_url, callback=self.parse)
      
    def parse_image(self, response):
      unixdt = response.meta.get('DT')
      jsonresponse_img = json.loads(response.body.decode('utf-8'))
      img_url = jsonresponse_img['images'][0]['source']
      if(os.path.exists("downloads/{}/{}.jpg".format(self.ap_id, jsonresponse_img["id"])) == False):
          urllib.urlretrieve(img_url, "downloads/{}/{}.jpg".format(self.ap_id, jsonresponse_img["id"]))
      os.utime("downloads/{}/{}.jpg".format(self.ap_id, jsonresponse_img["id"]),(unixdt,unixdt))

