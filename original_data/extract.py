import concurrent.futures
import json
import os
from typing import List, Dict
from openai import OpenAI
import re
from datetime import datetime
import asyncio

client = OpenAI(
    api_key = "sk-a7e894f3de444345913448c536bebfd4",    
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

path = "./../datasets/processed_text/coliee/fact.json"
crime_chosen = "./../datasets/coliee2025_5000"

files = os.listdir(crime_chosen)

with open("./crime_type.json","r")as f:
    corres = json.load(f)
    f.close()
inverse = {}
for ct in corres:
    for cn in corres[ct]:
        inverse[cn] = ct
with open("./attr_chosen.json","r")as f:
    attr_ch = json.load(f)
    f.close()
path_to = "./../datasets/coliee_ext"

def fun(case,data):
    # if is_file_empty(os.path.join(path_to,case+".json")):
    if not os.path.exists(os.path.join(path_to,case+".json")):
        if case+".json" in files:
            prompt1 = """ the main crime of case """+case+""" are ."""+str(data[case])+"."
            for crime in data[case]:
                prompt1 += "The crime type of "+ crime + "is " +inverse[crime]+". The Attributes of this crime can include the following:"+ str(attr_ch[inverse[crime]])+"."
            prompt1+="Extract the attributes from the crime description and return the results in JSON format. The JSON should include attribute names and values. Like following, "+"""{ 
    "Case ID": "", [{ """
            for crime in data[case]:
                prompt1+="""
    "Crime_Name": ["""+crime+"""],
    "Crime_Type":["""+inverse[crime]+"""],
    "Attribute_Name1": [], 
    "Attribute_Name2": [], 
    "Attribute_Name3": [],
    "Attribute_Name4": [], 
    "Attribute_Name5": []
    },"""
            prompt1 = prompt1[:-1]
            prompt1+="""]}
            please return only the json with standard format, without ```json``` or ellipsis '...'"""
        # print(prompt1)
        print(case+".json")
        response = client.chat.completions.create(
                    model="qwen-plus",
                    messages=[
                        {"role": "system", "content": "You are a legal assistant"},
                        {"role": "user", "content": prompt1},
                    ],
                    temperature=0.3,
                    stream=False
                )
        res1 = response.choices[0].message.content
        print(res1)
        res1 = json.loads(res1)
        print("62**",res1)
        return res1
    return None
    

with open(path,"r")as f:
    data = json.load(f)
    for case in data:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            try:
                ret = executor.submit(fun, case, data).result()
                if ret is not None:
                    with open(os.path.join(path_to,case+".json"),"w",encoding='utf-8')as f:
                                json.dump(ret, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print("error",e)
                pass

