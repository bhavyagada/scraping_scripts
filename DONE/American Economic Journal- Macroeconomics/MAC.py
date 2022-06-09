# Imports

import re
import csv
import sys
from os import path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# CSV Header and Data Lists

article_header = ["issn", "e_issn", "publication_name", "volume", "issue", "document_title", "document_type", 
                "issue_date", "publication_date", "digital_object_identifier", "abstract", "jel_classification"]
article_data = ["1945-7707", "1945-7715", "American Economic Journal: Macroeconomics"]

author_header = ["digital_object_identifier", "co_author_name", "co_author_order"]

# Write to CSV files

try:
    # Article Writer
    if path.exists('Articles-American Economic Journal Macroeconomics.csv') == False:
        articles_file = open('Articles-American Economic Journal Macroeconomics.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)
        article_writer.writerow(article_header)
    else:
        articles_file = open('Articles-American Economic Journal Macroeconomics.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)

    # Author Writer
    if path.exists('Authors-American Economic Journal Macroeconomics.csv') == False:
        authors_file = open('Authors-American Economic Journal Macroeconomics.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
        author_writer.writerow(author_header)
    else:
        authors_file = open('Authors-American Economic Journal Macroeconomics.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
except Exception as e:
    articles_file.close()
    authors_file.close()
    print(e)

# Browse

driver = webdriver.Chrome(executable_path="C:\\Users\\User\\Desktop\\Scraping\\GScholar\\chromedriver")

url = "https://www.aeaweb.org/journals/mac/issues"
driver.get(url)

def browse_volumes_page():
    issue_url_list = []
    
    volumes = driver.find_elements_by_xpath("//article[contains(@class, 'journal-preview')]/div/a")
    for v in volumes:
        url = v.get_attribute("href")
        issue_url_list.append(url)

    return issue_url_list

issue_urls = browse_volumes_page()
print('\n'.join(issue_urls))

latest_url = issue_urls[0]

if len(sys.argv) > 1 and sys.argv[1] == 'scrape_latest':
    with open('recent.txt', 'r') as f:
        last_issue = f.read()
    y = issue_urls.index(last_issue)
    issue_urls = issue_urls[:y]
    with open('recent.txt', 'w') as f:
        f.write(latest_url)

    print(issue_urls)

article_urls = []

for url in issue_urls:
    driver.get(url)
    articles = driver.find_elements_by_xpath("//article/h3/a")
    for a in articles:
        url = a.get_attribute("href")
        article_urls.append(url)
    
    print('\n'.join(article_urls))

    for url in article_urls:
        driver.get(url)
        url_type = driver.execute_script("return document.contentType")

        if url_type != 'text/html':
            article_writer.writerow(article_data)
        else:
            try:
                vol_issue_date = driver.find_element_by_xpath("//a[2]/li[@class='journal']").text
                vi = re.findall("[\d]+", vol_issue_date)
                date = re.findall("[^\d, ]+", vol_issue_date)
                volume = vi[0]
                issue = vi[1]
                issue_date = date[2] + " " + vi[2]
                publication_date = issue_date
            except NoSuchElementException:
                volume = "None"
                issue = "None"
                issue_date = "None"
                publication_date = "None"

            try:
                document_title = driver.find_element_by_xpath("//h1[@class='title']").text
            except NoSuchElementException:
                document_title = "None"

            document_type = "Article"

            try:
                abstract = driver.find_element_by_xpath("//section[@class='article-information abstract']").text
                abstract = abstract[9:]
            except NoSuchElementException:
                abstract = "None"

            try:
                doi = driver.find_element_by_xpath("//span[@class='doi']").text
                digital_object_identifier = re.findall(": (.*)", doi)
            except NoSuchElementException:
                digital_object_identifier = "None"

            try:
                jel = driver.find_elements_by_xpath("//ul[@class='jel-codes']/li/strong[@class='code']")
                classes = []
                for j in jel:
                    classes.append(j.text)
                if len(classes) == 0:
                    jel_classification = "None"
                else:
                    jel_classification = ', '.join(classes)
            except NoSuchElementException:
                jel_classification = "None"

            temp_article_list = [volume, issue, document_title, document_type, issue_date, publication_date, digital_object_identifier[0], abstract, jel_classification]
            article_list = article_data + temp_article_list
            article_writer.writerow(article_list)

            print('\n'.join(article_list))

            try:
                authors = driver.find_elements_by_xpath("//li[@class='author']")
                i = 1
                for a in authors:
                    author_data = [digital_object_identifier[0], a.text, i]
                    i += 1

                    print(author_data)
                    author_writer.writerow(author_data)
                    author_data.clear()
            except NoSuchElementException:
                author_data = [digital_object_identifier[0], "None", "None"]
                author_writer.writerow(author_data)
        
    article_urls.clear()

# Close the driver and csv files when we're done.

articles_file.close()
authors_file.close()
driver.close()
