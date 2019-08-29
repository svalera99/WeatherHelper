#!/usr/bin/env python
# coding: utf-8

from subprocess import call 



def returnProbabilitieVector(sentence, modelName):
    with open("config.txt","w+") as conf_file:
        conf_file.write(sentence + "\n" + modelName)
        
    call(["java","-cp","../stanford-corenlp-full-2018-10-05/*", "showProbabilities.java"]) # third member - link to folder that contains stanford ner data
    with open("probVect.txt","r+") as res_file:
        results = res_file.read()
    #print(results)

    final_dict = dict()
    splitted = [list(filter(lambda x: x !="",i.split(" "))) for i in [j for j in results.split("\n")]][:-1]
    for word in splitted:
        tmp_dict = {word[i]:word[i+1] for i in range(1,len(word)-1,2)}
        final_dict.update({word[0]:tmp_dict})
    return final_dict



def returnMostLikely(vector, category):
    max_lst = list()
    for key in vector.keys():
        max_lst.append((key,vector[key][category]))
    return max(max_lst, key=lambda x: float(x[1]))[0]



# vect = returnProbabilitieVector("Those were the best days of my life in Lviv", "dummy-ner-model.ser.gz")
# returnMostLikely(vect, "LOC")

