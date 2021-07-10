import os
import sys


if len(sys.argv) >1:
    root_dir = sys.argv[1]
else:
    root_dir="E:\sxoli\ptuxiakh\IKEA-Dataset-master\IKEA-Dataset-master"

print("root directory=",root_dir)
duplicate_items=0
all_items=0
duplicate_check=[]
items_with_info=0
replacements={}

file=open("class_names.txt","r")
replacement_lines=file.readlines()
for replacement in replacement_lines:
    if not replacement.startswith("#") and len(replacement)>0:
        temp=replacement.rsplit("|",1)
        replacements["".join(temp[0].split())]="".join(temp[1].split())
file.close()


parsed=[]
classes=[]
classes_items={}
for root,dirs,files in os.walk(root_dir):
    for dir in dirs:
        classes.append(dir.strip().replace(" ",""))
        classes_items[dir.strip().replace(" ","")]=[]
for root,dirs,files in os.walk(root_dir):
    for file in files:
        if file.endswith(".jpg") or file.endswith(".txt") or file.endswith(".TXT"):
            if file.endswith(".jpg"):
                all_items+=1
                if file not in duplicate_check:
                    duplicate_check.append(file)
                else:
                    duplicate_items+=1
            filepath=os.path.join(root,file)
            t=filepath.rsplit("\\",2)
            current_class=t[-2].strip().replace(" ","")
            if current_class in classes_items.keys():
                classes_items[current_class].append(filepath)
            else:
                classes_items[current_class]=[]
temp={}
for key in classes_items.keys():
    if len(classes_items[key])>0:
        temp[key]=classes_items[key]
classes_items=temp
item_class={}


item_characteristics={}
info_found=0
info_not_found=0
for key in classes_items.keys():

    items=classes_items[key]
    txt_filepath=items[-1]
    if not txt_filepath.endswith(".txt") or not txt_filepath.endswith(".TXT"):
        for i in range(len(items)):
            if items[i].endswith(".txt") or items[i].endswith(".TXT"):
                txt_filepath=items[i]
                pos=i
        items.remove(items[pos])
    else:
        items=items[:-1]

    for item in range(len(items)):
        items[item]=items[item].rsplit("\\",1)[-1]
        items[item]=items[item].rsplit(".",1)[0]

    for i in range(len(items)):
        item=items[i]
        if item in item_class.keys():
            item_class[item+"_alt"]=key
            items[i]=item+"_alt"
        else:
            item_class[item]=key
    txt_file=open(txt_filepath)
    lines=txt_file.readlines()
    lines_=[]
    for line in lines:
        if not line=="\n":
            lines_.append(line.strip())
    is_found=False
    not_found=[]
    for item in items:
        not_found.append(item)
    for i in range(len(lines_)):
        lines_[i]=lines_[i].strip()
        for id in items:
            if id.rsplit("_alt",1)[0]==lines_[i]:
                is_found=True
                pos=i+1
                info_found+=1
                if "Package" not in lines_[pos]:
                    width="0"
                    length="0"
                    split_line=lines_[pos].split(" ")
                    for k in range(len(split_line)):
                        if split_line[k]=="Width:":
                            width=split_line[k+1]
                        if split_line[k]=="Length:":
                            length=split_line[k+1]
                    if width!="0" or length!="0":
                        items_with_info+=1
                        item_characteristics[id]=[length,width]
                    if id in not_found:
                        not_found.remove(id)

    for item in not_found:
        info_not_found+=1
        width="0"
        length="0"
        item_characteristics[item]=[length,width]

print("found info for",info_found)
print("didn't find info for",info_not_found)

f=open("base_ontology.owl","r")
lines=f.readlines()
f.close()
f=open("new_ontology.owl","w")
for line in lines:
    if not "</rdf:RDF>" in line:
        f.write(line)


for ph_id in item_characteristics.keys():
        class_=str(item_class[ph_id])
        if item_characteristics.get(ph_id)[0]=="0" and item_characteristics.get(ph_id)[1]=="0":
            f.write("<"+str(replacements[class_])+ ' rdf:ID="_'+str(ph_id).rsplit("_alt",1)[0]+'"/>'+"\n")
        else:
            f.write("<"+str(replacements[class_])+ ' rdf:ID="_'+str(ph_id).rsplit("_alt",1)[0]+'">'+"\n")
            if not item_characteristics.get(ph_id)[0]=="0":
                f.write('<hasLength rdf:datatype="http://www.w3.org/2001/XMLSchema#float"'+"\n"+
                ">"+str(item_characteristics.get(ph_id)[0])+"</hasLength>"+"\n")
            if not item_characteristics.get(ph_id)[1]=="0":
                f.write('<hasWidth rdf:datatype="http://www.w3.org/2001/XMLSchema#float"'+"\n"+
                ">"+str(item_characteristics.get(ph_id)[1])+"</hasWidth>"+"\n")
            f.write("</"+str(replacements[class_])+">"+"\n")
f.write(
"""
 </rdf:RDF>""")

f.close()
print("finished")
print("all items are",all_items)
print("found",duplicate_items,"duplicates")
print("found info for",items_with_info,"items")
print("duplicates are",duplicate_items/all_items*100,"%")
print("items with info are",items_with_info/(all_items-duplicate_items)*100,"%")










#
