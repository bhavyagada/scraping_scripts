# Imports

import re
import csv
import sys
from os import path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# CSV Header and Data Lists

article_header = ["issn", "e_issn", "publication_name", "volume", "issue", "document_title", "issue_date", 
                    "publication_date", "digital_object_identifier", "abstract", "keywords"]
article_data = ["0276-7783", "2162-9730", "Management Information Systems Quarterly"]

author_header = ["digital_object_identifier", "co_author_name", "co_author_order"]

# Write to CSV files

try:
    # Article Writer
    if path.exists('Articles-Management Information Systems Quarterly.csv') == False:
        articles_file = open('Articles-Management Information Systems Quarterly.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)
        article_writer.writerow(article_header)
    else:
        articles_file = open('Articles-Management Information Systems Quarterly.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)

    # Author Writer
    if path.exists('Authors-Management Information Systems Quarterly.csv') == False:
        authors_file = open('Authors-Management Information Systems Quarterly.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
        author_writer.writerow(author_header)
    else:
        authors_file = open('Authors-Management Information Systems Quarterly.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
except Exception as e:
    articles_file.close()
    authors_file.close()
    print(e)

# Browse

driver = webdriver.Chrome(executable_path="C:\\Users\\User\\Desktop\\Scraping\\chromedriver")

url = "https://www.misq.org/archive/"
driver.get(url)

def browse_volumes_page():
    issue_url_list = []
    
    volumes = driver.find_elements_by_xpath("//div[@id='main']/table/tbody/tr/td/a")
    for v in volumes:
        url = v.get_attribute("href")
        issue_url_list.append(url)

    return issue_url_list

issue_urls = browse_volumes_page()
print('\n'.join(issue_urls))

latest_issue = issue_urls[2]

if len(sys.argv) > 1 and sys.argv[1] == 'scrape_latest':
    with open('recent.txt', 'r') as f:
        last_issue = f.read()
    y = issue_urls.index(last_issue)
    issue_urls = issue_urls[:y]
    with open('recent.txt', 'w') as f:
        f.write(latest_issue)
    
    print('\n'.join(issue_urls))

article_urls = []

for url in issue_urls[2:]:
    driver.get(url)

    articles = driver.find_elements_by_xpath("//div[@id='main']/p/a")
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
                document_title = driver.find_element_by_xpath("//h3[@class='product-name']").text
                document_title = re.sub("\n", "", document_title)
            except NoSuchElementException:
                document_title = "None"

            try:
                abstract = driver.find_element_by_xpath("//div[@class='product-specs']").text
                abs = re.split("\n", abstract)
                index = -1
                if len(abs) > 1:
                    for a in abs[len(abs) - 2:]:
                        date = re.search("online.(.*)", a, re.IGNORECASE)
                        if date:
                            index = abs.index(a)
                            issue_date = date.group(1).strip()
                            publication_date = issue_date
                            break
                        else:
                            issue_date = "None"
                            publication_date = "None"
                    abstract = " ".join(abs[:index]).strip()
                else:
                    abstract = abs[0]
                    issue_date = "None"
                    publication_date = "None"
            except NoSuchElementException:
                abstract = "None"
                issue_date = "None"
                publication_date = "None"

            try:
                volume = driver.find_element_by_xpath("//td[contains(text(), 'Volume')]/following-sibling::td[@class='data last']").text
            except NoSuchElementException:
                volume = "None"

            try:
                issue = driver.find_element_by_xpath("//td[contains(text(), 'Issue')]/following-sibling::td[@class='data last']").text
            except NoSuchElementException:
                issue = "None"

            try:
                keywords = driver.find_element_by_xpath("//td[contains(text(), 'Keywords')]/following-sibling::td[@class='data last']").text
            except NoSuchElementException:
                keywords = "None"
            
            try:
                doi = driver.find_element_by_xpath("//td[contains(text(), 'Page Numbers')]/following-sibling::td[@class='data last']").text
                dobj = re.search(":(.*)", doi, re.IGNORECASE)
                if dobj:
                    digital_object_identifier = dobj.group(1).strip()
                else:
                    digital_object_identifier = "None"
            except NoSuchElementException:
                digital_object_identifier = "None"

            temp_article_list = [volume, issue, document_title, issue_date, publication_date, digital_object_identifier, abstract, keywords]
            article_list = article_data + temp_article_list

            print('\n'.join(article_list))
            article_writer.writerow(article_list)

            try:
                auths = driver.find_element_by_xpath("//td[contains(text(), 'Author')]/following-sibling::td[@class='data last']").text
                a_list = auths.split(" and ")
                authors = []
                author_names = []
                for a in a_list:
                    authors.append(re.split(",", a))
                
                for x in authors:
                    for y in x:
                        author_names.append(y.strip())
                
                author_names = list(filter(None, author_names))

                j = 1
                for name in author_names:
                    if digital_object_identifier != "None":
                        author_data = [digital_object_identifier, name, j]
                    else:
                        author_data = ["None", name, j]
                    j += 1
                    print(author_data)
                    author_writer.writerow(author_data)
                    author_data.clear()

            except NoSuchElementException:
                author_data = ["None", "None"]
                author_writer.writerow(author_data)

    article_urls.clear()

# Close the driver and csv files when we're done.

articles_file.close()
authors_file.close()
driver.close()
