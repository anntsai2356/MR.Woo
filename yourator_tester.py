import requests
from urllib.parse import urlencode

params = {
    "category[]": "後端工程",
    "category[]": "全端工程",
    "area[]": "TPE",
    "position[]": "full_time",
    "sort": "recent_updated",
}
url = "https://www.yourator.co/api/v2/jobs?" + urlencode(params)

request = requests.get(url)

print(request.text)