#!/usr/bin/env python
# coding: utf-8

# In[1]:


from nltk.stem import WordNetLemmatizer 
lemmatizer = WordNetLemmatizer()
from spacy import load
nlp = load('en_core_web_lg', disable=["ner","tagger","parser"])

import os
import pandas as pd
from ast import literal_eval
import operator
from scipy.spatial.distance import euclidean

import warnings
from gensim.models import FastText, KeyedVectors



def getMostSimilarTag(user_input, models):
    tags_dict = {'food': {'french', 'meat', 'cafes_coffee', 'steakhouse', 'fast_food', 'sushi', 
    'pizza', 'restaurant', 'american', 'italian', 'international', 'diner', 'mexican', 
    'vegetarian', 'asian', 'thai', 'seafood', 'chinese', 'indian'}, 
    'shopping': {'toy', 'department_store', 'antiques', 'fashion', 'gift'}, 
    'nightlife': {'night_club', 'jazz_cafe', 'bar', 'lounge'}, 
    'museums': {'art', 'planetarium', 'science', 'history', 'gallery'}, 
    'sightseeings': {'religious_site', 'historic_site', 'memorial_monument'},
     'nature': {'zoo_aquarium', 'park'}}
    clean_tags = {tag:[name  if "_" not in name else "coffee" if name == "cafes_coffee" else name[:name.index("_")] 
                                for name in tags_dict[tag]] for tag in tags_dict.keys()}
    warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim.models')
    google_model = models[0]
    wikipedia_model = models[1]
    answer = {tag:0 for tag in clean_tags.keys()}
    google_res, wiki_res, spacy_res = dict(), dict(), dict()

    for noun in user_input: #firstly choose the tag categorie
        g = google_model.wv
        w = wikipedia_model.wv
        for tag in clean_tags.keys():
            try:
                simil = google_model.similarity(noun, tag)
            except KeyError:
                simil = 0

            google_res.update({tag:simil})


            doc = nlp(noun)
            doc2 = nlp(tag)
            simil = doc[0].similarity(doc2[0])
            spacy_res.update({tag:simil})
            
            try:
                simil = wikipedia_model.similarity(noun, tag)
            except KeyError:
                simil = 0

            wiki_res.update({tag:simil})

        google_answer = max(google_res.items(), key=operator.itemgetter(1))
        answer[google_answer[0]] += 1

        spacy_answer = max(spacy_res.items(), key=operator.itemgetter(1))
        answer[spacy_answer[0]] += 1

        wiki_answer = max(wiki_res.items(), key=operator.itemgetter(1))
        answer[wiki_answer[0]] += 1

        

    most_likely_tag = max(answer.items(), key=operator.itemgetter(1))[0] #than concreete tag type
    doc = nlp(most_likely_tag)
    final_res = dict()
    for word in clean_tags[most_likely_tag]:
        doc2 = nlp(word)
        final_res.update({most_likely_tag+":"+word:doc2[0].similarity(doc[0])})
    #print(final_res)
    
    return final_res


# In[5]:


# getMostSimilarTag(["meet friends"])




def returnClosestLocations(tagName, currentLocation = [-118.360213975157, 34.0472711523094], limit = 3):
    places_list, min_dist_places = list(), list()
    for file in os.listdir("../tags"):
        if file.endswith(".xlsx"):
            df = pd.read_excel("~/Programs/jupyterEnvironments/sentimentalAnalysis/sentimental/StangordNER/tags/" + file)
            for i in range(df.shape[0]):
                row = df.iloc[i]
                categorie_list = literal_eval(row.loc["categories"])
                clean_categorie_list = [name  if "_" not in name else "food:coffee" if name == "food:cafes_coffee" else name[:name.index("_")]
                                       for name in categorie_list]
                if tagName in clean_categorie_list:
                    if pd.notna(float(row.loc["lon"])) and pd.notna(float(row.loc["lat"])):
                        places_list.append([row.loc["_source/name"],float(row.loc["lon"]),float(row.loc["lat"])])
           
    for j in range(limit):
        closest = min(places_list, key=lambda x:euclidean(x[1:], currentLocation))
        places_list.remove(closest)
        min_dist_places.append(closest)
    
    #print(min_dist_places)
    return min_dist_places

