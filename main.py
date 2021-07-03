import time,sys,argparse,datetime,os.path
from progress.bar import Bar
from concurrent.futures import ThreadPoolExecutor,wait,as_completed
from src.utitlis import get_old_data,update_file,collect,output_save,date_stamp,not_empty

parser = argparse.ArgumentParser(description='This is a monitoring tool, it checks for any change in website')
parser.add_argument('-f', action="store",dest="file",help="file containing urls to monitor")
parser.add_argument('-t', action="store",dest="threads",default=20, help="No. of threads", type=int)
parser.add_argument('-o', action="store",dest="output",default="./", help="Directory in which output should be saved")
parser.add_argument('-db', action="store",dest="db",default="./", help="Directory in which db.json should be saved")

input = parser.parse_args()

diff=[]

url_file_path = input.file
thread = input.threads
outDir = input.output
if not url_file_path: raise Exception("Url file not provided") 
output_file_name = os.path.join(outDir, "output.html")
data_json_path= (os.path.join(input.db,'data.json') or os.path.join(os.path.abspath(os.path.dirname(__file__)),'data.json'))

# fetch old data from data.json
data= get_old_data(data_json_path)
futures,html=[],""

try:
    urls = list(filter(not_empty,open(url_file_path).read().split('\n')))
except Exception as e:
    raise e

bar = Bar('Progress', max=len(urls))

executor = ThreadPoolExecutor(max_workers=thread)
futures = [executor.submit(collect,url,data,diff) for url in urls]

for future in as_completed(futures):
    [data,diff] = future.result()
    bar.next()

header = f'{(data.get("date") or [datetime.datetime.now().strftime("%x")])[-1]} - {datetime.datetime.now().strftime("%x")}'
data = date_stamp(data)
update_file(data_json_path,data)

# Constructing output.html with diff data
properties = ["url","code","length", "lines", "words", "location"]
for d in diff:
    html += "<tr>"
    for p in properties:
        val = (d.get(p) or "No Change")
        if val != "No Change" and p!="url":
            html += f'<td class="highlight">{val}</td>'
        else:
            html += f'<td>{val}</td>'
    html += "</tr>"

output_save(html,header,output_file_name)

bar.finish()
