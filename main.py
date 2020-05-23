import time,sys,argparse,datetime,os.path
from huepy import *
from concurrent.futures import ThreadPoolExecutor,wait,as_completed
from src.utitlis import req as request,get_old_data,update_file,Compare_and_add,collect,output_save,date_stamp

parser = argparse.ArgumentParser(description='This is a monitoring tool, it checks for any change in website')
parser.add_argument('-f', action="store",dest="file",help="file containing urls to monitor")
parser.add_argument('-t', action="store",dest="threads",default=20, help="No. of threads", type=int,)
parser.add_argument('-o', action="store",dest="output",default="./", help="Directory in which output should be saved")
input = parser.parse_args()

start_time = time.time()
diff=[]

url_file_path = input.file
thread = input.threads
outDir = input.output
print(thread,outDir)
output_file_name = os.path.join(outDir, "output.html")
print(output_file_name)
# fetch old data from data.json
data= get_old_data()
futures,html=[],""
urls = open(url_file_path).read().split('\n')
print(f'{green("[~]")} Read All Urls Successfully')

executor = ThreadPoolExecutor(max_workers=thread)
futures = [executor.submit(collect,url,data,diff) for url in urls]
print(f'{green("[~]")} Fetching Urls')

for future in as_completed(futures):
    [data,diff] = future.result()
print(f'{green("[~]")} Storing Data And Trying To Find Difference')

header = f'{(data.get("date") or [datetime.datetime.now().strftime("%x")])[-1]} - {datetime.datetime.now().strftime("%x")}'
data = date_stamp(data)
update_file(data)
print(f'{green("[~]")} Creating HTML File ...')

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

if html:
    output_save(html,header,output_file_name)
print(f'{green("[~]")} Done.')


print("--- %s seconds ---" % (time.time()-start_time))
