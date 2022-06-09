# Imports

import re
import csv
import sys
from os import path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# CSV Header and Data Lists

article_header = ["issn", "e_issn", "publication_name", "volume", "issue", "document_title", "document_type", 
                "issue_date", "publication_date", "published_date", "manuscript_received_date", "manuscript_revised_date",
                "manuscript_accepted_date", "digital_object_identifier", "abstract", "keywords"]
article_data = ["0923-0645", "1573-059X", "Marketing Letters"]

author_header = ["digital_object_identifier", "co_author_name", "co_author_order", "co_author_affiliation"]

# Write to CSV files

try:
    # Article Writer
    if path.exists('Articles-Marketing Letters.csv') == False:
        articles_file = open('Articles-Marketing Letters.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)
        article_writer.writerow(article_header)
    else:
        articles_file = open('Articles-Marketing Letters.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)

    # Author Writer
    if path.exists('Authors-Marketing Letters.csv') == False:
        authors_file = open('Authors-Marketing Letters.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
        author_writer.writerow(author_header)
    else:
        authors_file = open('Authors-Marketing Letters.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
except Exception as e:
    articles_file.close()
    authors_file.close()
    print(e)

# Browse

driver = webdriver.Chrome(executable_path="C:\\Users\\User\\Desktop\\Scraping\\GScholar\\chromedriver")

url = "https://link.springer.com/journal/11002/volumes-and-issues"
driver.get(url)

def browse_volumes_page():
    issue_url_list = []
    
    volumes = driver.find_elements_by_xpath("//li[@class='c-list-group__item']/a")
    for v in volumes:
        url = v.get_attribute("href")
        issue_url_list.append(url)

    return issue_url_list

issue_urls = browse_volumes_page()
print('\n'.join(issue_urls))

latest_issue = issue_urls[0]

if len(sys.argv) > 1 and sys.argv[1] == 'scrape_latest':
    with open('recent.txt', 'r') as f:
        last_issue = f.read()
    y = issue_urls.index(last_issue)
    issue_urls = issue_urls[:y]
    with open('recent.txt', 'w') as f:
        f.write(latest_issue)
    
    print('\n'.join(issue_urls))

article_urls = []
document_type = []

for url in issue_urls:
    driver.get(url)
    try:
        volume_and_issue = driver.find_element_by_xpath("//div[@class='app-volumes-and-issues__info']/h1").text
        vid_list = volume_and_issue.split(",")
        volume_num = re.search("Volume(.[\s\d\w-]+)", vid_list[0], re.IGNORECASE)
        issue_num = re.search("issue(.[\s\d\w-]+)", vid_list[1], re.IGNORECASE)
        volume = volume_num.group(1).strip()
        issue = issue_num.group(1).strip()
        issue_date = vid_list[2]
        publication_date = issue_date
    except NoSuchElementException:
        volume = "None"
        issue = "None"
        issue_date = "None"
        publication_date = "None"

    articles = driver.find_elements_by_xpath("//article/div[@class='c-card__body app-card-body']")
    for a in articles:
        article = a.find_element_by_xpath(".//h3/a")
        doc_type = a.find_element_by_xpath(".//ul/li[@class='c-meta__item c-meta__item--block-sm-max']/span[contains(text(), 'Content type:')]/parent::li").text
        url = article.get_attribute("href")
        document_type.append(doc_type)
        article_urls.append(url)
    
    print('\n'.join(article_urls))

    i = 0
    for url in article_urls:
        driver.get(url)
        url_type = driver.execute_script("return document.contentType")

        if url_type != 'text/html':
            article_writer.writerow(article_data)
        else:
            try:
                document_title = driver.find_element_by_xpath("//h1[@class='c-article-title']").text
            except NoSuchElementException:
                document_title = "None"

            try:
                abstract = driver.find_element_by_xpath("//div[@id='Abs1-content']/p").text
            except NoSuchElementException:
                abstract = "None"

            try:
                manuscript_received_date = driver.find_element_by_xpath("//ul[@class='c-bibliographic-information__list']/li/p[contains(text(), 'Received')]/span[2]").text
            except NoSuchElementException:
                manuscript_received_date = "None"
            
            try:
                manuscript_revised_date = driver.find_element_by_xpath("//ul[@class='c-bibliographic-information__list']/li/p[contains(text(), 'Revised')]/span[2]").text
            except NoSuchElementException:
                manuscript_revised_date = "None"

            try:
                manuscript_accepted_date = driver.find_element_by_xpath("//ul[@class='c-bibliographic-information__list']/li/p[contains(text(), 'Accepted')]/span[2]").text
            except NoSuchElementException:
                manuscript_accepted_date = "None"

            try:
                published_date = driver.find_element_by_xpath("//ul[@class='c-bibliographic-information__list']/li/p[contains(text(), 'Published')]/span[2]").text
            except NoSuchElementException:
                published_date = "None"

            try:
                issue_date = driver.find_element_by_xpath("//ul[@class='c-bibliographic-information__list']/li/p[contains(text(), 'Issue Date')]/span[2]").text
                publication_date = issue_date
            except NoSuchElementException:
                issue_date = "None"
                publication_date = "None"

            try:
                digital_object_identifier = driver.find_element_by_xpath("//ul[@class='c-bibliographic-information__list']/li/p/span/a").text
            except NoSuchElementException:
                digital_object_identifier = "None"

            try:
                keywords = driver.find_elements_by_xpath("//h3[contains(text(), 'Keywords')]/following-sibling::ul[@class='c-article-subject-list'][1]/li/span")
                k_list = []
                for k in keywords:
                    k_list.append(k.text)
                if len(k_list) == 0:
                    keywords_list = "None"
                else:
                    keywords_list = ', '.join(k_list)
            except NoSuchElementException:
                keywords_list = "None"

            temp_article_list = [volume, issue, document_title, document_type[i], issue_date, publication_date, published_date, manuscript_received_date, manuscript_revised_date, manuscript_accepted_date, digital_object_identifier, abstract, keywords_list]
            article_list = article_data + temp_article_list
            i += 1

            print('\n'.join(article_list))
            article_writer.writerow(article_list)

            try:
                j = 1
                authors = driver.find_elements_by_xpath("//ul[@class='c-article-author-list js-etal-collapsed js-no-scroll']/li[contains(@class, 'c-article-author-list__item')]/a")
                for a in authors:
                    author_data = [digital_object_identifier, a.text, j]
                    driver.execute_script("arguments[0].click();", a)
                    each_author = driver.find_elements_by_xpath("//div[contains(@class, 'c-author-popup')]/section/ul/li[1]")
                    for e in each_author:
                        if e.is_displayed():
                            author_data.append(e.text)
                    j += 1

                    print(author_data)
                    author_writer.writerow(author_data)
                    author_data.clear()
            except NoSuchElementException:
                author_data = [digital_object_identifier, "None", "None", "None"]
                author_writer.writerow(author_data)
    
    document_type.clear()
    article_urls.clear()

# Close the driver and csv files when we're done.

articles_file.close()
authors_file.close()
driver.close()
