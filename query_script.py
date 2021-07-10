import rdflib
from rdflib import Graph
import rdflib.plugins.sparql as sparql
import rdfextras
from rdflib.namespace import RDFS
from rdflib.namespace import RDF
from rdflib import URIRef
from os import walk
import os
from PIL import Image
from nltk.corpus import wordnet as wn
import requests
from cleaningCN import *
from mainCN import *
import re

f=open("new_ontology.owl","r")
lines=f.readlines()
uri_root=""
for line in lines:
    if "xml:base" in line:
        l=line.rsplit("=",1)[-1]
        l=l.replace('"',"")
        l=l.replace(">","")
        l=l.strip()
        l=l.replace(" ","")
        uri_root=l



root_folder="E:\sxoli\ptuxiakh\IKEA-Dataset-master\IKEA-Dataset-master"
g = Graph()
g.parse('E:/sxoli/ptuxiakh/script/new_ontology.owl')
print("STARTING")


hierarchy=[]
current_class="IKEA"
done=False
class_uri=URIRef(uri_root+"#"+current_class)
class_uris=[]
stopped=False
stopped_class=""
while not done:
    current_classes=[]
    for class_,subj, obj in g.triples((None,RDFS.subClassOf,class_uri)):
        current_classes.append(class_.rsplit("#",1)[-1])
    if len(current_classes)>0:
        print("currect class is",current_class)
        for i in range(len(current_classes)):
            print(str(i+1)+"."+current_classes[i])
        choice=0
        while choice>len(current_classes) or choice<1:
            choice=input("choose class between 1 and "+str(len(current_classes))+
            " or input stop to get info for all items bellow current class ")
            try:
                if not choice=="stop":
                    choice=int(choice)
                    current_class=current_classes[choice-1]
                    hierarchy.append(current_class)
                    class_uri=URIRef(uri_root+"#"+current_class)
                else:
                    stopped=True
                    stopped_class=current_class
                    done=True
                    break
            except:
                print("input must be an integer or word stop")
                choice=0
    else:
        done=True

print("HIERARCHY IS",hierarchy)

if stopped:
    target_class=stopped_class
else:
    target_class=hierarchy[-1]




print("target class is",target_class)
class_uri=uri_root+"#"+target_class
class_uri=URIRef(class_uri)
class_items=[]
only_info=False


choice=input("show only instances that contain info for length or width?[y/n]")
choice=choice.lower()
while choice!="y" and choice!="n":
    choice=input("show only instances that contain info for length or width?[y/n]")
    choice=choice.lower()
if choice=="y":
    only_info=True

queries=[]
if only_info:
    choice=input("do you want to filter results based on length or width?[y/n]")
    choice=choice.lower()
    while choice!="y" and choice!="n":
        choice=input("do you want to filter results based on length or width?[y/n]")
        choice=choice.lower()
    filter_width=""
    filter_length=""
    if choice=="y":
        found=False
        while not found:
            f=input("select filter for width,must be in format >x or <x leave blank to not filter ")
            if not f=="":
                r=re.search('(>{1}|<{1}){1}(\d*){1}',f)
                try:
                    if len(r.group(2))>0 and len(r.group(1))>0:
                        filter_width=r.group(0)
                        found=True
                except:
                    continue
            else:
                found=True
                filter_width=""
        found=False
        while not found:
            f=input("select filter for length,must be in format >x or <x leave blank to not filter ")
            if not f=="":
                r=re.search('(>{1}|<{1}){1}(\d*){1}',f)
                try:
                    if len(r.group(2))>0 and len(r.group(1))>0:
                        filter_length=r.group(0)
                        found=True
                except:
                    continue
            else:
                filter_length=""
                found=True

    if not filter_length=="" and not filter_width=="":
        query1="""
        select ?item ?b
        where {
        ?item rdf:type ?b .
        ?b rdfs:subClassOf* ?class .
        ?item :hasWidth ?width .
        ?item :hasLength ?length .
        filter(?length """+filter_length+""" && ?width """+filter_width+""")
        }
        """
        queries.append(query1)
    elif not filter_length=="" and filter_width=="":
        query1="""
        select ?item ?b
        where {
        ?item rdf:type ?b .
        ?b rdfs:subClassOf* ?class .
        ?item :hasLength ?value .
        filter(?value""" +filter_length+""")
        }
        """
        queries.append(query1)
    elif filter_length=="" and not filter_width=="":
        query1="""
        select ?item ?b
        where {
        ?item rdf:type ?b .
        ?b rdfs:subClassOf* ?class .
        ?item :hasWidth ?value .
        filter(?value""" +filter_width+""")
        }
        """
        queries.append(query1)
    elif filter_length=="" and filter_width=="":
        query1="""
        select ?item ?b
        where {
        {
        ?item rdf:type ?b .
        ?b rdfs:subClassOf* ?class .
        ?item :hasWidth ?value .
        }
        UNION
        {
        ?item rdf:type ?b .
        ?b rdfs:subClassOf* ?class .
        ?item :hasLength ?value .
        }
        }
        """
        queries.append(query1)
