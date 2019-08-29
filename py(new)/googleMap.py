from requests import get
from selenium import webdriver
import os
os.environ["LANG"] = "en_US.UTF-8"

def renderMap(start_loc, end_loc, mode):
	request = (f"https://www.google.com/maps/dir/?api=1&origin={start_loc}&destination={end_loc}&travelmode=bicycling")

	driver = webdriver.Chrome("/home/valery/Documents/chromedriver")
	driver.get(request)
	#print (driver.page_source.encode('utf-8'))
	# driver.quit()
	# display.stop()