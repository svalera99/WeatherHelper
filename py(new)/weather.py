#!/usr/bin/env python
# coding: utf-8

# In[25]:


from requests import get
from pyowm import OWM
from mechanize import Browser
from bs4 import BeautifulSoup
from selenium import webdriver
from math import floor
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent='myapplication')
from datetime import datetime, time


# In[22]:


def getWeather(location, date):
    """
    [str, datetime] -> dict
    Finish time for more than 5 days
    """
    openWeatherKey = "441128368845c5854135b6a09d13ca66"
    owm = OWM(openWeatherKey) 
    
    weather_dict = dict()
    diff = abs(datetime.now().day - date.day)
    if  diff < 5: #if less than 5 days use open weather api
        fc = owm.three_hours_forecast(location)
        f = fc.get_weather_at(date)
        weather_dict.update({"temp_cel":f.get_temperature(unit="celsius")["temp"]})
        weather_dict.update({"temp_fahr":f.get_temperature(unit="fahrenheit")["temp"]})
        weather_dict.update({"rain": fc.will_be_rainy_at(date)})
        weather_dict.update({"snow": fc.will_be_snowy_at(date)})
 
        #print([func for func in dir(fc) if callable(getattr(fc, func))]) 
        
    elif diff < 14: # else parse bbc weather
        br = Browser()
        bbc_url = "https://www.bbc.com/weather/"
        br.open(bbc_url)
        br.set_handle_robots(False)
        br.addheaders = [("User-agent","Mozilla/5.0")] 
        
        formcount = 0
        for form in br.forms(): # get the number of form to input city name to
            if str(form.attrs["class"]) == "ls-o-form":
                break
            formcount += 1 
            
        br.select_form(nr=formcount-1)
        br.form["s"] = location     
        br.submit()
        url = br.geturl()

        resp = get(url)
        bSoup = BeautifulSoup(resp.content, "html.parser")
        a = bSoup.select(".location-search-results__result__link")[0]
        final_url = bbc_url + a.attrs["href"]

        resp = get(final_url)
        
        bSoup = BeautifulSoup(resp.content, "html.parser")
        temp_li = bSoup.select(f".wr-day--{diff}")[0] 
        
        
        weather_dict.update({"temp_celsius_max":int(temp_li.select(".wr-day-temperature__high")[0].select(".wr-value--temperature--c")[0].contents[0][:-1])})
        weather_dict.update({"temp_fahr_max":int(temp_li.select(".wr-day-temperature__high")[0].select(".wr-value--temperature--f")[0].contents[0][:-1])})
        weather_dict.update({"temp_celsius_min":int(temp_li.select(".wr-day-temperature__low-value")[0].select(".wr-value--temperature--c")[0].contents[0][:-1])})
        weather_dict.update({"temp_fahr_min":int(temp_li.select(".wr-day-temperature__low-value")[0].select(".wr-value--temperature--f")[0].contents[0][:-1])})
        
    return weather_dict
 
        
#getWeather("Kiev",datetime.datetime(2019, 7, 13, 12, 30)) use with time if less than five days 
#getWeather("Kiev,ua",datetime.datetime(2019, 7, 19)) without time if more


# In[ ]:




