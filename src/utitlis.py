import base64,json,datetime
import requests,os
from urllib3.exceptions import InsecureRequestWarning

## supress ssl WARNING
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
        response = requests.get(u, allow_redirects=False, verify=False)
        prop['code'] = [response.status_code]
        prop['length'] = [len(response.text)]
        prop['lines'] = [len(response.text.split('\n'))]
        prop['words'] = [len(response.text.split(' '))]
        prop['location'] = [response.headers.get('Location')]
        db[u] = prop
    except requests.exceptions.Timeout:
        print(f'{u} Timeout')
    except requests.exceptions.RequestException as e:
        print(f'{u} is Not reachable')

    return db


# read data.json
def get_old_data(data_json_path,data={}):
    if not os.path.exists(data_json_path):
        f=open(data_json_path, "w+")
        f.write("{}")
    else:
        with open(data_json_path, 'r') as json_file:
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
    if temp.get('url'): diff.append(temp)
    return [data,diff]

# update the data.json with new date
def update_file(data_json_path,data):
    with open(data_json_path, "w") as jsonFile:
        json.dump(data, jsonFile)

# create `output.html` from `template.html` and `diff data`
def output_save(html,header,name="./output.html"):
    template_file = os.path.join(os.path.dirname(__file__), 'template.html')
    with open(template_file, 'r') as template:
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

def not_empty(value):
    return value != ""