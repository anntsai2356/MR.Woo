import requests
import json
from urllib.parse import urlencode

params = {
    "ro": 0,
    "kwop": 7,
    "keyword": "後端工程師",
    "expansionType": "area,spec,com,job,wf,wktm",
    "order": 14,
    "asc": 0,
    "page": 6,
    "mode": "s",
    "jobsource": "2018indexpoc",
    "langFlag": 0,
    "langStatus": 0,
    "recommendJob": 1,
    "hotJob": 1,
}
url = "https://www.104.com.tw/jobs/search/list?" + urlencode(params)

headers ={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
        'Referer': 'https://www.104.com.tw/jobs/search/',
}

response = requests.get(url, headers=headers)

response.encoding = 'utf-8'
decoded_content = response.content.decode(response.encoding)
data = json.loads(decoded_content)

job_list = data['data']['list']

# print(job_list)

for x in job_list:
    print("title: "+ x['jobName'], "company: "+ x['custName'])