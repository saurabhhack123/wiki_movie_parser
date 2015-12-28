#!/usr/bin/python 

import urllib
import robotexclusionrulesparser as rerp
from bs4 import BeautifulSoup
from urlparse import urlparse, urljoin
from xlrd import *
import unicodedata
import xlwt

cache = {}

def get_page(url):
	page_url = urlparse(url)
	base = page_url[0] + '://' + page_url[1]
	robots_url = base + '/robots.txt'
	rp = rerp.RobotFileParserLookalike()
	rp.set_url(robots_url)
	rp.read()
	if not rp.can_fetch('*', url):
		print "Page off limits!"
		return BeautifulSoup(""), ""
	if url in cache:
		return cache[url]
	else:
		# print "Page not in cache: " + url
		try:
			content = urllib.urlopen(url).read()
			return BeautifulSoup(content), url
		except:
			return BeautifulSoup(""), ""

def crawl_wiki(search_for):
	page = "http://en.wikipedia.org/wiki/"+ search_for
	print page
	# print page
	# infobox vevent
	soup, url = get_page(page)
	# print soup

	table = soup.find('table',attrs={"class" : "infobox"})
	records = [] # store all of the records in this list
	count= 0 
	movie_record = {}

	for row in table.findAll('tr'):
	    count=count+1
	    if count < 3:
	    	continue

	    th = row.find_all("th")[0].get_text().strip()
	    th_ascii = unicodedata.normalize('NFKD', th).encode('ascii','ignore').replace('\n',' ')
	    td = row.find_all("td")[0].get_text().strip()
	    td_ascii = unicodedata.normalize('NFKD', td).encode('ascii','ignore').replace('\n',' ')
	    movie_record[th_ascii]=td_ascii

	return movie_record

wb = open_workbook('input_movie_list.xlsx')
workbook = xlwt.Workbook()
sheet = workbook.add_sheet('movie_data')


sheetname = wb.sheet_names()
sh1 = wb.sheet_by_index(0)
row = 0
col = 17

# prepare header

sheet.write(0,0,"Movie")
sheet.write(0,1,"Directed by")
sheet.write(0,2,"Produced by")
sheet.write(0,3,"Starring")
sheet.write(0,4,"Production company")
sheet.write(0,5,"Distributed by")
sheet.write(0,6,"Release dates")
sheet.write(0,7,"Budget")
sheet.write(0,8,"Box office")

row = 1;

for index in range(0,sh1.nrows):
    movie = sh1.cell(index,0).value.replace(" ","_")
    movie_record = crawl_wiki(movie)
    sheet.write(row,0,movie)
    sheet.write(row,1,movie_record["Directed by"])
    sheet.write(row,2,movie_record["Produced by"])
    sheet.write(row,3,movie_record["Starring"])
    
    if "Production company" in movie_record:
    	sheet.write(row,4,movie_record["Production company"])
    else:
    	sheet.write(row,4,"NA")


    sheet.write(row,5,movie_record["Distributed by"])
    sheet.write(row,6,movie_record["Release dates"])
    
    if "Budget" in movie_record:
    	sheet.write(row,7,movie_record["Budget"])
    else:
    	sheet.write(row,7,"NA")

    sheet.write(row,8,movie_record["Box office"])
    row = row+1;

workbook.save('output.xls')