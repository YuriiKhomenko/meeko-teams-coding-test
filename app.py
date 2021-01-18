import requests
import demjson
import json
import csv
import os
from datetime import datetime

# CONSTANTS
URL_TO_PARSE = 'https://www.ampereanalysis.com/reports'
CONNECTION_ERROR = 'Cannot access the website'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 ' \
    'Safari/537.36'
START_OF_JS_OBJECT = 'report_obj = '
END_OF_JS_OBJECT = '];'
CSV_HEADERS = ['Date', 'Author', 'Title']


def get_raw_html(url: str) -> str:
    """
    Function to send GET request to get HTML of the web-page
    :param url: url of the parsing web-page
    :return: str -> HTML page
    """
    print(f'Sending request to URL: {url}')
    headers = {'User-Agent': USER_AGENT}
    r = requests.get(url, headers=headers, verify=False)

    if r.status_code == 200:
        print('Successfully received HTML of the page.')
        return r.text
    else:
        print('No access to the web-page.')
        return CONNECTION_ERROR


def get_articles(url: str) -> list:
    """
    Function to retrieve html and get list of articles (python dictionaries)
    :param url: url of the parsing web-page
    :return: list of python dictionaries
    """
    data = get_raw_html(url)
    if data != CONNECTION_ERROR:
        print('Start of HTML cleaning...')
        start_index = data.find(START_OF_JS_OBJECT)
        # Deleting beginning of the html code which is irrelevant for us
        data = data[start_index:].replace(START_OF_JS_OBJECT, '')
        end_index = data.find(END_OF_JS_OBJECT) + 1
        # Finding end of JS object
        data = data[:end_index].strip()
        print('HTML cleaning finished. Converting HTML into list with dicts...')
        # Cleaning up JS object to be able to transfer it into list of python dicts
        data = demjson.decode(data)
        print('HTML has been successfully converted into Python list.')
        return data
    else:
        return []


def generate_article_output(article: dict) -> dict:
    """
    Function creates Python dictionaries with fields according to the requirements
    :param article: Python dictionary
    :return: dict -> Python dictionaries with needed fields
    """
    date = article['publish_on']
    author = article['authors'].replace('&#39;', '\'').replace('&amp;', '&')
    title = article['title'].replace('&#39;', '\'').replace('&amp;', '&')

    if not date:
        date = 'Unknown Date'
    elif not author:
        author = 'Unknown Author'
    elif not title:
        title = 'Unknown Title'

    return {
        'date': date,
        'author': author,
        'title': title
    }


def filter_blog_articles(url: str) -> list:
    """
    Creates list of filtered dictionaries
    :param url: url of the web-page from which we are going to collect data
    :return:
    """
    articles = get_articles(url)
    filtered_articles = []
    if articles:
        print('Articles received. Processing articles...')
        for article in articles:
            filtered_article = generate_article_output(article)
            filtered_articles.append(filtered_article)
        print('Finished processing.')
        return filtered_articles
    else:
        return []


def save_output_data(articles: list):
    """
    Saves data both to CSV and JSON file
    :param articles: list of articles
    :return: None
    """
    if not os.path.exists('data'):
        os.makedirs('data')
    timestamp = datetime.today().strftime('%Y%m%d-%H%M')
    print('Writing articles to the CSV file...')
    with open(f'data/articles_{timestamp}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADERS)
        for article in articles:
            writer.writerow(
                [article['date'], article['author'], article['title']])
    print(f'Articles were successfully saved into `articles_{timestamp}.csv`')
    print('Generating JSON file...')
    with open('data/articles.json', 'w') as file:
        json.dump(articles, file)
    print('JSON file successfully created under name `articles.json`.')


if __name__ == '__main__':
    posts = filter_blog_articles(URL_TO_PARSE)
    if posts:
        save_output_data(posts)
    else:
        print(f'There is a problem accessing {URL_TO_PARSE}')
