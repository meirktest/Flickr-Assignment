import requests
import mysql.connector as mysql
import pandas as pd
from datetime import datetime

api_key='yourApiKey'
flickr_endpoint = "https://www.flickr.com/services/rest/"

def scrape(keyword,size): 
    data_params = {'api_key': api_key,
                   'text':  keyword,
                   'method': 'flickr.photos.search',
                   'media': 'photos',
                   'format': "json",
                   'nojsoncallback': 1
                   }
    result = handle_response(requests.get(url=flickr_endpoint,params=data_params))
    if result:
        images = result['photos']['photo']
        count = 1
        for photo in images:
            if count > size:
                break
            count += 1
            photo_owner = photo['owner']
            photo_id = photo['id']
            url = f"https://www.flickr.com/photos/{photo_owner}/{photo_id}"
            scrapeTime = datetime.now()
            insert_data(url,scrapeTime,keyword)
        print(f"{size} records are inserted")
    else:
        print(result)


def search(minScrapeTime,maxScrapeTime,keyword, size):
    search_result = query_data(minScrapeTime, maxScrapeTime, keyword, size)
    if len(search_result):
        pd.options.display.max_colwidth = 100
        result = pd.DataFrame(search_result)
        result.columns = ["Keyword", "imageUrl", "scrapeTime"]
        print(result)
    else:
        print("No result")


def handle_response(response):
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        return errh
    except requests.exceptions.ConnectionError as errc:
        return errc
    except requests.exceptions.Timeout as errt:
        return errt
    except requests.exceptions.RequestException as err:
        return err


def insert_data(imageUrl,scrapeTime, keyword):
    mydb = mysql.connect(
    host="yourHost",
    user="yourUser",
    password="yourPassword",
    database="yourDB"
    )
    cursor = mydb.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS flickr_data (imageUrl VARCHAR(100), scrapeTime DATETIME, keyword VARCHAR(100))")

    sql = "INSERT INTO flickr_data (imageUrl,scrapeTime, keyword) VALUES (%s, %s, %s)"
    value = (imageUrl, scrapeTime, keyword)
    cursor.execute(sql, value)

    mydb.commit()

def query_data(minScrapeTime, maxScrapeTime, keyword, size):
    mydb = mysql.connect(
    host="yourHost",
    user="yourUser",
    password="yourPassword",
    database="yourDB"
    )
    cursor = mydb.cursor()

    query = f"""select keyword, imageUrl, scrapeTime 
               from yourDB.flickr_data 
               where keyword = '{keyword}' and scrapeTime between '{minScrapeTime}' and '{maxScrapeTime}' 
               limit {size};"""
    cursor.execute(query)
    return cursor.fetchall()

if __name__ == "__main__":
    #For scrape function
    print("Insert keyword: ")
    keyword = input()
    print("Insert size: ")
    size = int(input())
    scrape(keyword,size)

    #For search function
    print("\nSearch for a keyword: ")
    keyword_search = input()
    print("Min search time: ")
    min_serachTime = input()
    print("Max search time: ")
    max_searchTime = input()
    print("Select size for results: ")
    result_size = int(input())
    search(min_serachTime,max_searchTime,keyword_search, result_size)