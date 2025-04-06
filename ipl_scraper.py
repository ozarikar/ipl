from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

def get_all_data(last_x_seasons):
    url = 'https://www.iplt20.com/matches/results/'
    seasons = find_all_seasons(url)
    all_seasons_data = []
    for season in seasons[0:last_x_seasons]:
       all_seasons_data.append(get_season_data(season))
    return all_seasons_data

def get_season_data(season):
    url = f'https://www.iplt20.com/matches/results/{season}'
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'lxml')
    matches = soup.find_all('a', class_='vn-matchBtn ng-scope')
    curr_season_data = []
    for match in matches:
        curr_season_data.append(get_match_data(match['href']))
    driver.quit()
    return curr_season_data
    

def get_match_data(url):
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'lxml')
    matches = soup.find_all('li', class_='ng-scope')
    for match in matches:
        list_of_matches.append(match.text.strip())
    driver.quit()
    return list_of_matches

def find_all_seasons(url):
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    list_of_seasons = []
    driver.get(url)
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'lxml')
    seasons = soup.find_all('div', class_='cSBListItems ng-binding ng-scope', attrs={'ng-repeat': 'list in seasonList'})
    for season in seasons:
        list_of_seasons.append(season.text.strip().split()[-1])
    driver.quit()
    return list_of_seasons

def main():
    data = get_all_data(3)

if __name__ == "__main__":
    main()
