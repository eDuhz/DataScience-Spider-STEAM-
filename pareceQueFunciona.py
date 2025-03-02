#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-09 11:12:50
# Project: steam_project

from pyspider.libs.base_handler import *
import re
tag = '9'

class Handler(BaseHandler):
    crawl_config = {
    }
    
    @every(minutes=2)
    def on_start(self):
        self.crawl('http://store.steampowered.com/search/?tags='+ tag +'&page=1', callback=self.index_page)

    @config(priority=2)
    def detail_page(self, response):
        if response.doc('.game_purchase_action > div > .price').text():
            return {
                "url": response.url,
                "title": response.doc('.apphub_AppName').text(),
                "developer": response.doc('#developers_list > a').text(),
                "score": response.doc('.high').text(),
                "overall_Reviews": response.doc('#review_histogram_rollup_section span.game_review_summary').text(),
                "price": response.doc('.game_purchase_action > div > .price').text().split(' ')[1].replace(',','.'),
                "release_date": response.doc('.date').text(),
                "genre": response.doc('.underlined_links a').text().split(' ')[0]
            }
        elif response.doc('.discount_final_price').text():
            return {
                "url": response.url,
                "title": response.doc('.apphub_AppName').text(),
                "developer": response.doc('#developers_list > a').text(),
                "score": response.doc('.high').text(),
                "overall_Reviews": response.doc('#review_histogram_rollup_section span.game_review_summary').text(),
                "price": response.doc('.discount_final_price').text().split(' ')[1].replace(',','.'),
                "release_date": response.doc('.date').text(),
                "genre": response.doc('.underlined_links a').text().split(' ')[0]
            }
        else:
            return {
                "url": response.url,
                "title": response.doc('.apphub_AppName').text(),
                "developer": response.doc('#developers_list > a').text(),
                "score": response.doc('.high').text(),
                "overall_Reviews": response.doc('#review_histogram_rollup_section span.game_review_summary').text(),
                "price": 'None',
                "release_date": response.doc('.date').text(),
                "genre": response.doc('.underlined_links a').text().split(' ')[0]
            }

    def filter_page(self, response):
        
        #Agecheck1 - click the button
        if re.match("http://store.steampowered.com/app/\d+/age\w+", response.url):
            self.crawl(response.url,
                               fetch_type='js', js_script="""function() {
                               HideAgeGate();
                   }
                   """,callback=self.detail_page)
        #Agecheck2 - Select birthday
        elif re.match("http://store.steampowered.com/agecheck/app/\d+", response.url):
            self.crawl(response.url,
                               fetch_type='js', js_script="""function() {
                               $J('#ageYear').val(1980);
                                $J('#agecheck_form').submit();
                   }
                   """,callback=self.detail_page)
        #Normal access
        else:
            if response.doc('.game_purchase_action > div > .price').text():
                return {
                    "url": response.url,
                    "title": response.doc('.apphub_AppName').text(),
                    "developer": response.doc('#developers_list > a').text(),
                    "score": response.doc('.high').text(),
                    "overall_Reviews": response.doc('#review_histogram_rollup_section span.game_review_summary').text(),
                    "price": response.doc('.game_purchase_action > div > .price').text().split(' ')[1].replace(',','.'),
                    "release_date": response.doc('.date').text(),
                    "genre": response.doc('.underlined_links a').text().split(' ')[0]
                }
            elif response.doc('.discount_final_price').text():
                return {
                    "url": response.url,
                    "title": response.doc('.apphub_AppName').text(),
                    "developer": response.doc('#developers_list > a').text(),
                    "score": response.doc('.high').text(),
                    "overall_Reviews": response.doc('#review_histogram_rollup_section span.game_review_summary').text(),
                    "price": response.doc('.discount_final_price').text().split(' ')[1].replace(',','.'),
                    "release_date": response.doc('.date').text(),
                    "genre": response.doc('.underlined_links a').text().split(' ')[0]
                }
            else:
                return {
                    "url": response.url,
                    "title": response.doc('.apphub_AppName').text(),
                    "developer": response.doc('#developers_list > a').text(),
                    "score": response.doc('.high').text(),
                    "overall_Reviews": response.doc('#review_histogram_rollup_section span.game_review_summary').text(),
                    "price": 'None',
                    "release_date": response.doc('.date').text(),
                    "genre": response.doc('.underlined_links a').text().split(' ')[0]
                }
        
    #iterates over steam's main page (no tags)
    #that will take a while...
    def index_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            if re.match("http://store.steampowered.com/app/\d+/\w+", each.attr.href):
                self.crawl(each.attr.href, callback=self.filter_page)
        #next index page
        cont = 0
        for each in response.doc('.search_pagination_right > a.pagebtn').items():
            cont += 1
        s = response.url.split('page=')
        url = s[0] + 'page=' + str(int(s[1]) + 1)
        
        if response.url == 'http://store.steampowered.com/search/?tags='+ tag +'&page=1'or cont > 1:
                self.crawl(url, callback=self.index_page)
        