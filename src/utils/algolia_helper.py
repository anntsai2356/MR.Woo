import requests
import json
import re


class AlgoliaHelper:
    @staticmethod
    def getCakeresumeToken(url: str) -> dict:
        """
        url : The url is page that use search box.

        There has many keys in cake resume.
        only key_jobs_and_pages is used to search Job index.

        Ex:
        {
            "algolia": {
                "id": "966RG9M3EK",
                "key": "NjNhZ...", (length = 620)
                "key_global_search": "MzA0M2...", (length = 284)
                "key_query_suggestions": "MDliO...", (length = 396)
                "key_users": "ZTZiM...", (length = 360)
                "key_jobs_and_pages": "NDM0O...", (length = 520)
                "key_featured_pages": "ZGUxY...", (length = 312)
                "key_featured_jobs": "NmU1M...", (length = 476)
                "key_published_posts": "ZThhN...", (length = 316)
                "key_organizations": "OTkwZ...", (length = 252)
                "key_activities": "MmYwN...", (length = 244)
                "key_articles": "OThkM...", (length = 292)
                "key_featured_items_tw_user": "MDgyY...", (length = 356)
                "key_featured_items_non_tw_user": "ZDM1Y..." (length = 423)
            }
        }
        """

        result = {"app_id": "", "api_key": ""}

        response = requests.get(url)
        response.encoding = "utf-8"
        decoded_content = response.content.decode(response.encoding)

        match = re.search('("algolia"?):{(.+?)}', decoded_content).group()
        match = "{" + match + "}"
        info = json.loads(match.replace("'", '"'))

        if not info["algolia"]["id"] and not info["algolia"]["key_jobs_and_pages"]:
            print(f"WARN: Could not find algolia keys in {url}.")
            return result

        result["app_id"] = info["algolia"]["id"]
        result["api_key"] = info["algolia"]["key_jobs_and_pages"]

        return result


if __name__ == "__main__":
    url = "https://www.cakeresume.com/jobs"
    result = AlgoliaHelper.getCakeresumeToken(url)

    print(result)
