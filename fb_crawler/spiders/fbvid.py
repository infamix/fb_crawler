# -*- coding: utf-8 -*-
import scrapy
import json
import os
import re
import urlparse
import urllib


from scrapy import Request
from bs4 import BeautifulSoup
from scrapy.shell import inspect_response
from scrapy.http import FormRequest



class FacebookVideoSpider(scrapy.Spider):
    
    name = 'fbvid'
    
    access_token='154222325302815|Ny6vy6OnheSr1omJ0w7BjW1EkGw'
        
    def __init__(self, page_id=None, access_token='154222325302815|Ny6vy6OnheSr1omJ0w7BjW1EkGw', *args, **kwargs):
         super(FacebookVideoSpider, self).__init__(*args, **kwargs)
         self.page_id = page_id
         self.start_urls = ["https://graph.facebook.com/v2.11/{PAGE_ID}/videos/uploaded?limit=40&access_token={TOKEN}".format(PAGE_ID=page_id,
                      TOKEN=access_token)]
         

    def parse(self, response):
      vid_dir = "./" + self.page_id
      if not os.path.exists(vid_dir):
        os.makedirs(vid_dir, mode=0o777)
      jsonresponse = json.loads(response.body.decode('utf-8'))
      for x in range(40):
        vid_id = jsonresponse['data'][x]['id']
        vid_url = "https://graph.facebook.com/v2.11/{VID_ID}?fields=images&access_token={TOKEN}".format(VID_ID=vid_id,TOKEN=self.access_token)
        yield Request(photo_url, callback=self.parse_vid)
      next_photos_url = "https://graph.facebook.com/v2.11/{PAGE_ID}/photos/uploaded?limit=40&access_token={TOKEN}&after={NEXT}".format(PAGE_ID=self.page_id, TOKEN=self.access_token, NEXT=jsonresponse['paging']['cursors']['after'])
      yield Request(next_photos_url, callback=self.parse)
      
    def parse_image(self, response):
      jsonresponse_img = json.loads(response.body.decode('utf-8'))
      img_url = jsonresponse_img['images'][0]['source']
      urllib.urlretrieve(img_url, "{}/{}.jpg".format(self.page_id, jsonresponse_img["id"]))
