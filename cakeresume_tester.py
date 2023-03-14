import requests
import json
from urllib.parse import urlencode

params = {
    "x-algolia-agent": "Algolia for JavaScript (4.14.2); Browser (lite); instantsearch.js (4.49.1); react (18.2.0); react-instantsearch (6.38.1); react-instantsearch-hooks (6.38.1); JS Helper (3.11.1)",
    "x-algolia-api-key": "OTQ1MjI1MmYwNmM0YmQ0MjIxMTZhNzM1NWNhZGQ0YzQ5OGM2Y2I5NzQ1ZTM1MjViMTMyMTE0NTk3MTZkODI2NHZhbGlkVW50aWw9MTY3OTMwODQ5NSZyZXN0cmljdEluZGljZXM9Sm9iJTJDSm9iX29yZGVyX2J5X2NvbnRlbnRfdXBkYXRlZF9hdCUyQ0pvYl9wbGF5Z3JvdW5kJTJDUGFnZSUyQ1BhZ2Vfb3JkZXJfYnlfY29udGVudF91cGRhdGVkX2F0JmZpbHRlcnM9YWFzbV9zdGF0ZSUzQSslMjJjcmVhdGVkJTIyK0FORCtub2luZGV4JTNBK2ZhbHNlJmhpdHNQZXJQYWdlPTEwJmF0dHJpYnV0ZXNUb1NuaXBwZXQ9JTVCJTIyZGVzY3JpcHRpb25fcGxhaW5fdGV4dCUzQTgwJTIyJTVEJmhpZ2hsaWdodFByZVRhZz0lM0NtYXJrJTNFJmhpZ2hsaWdodFBvc3RUYWc9JTNDJTJGbWFyayUzRQ==",
    "x-algolia-application-id": "966RG9M3EK",
}
url = "https://966rg9m3ek-dsn.algolia.net/1/indexes/*/queries?" + urlencode(params)

search_json = {
    "requests": [
        {
            "indexName": "Job",
            "params": "clickAnalytics=true&distinct=false&enablePersonalization=true&facets=%5B%22location_list%22%2C%22profession%22%2C%22job_type%22%2C%22seniority_level%22%2C%22salary_range%22%2C%22remote%22%2C%22year_of_seniority%22%2C%22number_of_management%22%2C%22page.number_of_employees%22%2C%22page.sector%22%2C%22page.tech_labels%22%2C%22lang_name%22%2C%22salary_type%22%2C%22salary_currency%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&maxValuesPerFacet=500&page=0&query=php&tagFilters=&userToken=39196",
        }
    ]
}
response = requests.post(url, json=search_json)

response.encoding = 'utf-8'
decoded_content = response.content.decode(response.encoding)
json_data = json.loads(decoded_content)
print(json_data)