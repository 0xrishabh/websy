import base64,json,datetime
import requests
from huepy import *
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def collect(url,data,diff):
    if url:
        re = req(url)
        if data.get(url):
            [data,diff] = Compare_and_add(data,re,url,diff)
        else:
            # this adds the "re" object to the json file
            data.update(re)
    return [data,diff]

# request url and create json object with different properties
def req(u):
    db,prop={},{}
    try:
        rq = requests.get(u, allow_redirects=False, verify=False)
        print(run(italic(f'Requesting {u}')))
        prop['code'] = [rq.status_code]
        prop['length'] = [len(rq.text)]
        prop['lines'] = [len(rq.text.split('\n'))]
        prop['words'] = [len(rq.text.split(' '))]
        prop['location'] = [rq.headers.get('Location')]
        db[rq.url] = prop
    except requests.exceptions.Timeout:
        print(bad(f'{u} Timeout'))
    except requests.exceptions.RequestException as e:
        print(bad(f'{u} is Not reachable'))

    return db


# read data.json
def get_old_data(data={}):
    with open('data.json', 'r') as json_file:
        data = json.load(json_file)
    return data

# compare data[url] json with req[url], add to the data.json and diff
def Compare_and_add(data,req,url,diff):
    temp={}
    for prop in data[url].keys():
        old,new=data[url][prop],req[url][prop]
        if old[-1]!=new[0]:
            temp['url'] = url
            if prop != "location" and prop != "code":
                temp[prop] = abs(int(old[-1])-int(new[0]))
            else:
                temp[prop] = f'{(old[-1] or 0)} --> {(new[0] or 0)}'
        data[url][prop].append(req[url][prop][0])
    if temp!={} and temp.get('url'): diff.append(temp)
    return [data,diff]

# update the data.json with new date
def update_file(data):
    with open("data.json", "w") as jsonFile:
        json.dump(data, jsonFile)

# create `output.html` from `template.html` and `diff data`
def output_save(html,header,name="./output.html"):
    with open('src/template.html', 'r') as template:
        result = template.read()
        result = result.replace("FILL_WITH_DIFF_RESULT",html)
        result = result.replace("HEADER",header)
    f = open(name,"w")
    f.write(result)
    f.close()

# Add today's date in data.json
def date_stamp(data):
    today=datetime.datetime.now().strftime("%x")
    if data.get('date'):
        data['date'].append(today)
    else:
        data['date'] = [today]
    return data
