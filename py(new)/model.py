#!/usr/bin/env python
# coding: utf-8

from weather import getWeather
from javaCommunicator import returnProbabilitieVector, returnMostLikely
from getMostSimilarTag import getMostSimilarTag, returnClosestLocations
from googleMap import renderMap


from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer 
stemmer = PorterStemmer()
from nltk.tag.stanford import StanfordNERTagger

from spacy import load
nlp_small = load('en_core_web_sm',disable=["ner"])
from spacy.symbols import VERB


# In[6]:

import re
from calendar import month_name
from difflib import get_close_matches
from datetime import datetime, time
import operator


def main(cached_models):
	def show_train_res(corpus, model='english.muc.7class.distsim.crf.ser'):
		jar = '../stnf/stanford-ner.jar'
		ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')
		words = word_tokenize(corpus)
		return ner_tagger.tag(words)


	def find_date_re(string):
		for delim in ["/","-","."]:
			date = re.search(r'\d{{2}}{delim}\d{{2}}'.format(delim=delim), string)
			if date:
				return date, delim
		return None, None


	def find_date(sent, model="english.muc.7class.distsim.crf.ser"):
		"""
		sent is being modyfied to strip off the words that are already marked as date
		"""
		while True:
			ents = show_train_res(sent, model)
			date = " ".join([ent[0] for ent in ents if ent[1]=="DATE"])

			if date and not re.search(r'\d', date): # we parsed month but not day
				windowOf2 = " ".join([word for inx,word in enumerate(sent.split(" ")) if abs(inx - sent.split(" ").index(date)) < 3 and word != date])
				day = re.search(r"\d{2}|\d{1}", windowOf2)
				sent = sent if " " not in sent else sent.replace(date,"")
				while not day: # no day was actually there
					day = re.search(r"\d{2}|\d{1}",input("Please specify your visit day"))
				date = datetime.strptime(str(day.group())+" " + date+" " + "2019","%d %B %Y")
				return date, sent
			else:
				date, delim = find_date_re(sent)
				if date:
					sent = sent if " " not in sent else sent.replace(date.group(),"")
					date = datetime.strptime(date.group() + delim+"2019",f"%d{delim}%m{delim}%Y")
					return date, sent


			pVect = returnProbabilitieVector(sent, model)
			month = returnMostLikely(pVect, "DATE")
			windowOf2 = " ".join([word for inx,word in enumerate(sent.split(" ")) if abs(inx - sent.split(" ").index(month)) < 3 and word != month])
			day = re.search(r"\d{2}|\d{1}", windowOf2)
			try:
				month = get_close_matches(month, month_name)[0]
				sent = sent if " " not in sent else sent.replace(month,"")
				date = datetime.strptime(str(day.group())+" " + month+" " + "2019","%d %B %Y")
				return date, sent
			except:
				sent = input("Try typing date once again\n")


	def find_location(sent,model="english.muc.7class.distsim.crf.ser"):
		ents = show_train_res(sent, model)
		loc = " ".join([ent[0] for ent in ents if ent[1]=="LOCATION"])
		if not loc:
			pVect = returnProbabilitieVector(sent, model)
			loc = returnMostLikely(pVect, "LOCATION")
		return loc


	model = "english.muc.7class.distsim.crf.ser"#"dummy-ner-model.ser.gz"

	loc_dat =  "I wanna go to California on 30/08"#input("Where and when are u planing to go?\n")#
	activity = "sleep"#input("And what are going to do there?\n")#"I'm going to meet friends and have a tasty burger with them"
	#ents_act = show_train_res(activity, model)

	date, loc_dat = find_date(loc_dat)
	loc = find_location(loc_dat)
	#act = " ".join([ent[0] for ent in ents_act if ent[1]=="ACTIVITY"])

	# if not act and model != "english.muc.7class.distsim.crf.ser": finish when got data for ner model
	#     pVect = returnProbabilitieVector(activity, model)
	#     act = returnMostLikely(vect, "ACTIVITY")


	act = None # for now
	try:
		if abs(datetime.now().day - date.day) < 5:
				getWeather(loc, date)
				time_ = list(map(int,(input("specify your outdoor hours, if you desire, or just press Enter to skip\n") or "0:0").split(":")))
				if all(time_):
					t = time(time_[0],time_[1],0)
					date = datetime.combine(date, t)
				weather_dict = getWeather(loc, date)
				print("It will rain at that time") if weather_dict["rain"] else print("It wont be rainy that time")
				print("Snow will fall at that time") if weather_dict["snow"] else print("It wont be snowy that time")
				print(f"Temperature is {weather_dict['temp_cel']} celsius or {weather_dict['temp_fahr']} fahrenheit")
		elif abs(datetime.now().day - date.day) < 14:
				weather_dict = getWeather(loc, date)
				print(f"At that day maximum temparature is {weather_dict['temp_celsius_max']} celsius or {weather_dict['temp_fahr_max']} fahrenheit") 
				print(f"At that day minimum temparature is {weather_dict['temp_celsius_min']} celsius or {weather_dict['temp_fahr_min']} fahrenheit")
	except IndexError:
		pass


	if not act:
		doc = nlp_small(activity)
		acts = {}
		if len(doc) == 1:
			acts.update({doc.text:[doc.text]})
		for possible_act in doc:
			if possible_act.pos == VERB:
				children = [child.text for child in possible_act.children if not child.is_stop and child.pos_ == "NOUN"]
				children = children if children else possible_act
				if possible_act.text not in acts.keys():
					acts.update({possible_act.text: children})
				else:
					acts[possible_act.text].append(children)

	if not acts:
		acts.update({"visit":[loc]})

	
	print(f"Read location is {loc}, date {date}, action - {acts}")

	tags = {}
	for pos_act in acts.keys():
		resulted_tag = getMostSimilarTag([" ".join([stemmer.stem(word) for word in acts[pos_act]])], cached_models)
		most_likely_tag = max(resulted_tag.items(), key=operator.itemgetter(1))
		tags.update({pos_act+" "+" ".join(acts[pos_act]):[most_likely_tag[0], most_likely_tag[1]]})
		 
	max_like_tag = max(tags)

	print(f"For action - {max_like_tag} the closest tag match is {tags[max_like_tag][0]} with similarity {tags[max_like_tag][1]}")
	places = returnClosestLocations(tags[max_like_tag][0])
	print(f"Closest places to visit are {places} \n")

	place_num = 1#int(input("Which place would u like to choose? 1/2/3"))
	typeOfMov = "driving"#input("driving, walking or bycycling")
	#print(places[place_num])
	renderMap("34.0472711523094,-118.360213975157",str(places[place_num][2])+","+str(places[place_num][1]), typeOfMov)