else:
    query1="""
    select ?item ?b
    where {
    ?item rdf:type ?b .
    ?b rdfs:subClassOf* ?class .

    }
    """
    queries.append(query1)


for query in queries:
    results = g.query(query,initBindings={'class': URIRef(uri_root+"#"+target_class)})
    for x in results:
        if str(x[0]).rsplit("#",1)[-1].replace("_","") not in class_items:
            class_items.append( ( str(x[0]).rsplit("#",1)[-1].replace("_",""), str(x[1]).rsplit("#",1)[-1]) )

if len(class_items)==0:
    print("there are no instances")
else:
    print("items ",class_items)
    print("give a number to choose item")
    choice=-1
    while choice<0 or choice>len(class_items):
        choice=input("choose number between 1 and "+str(len(class_items))+" ")
        try:
            choice=int(choice)-1
        except:
            print("input has to be an integer")
            choice=-1
            continue

    target_item=class_items[choice][0]
    target_class=class_items[choice][1]
    if target_class not in hierarchy:
        hierarchy.append(target_class)
    dataset_root="E:\sxoli\ptuxiakh\IKEA-Dataset-master\IKEA-Dataset-master"



    reverse_replace_file=open("class_names.txt","r")
    replace={}
    all_lines=reverse_replace_file.readlines()
    for line in all_lines:
        if not line.startswith("#"):
            lt=line.split("|")
            lt[1]=lt[1].replace("\n","")
            replace[lt[1]]=[lt[0]]
    if target_class in replace:
        target_class_r=replace[target_class]
    else:
        target_class_r=target_class
    target_class_r=target_class_r[0]
    print("target class is ",target_class_r)
    print("target item is", target_item)
    found_length=False
    item_uri=URIRef(uri_root+"#_"+target_item)
    property_uri=URIRef(uri_root+"#hasLength")
    for item,subj, obj in g.triples((item_uri,property_uri,None)):
        if obj.isdigit():
            item_length=obj
            found_length=True
        else:
            try:
                item_length=float(obj)
                found_length=True
            except:
                continue
    if found_length:
        print("item length=",item_length)
    else:
        print("There's no length info for item",target_item)



    found_width=False
    property_uri=URIRef(uri_root+"#hasWidth")
    for item,subj, obj in g.triples((item_uri,property_uri,None)):
        if obj.isdigit():
            item_width=obj
            found_width=True
        else:
            try:
                item_width=float(obj)
                found_width=True
            except:
                continue
    if found_width:
        print("item width=",item_width)
    else:
        print("There's no width info for item",target_item)


    for dataset_root, dirs , files in os.walk(dataset_root):
        for name in files:
            if name==target_item+".jpg" and target_class_r.replace(" ","") in os.path.join(dataset_root,name).replace(" ",""):
                print(os.path.join(dataset_root,name))
                target_item_path=os.path.join(dataset_root,name)
    image = Image.open(target_item_path)
    image.show()




classes_=[]
syns=[]
have_info=[]
for _class in hierarchy:
    results=wn.synsets(_class)
    if len(results)>0:
        have_info.append(_class.lower())


if len(have_info)>0:
    while len(have_info)>0:
        print("Do you want me to search for information on the Web, for the object class",have_info[0]+"? [y/n]")
        choice=input()
        while choice!="y" and choice!="n":
            print("Do you want me to search for information on the Web, for the object class",have_info[0]+"? [y/n]")
            choice=input()
        if choice=="y":
            print("info for ",have_info[0])
            data1, data2, data3 = cn(have_info[0])
            prp = findSimilarity(data2, data1, [have_info[0]], data3)
            first = prp.cleaning_entities()
            second, weights = prp.cleaning_entities2(first[1], first[0])
            cleaned_weights = prp.grounding(second, weights)
            for key in cleaned_weights.keys():
                extra_inf=cleaned_weights[key]
                if len(extra_inf)>0:
                    if len(extra_inf)>5:
                        extra_inf=extra_inf[:5]
                    print(have_info[0],key.replace("/r/",""),extra_inf)
            have_info=have_info[1:]
        else:
            have_info=have_info[1:]

else:
    print("Sorry I could not find something in the Web")
