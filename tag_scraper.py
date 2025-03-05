from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import bs4
import json

# scrapes all the genres from Goodreads
# and writes them to 'tags.json'

num_pages = 14
genres_dict = {}

# set headless to True to run in the background
options = Options()
# options.headless = True

# open the browser
driver = webdriver.Chrome(options=options)

# loop through all the pages
for i in range(num_pages):
    # get the page
    url = f'https://www.goodreads.com/genres/list?page={i+1}'
    driver.get(url)

    # get the page source
    page = driver.page_source
    soup = bs4.BeautifulSoup(page, 'html.parser')

    # get all the genres
    genres = soup.find_all('div', class_='shelfStat')

    # loop through the genres
    for genre in genres:
        # each genre is in a div with class 'shelfStat'
        # with two divs inside it
        # the first div has the genre name
        # the second div has the number of books in the genre
        genre_name = genre.find_all('div')[0].text
        genre_name = genre_name.strip()
        genre_count = genre.find_all('div')[1].text
        genre_count = genre_count.strip()

        # parse the count
        # make sure to remove commas
        genre_count = genre_count.split(' ')[0]
        genre_count = genre_count.replace(',', '')
        genre_count = int(genre_count)

        print(genre_name, genre_count)

        # add the genre to the dictionary
        genres_dict[genre_name] = genre_count

# write the genres to a file
with open('tags.json', 'w') as f:
    json.dump(genres_dict, f)
