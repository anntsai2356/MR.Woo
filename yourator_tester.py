import requests
import json
from urllib.parse import urlencode

# 有多個分類的話，結果會混再一起再用更新日期排序
params = {
    "category[]": "後端工程",
    # "category[]": "全端工程",
    "area[]": "TPE",
    "position[]": "full_time",
    "sort": "recent_updated",
    "page": 1
}
url = "https://www.yourator.co/api/v2/jobs?" + urlencode(params)

response = requests.get(url)

response.encoding = 'utf-8'
decoded_content = response.content.decode(response.encoding)
data = json.loads(decoded_content)
print(data)

# job_list = data['jobs']

# # print(job_list)

# for x in job_list:
#     print("title: "+ x['name'], "company: "+ x['company']['brand'])