import re 
import requests as r
s=r.session()
def step_2(s,seperator,base=10):
    mapped_range="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"
    numbers=mapped_range[0:base]
    max_iter=0
    for index,value in enumerate(s[::-1]):
        max_iter += int(value if value.isdigit() else 0) * (seperator**index)
    mid = ''
    while max_iter > 0:
        mid = numbers[int(max_iter % base)] + mid
        max_iter = (max_iter - (max_iter % base)) / base
    return mid or '0'


def step_1(data,key,load,seperator):
    payload = ""
    i=0
    seperator=int(seperator)
    load=int(load)
    while i<len(data):
        s=""
        while (data[i]!=key[seperator]):
            s += data[i]
            i += 1
        for index,value in enumerate(key):
            s = s.replace(value,str(index))
        payload += chr(int(step_2(s,seperator,10))-load)
        i  += 1
    payload=re.findall(r'action="([^\"]+)" method="POST"><input type="hidden" name="_token"\s+value="([^\"]+)',payload)[0]
    return payload

def get_dl_link(link:str):
    resp=s.get(link)
    data,key,load,seperator=re.findall(r'\("(\S+)",\d+,"(\S+)",(\d+),(\d+)',resp.text)[0]
    url,token=step_1(data=data,key=key,load=load,seperator=seperator)
    data={"_token":token}
    headers={'referer': link}
    resp=s.post(url=url,data=data,headers=headers,allow_redirects=False)
    return resp.headers["location"]