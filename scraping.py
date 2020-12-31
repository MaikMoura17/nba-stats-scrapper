import os
import time
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

seasons = []
rankings = {
	'points': {'field': 'PTS', 'label': 'PTS'},
	'assists': {'field': 'AST', 'label': 'AST'},
	'three_points': {'field': 'FG3M', 'label': '3PM'},
	'rebounds': {'field': 'REB', 'label': 'REB'},
	'steals': {'field': 'STL', 'label': 'STL'},
	'blocks': {'field': 'BLK', 'label': 'BLK'},
	'turnovers': {'field': 'TOV', 'label': 'TOV'}
}


def build_rank(type):

	field, label = rankings[type]['field'], rankings[type]['label']

	driver.find_element_by_xpath(
		f"//div[@class='nba-stat-table']//table//thead//tr//th[@data-field='{field}']").click()

	soup = get_element("//div[@class='nba-stat-table']//table")
	table = soup.find(name='table')

	df_full = pd.read_html(str(table))[0].head(10)
	df = df_full[['Unnamed: 0', 'PLAYER', 'TEAM', label]]
	df.columns = ['pos', 'player', 'team', 'total']

	return df.to_dict('records')


def get_seasons():
	soup = get_element("//div[@class='row row5 collapse stats-filters-top']//div//div[@split='splits.Season']//div//label//select[@name='Season']")

	for i in range(7, 32):
		selection = soup.find(attrs={"value": f"object:{i}"})
		seasons.append(selection['label'])


def get_element(xpath):
	element = driver.find_element_by_xpath(xpath)
	html_content = element.get_attribute('outerHTML')
	
	return BeautifulSoup(html_content, 'html.parser')


def create_json(top_10_ranking, season):
	js = json.dumps(top_10_ranking)
	fp = open(f'results/{season}_ranking.json', 'w')
	fp.write(js)
	fp.close()


base_url = 'https://www.nba.com/stats/players/traditional/?PerMode=Totals&sort=MIN&dir=-1&Season=2020-21&SeasonType=Regular%20Season'

option = Options()
option.headless = True
driver = webdriver.Chrome(executable_path=rf'{os.path.dirname(os.path.realpath(__file__))}\drivers\chromedriver.exe')
driver.get(base_url)
driver.implicitly_wait(5)

driver.find_element_by_id('onetrust-accept-btn-handler').click()

get_seasons()

for season in seasons:
	top_10_ranking = {}
	driver.find_element_by_xpath(
		f"//div[@class='row row5 collapse stats-filters-top']//div//div[@split='splits.Season']//div//label//select[@name='Season']//option[@label='{season}']").click()

	for rank in rankings:
		top_10_ranking[rank] = build_rank(rank)
		
	create_json(top_10_ranking, season)

driver.quit()