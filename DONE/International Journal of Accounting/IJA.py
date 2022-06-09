# Imports

import re
import csv
import sys
from os import path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# CSV Header and Data Lists

article_header = ["issn", "e_issn", "publication_name", "volume", "issue", "document_title", "issue_date", 
                "publication_date", "published_date", "digital_object_identifier", "abstract", "keywords"]
article_data = ["1094-4060", "2213-3933", "International Journal of Accounting"]

author_header = ["digital_object_identifier", "co_author_name", "co_author_order", "co_author_affiliation"]

# Write to CSV files

try:
    # Article Writer
    if path.exists('Articles-International Journal of Accounting.csv') == False:
        articles_file = open('Articles-International Journal of Accounting.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)
        article_writer.writerow(article_header)
    else:
        articles_file = open('Articles-International Journal of Accounting.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)

    # Author Writer
    if path.exists('Authors-International Journal of Accounting.csv') == False:
        authors_file = open('Authors-International Journal of Accounting.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
        author_writer.writerow(author_header)
    else:
        authors_file = open('Authors-International Journal of Accounting.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
except Exception as e:
    articles_file.close()
    authors_file.close()
    print(e)

# Browse

driver = webdriver.Chrome(executable_path="C:\\Users\\User\\Desktop\\Scraping\\chromedriver")

url = "https://www.worldscientific.com/toc/tija/current"
driver.get(url)

def browse_volumes_page():
    year_list = []
    issue_url_list = []

    available = driver.find_element_by_xpath("//div[@id='loi-banner']/a[3]")
    driver.execute_script("arguments[0].click();", available)
    years = driver.find_elements_by_xpath("//div[@class='tab__content']/div/div/ul/li/a")
    for y in years:
        url = y.get_attribute("href")
        year_list.append(url)

    for year in year_list:
        driver.get(year)
        available = driver.find_element_by_xpath("//div[@id='loi-banner']/a[3]")
        driver.execute_script("arguments[0].click();", available)
        volumes = driver.find_elements_by_xpath("//div[contains(@class, 'tab__content')]/div/ul/li/a")
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

for url in issue_urls:
    driver.get(url)
    try:
        volume_and_issue = driver.find_element_by_xpath("//h3[@class='sep citation section__header']").text
        vid_list = volume_and_issue.split(",")
        volume_num = re.search("Volume(.*)", vid_list[0], re.IGNORECASE)
        issue_num = re.search("Issue(.*)\((.*?)\)", vid_list[1], re.IGNORECASE)
        volume = volume_num.group(1).strip()
        issue = issue_num.group(1).strip()
        dates = re.search("\((.*?)\)", vid_list[1], re.IGNORECASE)
        issue_date = dates.group(1).strip()
        publication_date = issue_date
    except NoSuchElementException:
        volume = "None"
        issue = "None"
        issue_date = "None"
        publication_date = "None"

    article_urls = []
    articles = driver.find_elements_by_xpath("//div[@class='issue-item']/h5/a")
    for a in articles:
        url = a.get_attribute("href")
        article_urls.append(url)

    print('\n'.join(article_urls))

    for url in article_urls:
        driver.get(url)
        try:
            document_title = driver.find_element_by_xpath("//h1[@class='citation__title']").text
        except NoSuchElementException:
            document_title = "None"
        
        try:
            published = driver.find_element_by_xpath("//section[@class='article__history']/span").text
            date = re.search("Published:(.*)", published, re.IGNORECASE)
            published_date = date.group(1).strip()
        except NoSuchElementException:
            published_date = "None"

        try:
            abstract = driver.find_element_by_xpath("//div[@class='abstractSection abstractInFull']/p").text
            abstract = re.sub("\n", "", abstract)
        except NoSuchElementException:
            abstract = "None"

        try:
            digital_object_identifier = driver.find_element_by_xpath("//div[@class='epub-section']/span/a").text
        except NoSuchElementException:
            digital_object_identifier = "None"

        try:
            keyword_list = []
            keys = driver.find_elements_by_xpath("//div[@id='keywords']/ul/li/a")
            for k in keys:
                keyword_list.append(k.text)
            if len(keyword_list) > 0:
                keywords = ", ".join(keyword_list)
            else:
                keywords = "None"
        except NoSuchElementException:
            keywords = "None"

        temp_article_list = [volume, issue, document_title, issue_date, publication_date, published_date, digital_object_identifier, abstract, keywords]
        article_list = article_data + temp_article_list

        print('\n'.join(article_list))
        article_writer.writerow(article_list)

        try:
            j = 1
            isorcid = False
            author_info = driver.find_elements_by_xpath("//div[@class='accordion']/div/div")
            for info in author_info:
                name = info.find_element_by_xpath("./a/span").text
                more = info.find_element_by_xpath("./a")
                driver.execute_script("arguments[0].click();", more)
                try:
                    orcid = info.find_element_by_xpath("./div/p[@class='orcid-account']")
                    isorcid = True
                except NoSuchElementException:
                    isorcid = False

                if isorcid == True:
                    try:
                        aff = info.find_element_by_xpath("./div/p[4]")
                        affiliation = aff.text
                    except NoSuchElementException:
                        affiliation = "None"
                else:
                    try:
                        aff = info.find_element_by_xpath("./div/p[3]")
                        affiliation = aff.text
                    except NoSuchElementException:
                        affiliation = "None"

                author_data = [digital_object_identifier, name, j, affiliation]
                print(author_data)
                j += 1
                author_writer.writerow(author_data)
                author_data.clear()
        except NoSuchElementException:
            author_data = [digital_object_identifier, "None", "None", "None"]
            author_writer.writerow(author_data)

# Close the driver and csv files when we're done.

articles_file.close()
authors_file.close()
driver.close()
