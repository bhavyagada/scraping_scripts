# Imports

import re
import csv
import sys
from os import path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# CSV Header and Data Lists

article_header = ["issn", "e_issn", "publication_name", "volume", "issue", "document_title", "document_type", 
                "issue_date", "publication_date", "manuscript_received_date", "manuscript_accepted_date", 
                "digital_object_identifier", "abstract"]
article_data = ["0001-4826", "1558-7967", "The Accounting Review"]

author_header = ["digital_object_identifier", "co_author_name", "co_author_order", "co_author_affiliation"]

# Write to CSV files

try:
    # Article Writer
    if path.exists('Articles-The Accounting Review.csv') == False:
        articles_file = open('Articles-The Accounting Review.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)
        article_writer.writerow(article_header)
    else:
        articles_file = open('Articles-The Accounting Review.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)

    # Author Writer
    if path.exists('Authors-The Accounting Review.csv') == False:
        authors_file = open('Authors-The Accounting Review.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
        author_writer.writerow(author_header)
    else:
        authors_file = open('Authors-The Accounting Review.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
except Exception as e:
    articles_file.close()
    authors_file.close()
    print(e)

# Browse

driver = webdriver.Chrome(executable_path="C:\\Users\\User\\Desktop\\Scraping\\chromedriver")

url = "https://meridian.allenpress.com/accounting-review/issue/browse-by-year"
driver.get(url)

def browse_volumes_page():
    years_list = []
    
    years = driver.find_elements_by_xpath("//div[@class='widget-ContentBrowseAllYearsManifest widget-instance-IssueBrowseAllYears']/ol/li/a")
    for y in years:
        url = y.get_attribute("href")
        years_list.append(url)

    years_list.reverse()
    return years_list

all_volumes = browse_volumes_page()
print('\n'.join(all_volumes))

latest_year = all_volumes[0]
if len(sys.argv) > 1 and sys.argv[1] == 'scrape_latest':
    with open('recent_year.txt', 'r') as f:
        last_year = f.read()
    y = all_volumes.index(last_year)
    all_volumes = all_volumes[:y]
    
    print(all_volumes)

article_urls = []
volumes_list = []

for url in all_volumes:
    driver.get(url)
    volumes = driver.find_elements_by_xpath("//div[@class='widget-ContentBrowseByYearManifest widget-instance-IssueBrowseByYear']/ol/li/a")
    for v in volumes:
        url = v.get_attribute("href")
        volumes_list.append(url)

    volumes_list.reverse()

    if (url == latest_year):
        latest_issue = volumes_list[0]
        if len(sys.argv) > 1 and sys.argv[1] == 'scrape_latest':
            with open('recent.txt', 'r') as f:
                last_issue = f.read()
            y = all_volumes.index(last_issue)
            volumes_list = volumes_list[:y]
            with open('recent.txt', 'w') as f:
                f.write(latest_issue)
            with open('recent_year.txt', 'w') as f:
                f.write(latest_year)
            
            print(volumes_list)

    print('\n'.join(volumes_list))

    for url in volumes_list:
        driver.get(url)
        document_type = "Article"
        articles = driver.find_elements_by_xpath("//div[@class='section-container']/section/h4[contains(translate(., 'ARTICLES', 'Articles'), 'Articles')]/following-sibling::div/div/div/h5/a")
        for a in articles:
            article_url = a.get_attribute('href')
            article_urls.append(article_url)

        print('\n'.join(article_urls))

        for url in article_urls:
            driver.get(url)
            try:
                volume_and_issue = driver.find_element_by_xpath("//span[@class='volume issue']").text
                vid_list = volume_and_issue.split(",")
                volume_num = re.search("Volume(.[\s\d\w-]+)", vid_list[0], re.IGNORECASE)
                issue_num = re.search("Issue(.[\s\d\w-]+)", vid_list[1], re.IGNORECASE)
                volume = volume_num.group(1).strip()
                issue = issue_num.group(1).strip()
            except NoSuchElementException:
                volume = "None"
                issue = "None"

            try:
                issue_date = driver.find_element_by_xpath("//span[@class='article-date']").text
                publication_date = issue_date
            except NoSuchElementException:
                issue_date = "None"
                publication_date = "None"
            
            try:
                document_title = driver.find_element_by_xpath("//h1[@class='wi-article-title article-title-main']").text
            except NoSuchElementException:
                document_title = "None"

            try:
                digital_object_identifier = driver.find_element_by_xpath("//div[@class='citation-doi']/a").text
            except NoSuchElementException:
                digital_object_identifier = "None"
            
            try:
                article_history = driver.find_element_by_xpath("//div[@class='ww-citation-history-wrap js-history-dropdown-wrap']/a")
                driver.execute_script("arguments[0].click();", article_history)
                manuscript_received_date = driver.find_element_by_xpath("//div[contains(text(), 'Received')]/following-sibling::div[@class='wi-date']").text
                manuscript_accepted_date = driver.find_element_by_xpath("//div[contains(text(), 'Accepted')]/following-sibling::div[@class='wi-date']").text
            except NoSuchElementException:
                manuscript_received_date = "None"
                manuscript_accepted_date = "None"
            
            try:
                abstract = driver.find_element_by_xpath("//section[@class='abstract']/p").text
            except NoSuchElementException:
                abstract = "None"

            temp_article_list = [volume, issue, document_title, document_type, issue_date, publication_date, manuscript_received_date, manuscript_accepted_date, digital_object_identifier, abstract]
            article_list = article_data + temp_article_list
            print('\n'.join(article_list))
            article_writer.writerow(article_list)

            try:
                j = 1
                authors = driver.find_elements_by_xpath("//div[@class='al-authors-list']/div/a")
                for a in authors:
                    author_data = [digital_object_identifier, a.text, j]
                    driver.execute_script("arguments[0].click();", a)
                    each_author = driver.find_elements_by_xpath("//div[@class='aff']")
                    affs = []
                    for e in each_author:
                        if e.is_displayed():
                            affs.append(e.text)

                    if len(affs) == 0:
                        author_data.append("None")
                    else:
                        affiliations = ", ".join(affs)
                        author_data.append(affiliations)
                    j += 1

                    print(author_data)
                    author_writer.writerow(author_data)
                    author_data.clear()
            except NoSuchElementException:
                author_data = [digital_object_identifier, "None", "None", "None"]
                author_writer.writerow(author_data)

        article_urls.clear()
    volumes_list.clear()

# Close the driver and csv files when we're done.

articles_file.close()
authors_file.close()
driver.close()
