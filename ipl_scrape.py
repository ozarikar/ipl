#scrape https://www.espncricinfo.com/series/indian-premier-league-2023-1345038/match-schedule-fixtures-and-results
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_ipl_schedule(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    matches = []
    match_containers = soup.find_all('div', class_='match-info')

    for match in match_containers:
        teams = match.find_all('div', class_='team-name')
        team1 = teams[0].text.strip()
        team2 = teams[1].text.strip()

        date_time = match.find('div', class_='match-date').text.strip()
        venue = match.find('div', class_='match-venue').text.strip()

        matches.append({
            'Team 1': team1,
            'Team 2': team2,
            'Date & Time': date_time,
            'Venue': venue
        })

    return pd.DataFrame(matches)