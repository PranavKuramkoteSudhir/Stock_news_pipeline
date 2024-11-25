import os
import requests

# If you exported as API_KEY, use:
print(os.getenv('API_KEY'))


API_TOKEN =(os.getenv('API_KEY'))

BASE_URL = "https://api.marketaux.com/v1/news/all"

params = {

    "symbols": "TSLA,AMZN,MSFT", # You can modify this list of symbols as needed

    "filter_entities": "true",

    "language": "en",

    "limit": 10, # This parameter requests the 10 most recent articles

    "api_token": API_TOKEN

}

response = requests.get(BASE_URL, params=params)

if response.status_code == 200:

    news_data = response.json()

    # Process the news_data here

    for article in news_data['data']:

        print(f"Title: {article['title']}")

        print(f"Published at: {article['published_at']}")

        print(f"Source: {article['source']}")

        print(f"Description: {article['description']}")

        print(f"Keywords: {article['keywords']}")

        print(f"URL: {article['url']}")

        print(f"Name: {article['entities'][0]['name']}")

        print("---")

else:

    print(f"Error: {response.status_code}")

    print(response.text)
    # Not these:
    # print(os.getenv('Api_key'))
    # print(os.getenv('api_key'))