from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import requests
import json
import time
import os

chrome_options = webdriver.ChromeOptions()
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)




def find_target_api_url(url, key_indicator, number_of_requests):
    urls = []
    max_retries=3
    try:
        retry_count = 0
        while retry_count <= max_retries:
            if retry_count == 0:
                driver.get_log("performance")  # Clear logs
                driver.get(url)
            else:
                print(f"Retrying ({retry_count}/{max_retries}) for {url} - '{key_indicator}' not found")
                driver.get_log("performance")  # Clear logs before reload
                driver.refresh()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            WebDriverWait(driver, 20).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            time.sleep(5)
            logs = driver.get_log("performance")
            urls = []
            for entry in logs:
                log = json.loads(entry["message"])["message"]
                if (log["method"] == "Network.requestWillBeSent" and "request" in log["params"]
                    and log["params"]["request"]["method"] == "GET" and key_indicator in log["params"]["request"]["url"]):
                    urls.append(log["params"]["request"]["url"])
                    if len(urls) == number_of_requests:
                        break
            if urls:
                print(f"Success: Found {len(urls)} URLs containing '{key_indicator}' for {url}")
                break
            retry_count += 1
            if retry_count > max_retries:
                print(f"No URLs found containing '{key_indicator}' for {url} after {max_retries} retries")
    except Exception as e:
        print(f"Error loading {url}: {e}")
    return urls



def find_all_seasons_codes(url):
    urls = find_target_api_url(url, "competition.js",1)
    if len(urls) == 0:
        raise ValueError(f"No URLs found containing 'competition.js' for {url}")
    url = urls[0]
    season_data = requests.get(url)
    season_data = season_data._content.decode('utf-8')
    season_data = season_data.replace("oncomptetion(", "").rstrip(");")
    season_data = json.loads(season_data)
    season_data = season_data['division']
    list_of_seasons = [season['SeasonName'] for season in season_data if 'SeasonName' in season]
    return list_of_seasons


def get_match_codes(season):
    url = f'https://www.iplt20.com/matches/results/{season}'
    urls = find_target_api_url(url, "matchschedule.js", 1)
    if len(urls) == 0:
        print(f"No URLs found for match {url} for season {season}")
        return []
    url = urls[0]
    season_summary = requests.get(url)._content.decode('utf-8')
    season_summary = season_summary.replace("MatchSchedule(", "").rstrip(");")
    season_summary = json.loads(season_summary)
    list_of_matches = season_summary['Matchsummary']
    list_of_matches = [match['MatchID'] for match in list_of_matches if 'MatchID' in match]
    return list_of_matches

def get_match_data(match_code, season):
    url = f'https://www.iplt20.com/match/{season}/{match_code}'
    urls = find_target_api_url(url, f'{match_code}-Innings', 2)
    if len(urls) != 2:
        print(f"No URLs found containing 'Innings' for {match_code} for season {season}")
        return []
    match_data = []
    for url in urls:
        if url:
            inning_data = requests.get(url)._content.decode('utf-8')
            inning_data = inning_data.replace("onScoring(", "").rstrip(");")
            inning_data = json.loads(inning_data)
            inning = inning_data.get("Innings1") or inning_data.get("Innings2")
            if inning:  # Check if inning is not None
                try:
                    match_data.extend(inning['OverHistory'])
                except KeyError:
                    print(f"KeyError: 'OverHistory' not found in inning data for match {match_code} in season {season}")
            else:
                print(f"No 'Innings1' or 'Innings2' found for match {match_code} in season {season}")
    return match_data

def get_all_data(last_x_seasons):
    url = 'https://www.iplt20.com/matches/results/'
    seasons = find_all_seasons_codes(url)
    matches_data = []
    for season in seasons[0:last_x_seasons]:
        matches = get_match_codes(season)
        for match in matches:
            matches_data.extend(get_match_data(match, season))
    return matches_data

def main():
    all_data = get_all_data(1)
    if not all_data:
        print("No data collected.")
        return
    file_path = 'ipl_data.csv'
    existing_data = []

    # Check if the file exists and read existing data
    if os.path.exists(file_path):
        with open(file_path, 'r', newline='') as file:
            reader = csv.DictReader(file)
            existing_data = list(reader)

    # Combine existing data with new data
    combined_data = existing_data + all_data

    # Remove duplicates based on all keys
    unique_data = {tuple(sorted(item.items())): item for item in combined_data}.values()

    # Write the combined unique data back to the file
    with open(file_path, 'w', newline='') as file:
        fieldnames = set().union(*[d.keys() for d in unique_data])  # Get all unique keys
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_data)

    print("Data saved to ipl_data.csv")
    driver.quit()  # Close the driver after all operations

if __name__ == "__main__":
    main()