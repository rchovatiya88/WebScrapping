# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 20:22:55 2017

@author: DELL
"""

###############################################################################################


# Importing libraries
from bs4 import BeautifulSoup as Soup
import urllib, requests, re, pandas as pd

try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar


# Input from csv file

input = pd.read_csv('C:\\Users\\DELL\\Documents\\Artsyjewels\\input.csv')



## Login to MMA silver site to get price info
cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
login_data = urllib.parse.urlencode({"customer[email]": "artsyjewelstore@gmail.com","customer[password]": ""}).encode("utf-8")
opener.open('https://www.mmasilver.com/account/login',login_data)

# MMAsilver.com url
base_url = input.iloc[0,0]
collection = input.iloc[0,1]          # retrieve by collection
page = '?page='    # start page number
pages = int(input.iloc[0,2])
pd.set_option('max_colwidth',500)    # to remove column limit (Otherwise, we'll lose some info)


sku_number = []
title = []
price = []
img_links = []

for pg in range(pages):    
    url = '%s%s%s%d'%(base_url, collection, page, pg)
    resp = opener.open(url)
    target = Soup(resp, "lxml")
    #print(target.prettify())
    targetElements = target.find('div',{"class":"productList row"}) # we're interested in each row (= each job)
    
    item_sku = targetElements.find_all('div', {'class':'item-wrapper'})
    product_title = targetElements.find_all('div', {'class': 'product-title'})
    product_price = targetElements.find_all('span',{'class':'original-price'})
    product_img = targetElements.find_all('div',{'class':'productImage'})
    
    
    #sku_number list creation
    for sku in range(0,len(item_sku),3):   
        sku_number.append(item_sku[sku].find('a').text[9:].replace('\n',''))   
    
    ##  title list
    for t in product_title:
        title.append(t.find('a').text.replace('\n','').replace('\t','')[4:])
    
    #Price list
    for p in range(0,len(product_price),3):
        price.append(product_price[p].text.replace('\n','').replace('\t','').replace('  ',''))
    
    #image list
    for im in product_img:
        img_links.append(im.find('img')['data-src'])

products = '/products/'
large_images = []
description = []  

for i in range(len(sku_number)):
    url = '%s%s%s%s'%(base_url, collection, products, sku_number[i])
    resp_in = opener.open(url)
    target_in = Soup(resp_in, "lxml")
    targ_product_img = target_in.find('div', {'class':'col-sm-6'})
    targ_product_details = target_in.find('div', {'class':'productDetails'})
        
    product_images = targ_product_img.find_all('div', {'class': 'pinch-zoom'})
    
#    for img in product_images:
 #       large_images.append(img.find('img')['src'])
    large_images.append(product_images[0].find('img')['src'])
    product_desc = targ_product_details.find_all('p')
    in_desc = ''
    for desc in product_desc:
        in_desc+=desc.text
    
    description.append(in_desc)


#creating DataFrame
df = pd.DataFrame({'SKU':sku_number, 'Title': title, 'Price': price, 'Image_URL':img_links, 'Description': description, 'img_url_large': large_images})


   
with open('C:\\Users\\DELL\\Documents\\Artsyjewels\\targetElements.txt','w') as file:
    file.write(str(product_images))


#Exporting DataFrame to csv
df.to_csv('C:\\Users\\DELL\\Documents\\Artsyjewels\\data_'+collection+'.csv',index = False)


