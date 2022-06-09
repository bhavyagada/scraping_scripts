# Imports

import re
import csv
import sys
from os import path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# CSV Header and Data Lists

article_header = ["issn", "e_issn", "publication_name", "volume", "issue", "document_title", "issue_date", 
                "publication_date", "published_date", "manuscript_received_date", "manuscript_accepted_date", 
                "digital_object_identifier", "abstract", "keywords", "jel_classification"]
article_data = ["2333-5955", "2333-5963", "Journal of the Association of Environmental and Resource Economists"]

author_header = ["digital_object_identifier", "co_author_name", "co_author_order"]

# Write to CSV files

try:
    # Article Writer
    if path.exists('Articles-Journal of the Association of Environmental and Resource Economists.csv') == False:
        articles_file = open('Articles-Journal of the Association of Environmental and Resource Economists.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)
        article_writer.writerow(article_header)
    else:
        articles_file = open('Articles-Journal of the Association of Environmental and Resource Economists.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)

    # Author Writer
    if path.exists('Authors-Journal of the Association of Environmental and Resource Economists.csv') == False:
        authors_file = open('Authors-Journal of the Association of Environmental and Resource Economists.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
        author_writer.writerow(author_header)
    else:
        authors_file = open('Authors-Journal of the Association of Environmental and Resource Economists.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
except Exception as e:
    articles_file.close()
    authors_file.close()
    print(e)

# Browse

driver = webdriver.Firefox(executable_path="C:\\Users\\User\\Desktop\\Scraping\\geckodriver")

url = "https://www.journals.uchicago.edu/loi/jaere"
driver.get(url)

def browse_volumes_page():
    year_list = []
    issue_url_list = []
    
    all_divs = driver.find_elements_by_xpath("//div[@class='row']/div/div/div/div/h3/a")
    for a in all_divs:
        url = a.get_attribute("href")
        year_list.append(url)
    
    for y in year_list:
        driver.get(y)
        volumes = driver.find_elements_by_xpath("//div[@class='row']/div/div/div/div/div/ul/li/a")
        for v in volumes:
            url = v.get_attribute("href")
            issue_url_list.append(url)

    url_list = list(set(issue_url_list))
    url_list.sort(reverse=True)
    return url_list

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
    article_urls = []
    articles = driver.find_elements_by_xpath("//div[@class='publication-body']/ul/li/div[2]/div[2]/div/h5/a")
    for a in articles:
        url = a.get_attribute("href")
        article_urls.append(url)

    print('\n'.join(article_urls))

    for url in article_urls:
        driver.get(url)
        try:
            document_title = driver.find_element_by_xpath("//h1[@class='citation__title']").text
            document_title = re.sub("\n", "", document_title)
        except NoSuchElementException:
            document_title = "None"

        try:
            abstract = driver.find_element_by_xpath("//div[@class='abstractSection abstractInFull']/p").text
            abstract = re.sub("\n", "", abstract)
        except NoSuchElementException:
            abstract = "None"

        try:
            volume_and_issue = driver.find_element_by_xpath("//span[@class='current-issue__parent-item']/a").text
            vid_list = volume_and_issue.split(",")
            volume_num = re.search("Volume(.*)", vid_list[0], re.IGNORECASE)
            issue_num = re.search("Number(.*)", vid_list[1], re.IGNORECASE)
            volume = volume_num.group(1).strip()
            issue = issue_num.group(1).strip()
        except NoSuchElementException:
            volume = "None"
            issue = "None"

        try:
            issue_date = driver.find_element_by_xpath("//span[@class='current-issue__date']/a").text
            publication_date = issue_date
        except NoSuchElementException:
            issue_date = "None"
            publication_date = "None"

        try:
            digital_object_identifier = driver.find_element_by_xpath("//div[@class='section__body section__body--article-doi']/a").text
        except NoSuchElementException:
            digital_object_identifier = "None"

        try:
            dates = driver.find_elements_by_xpath("//section[@id='history-section']/ul/li/span")
            manuscript_received_date = "None"
            manuscript_accepted_date = "None"
            published_date = "None"
            for d in dates:
                received = re.search("Received", d.text, re.IGNORECASE)
                if received:
                    manuscript_received_date = re.sub("Received", "", d.text).strip()
                    break

            for d in dates:
                accepted = re.search("Accepted", d.text, re.IGNORECASE)
                if accepted:
                    manuscript_accepted_date = re.sub("Accepted", "", d.text).strip()
                    break

            for d in dates:
                published = re.search("Published online", d.text, re.IGNORECASE)
                if published:
                    published_date = re.sub("Published online", "", d.text).strip()
                    break
        except NoSuchElementException:
            manuscript_received_date = "None"
            manuscript_accepted_date = "None"
            published_date = "None"

        try:
            kwords = []
            keys = driver.find_elements_by_xpath("//strong[contains(text(), 'Keywords')]/following-sibling::div[1]/ul/li/a")
            for k in keys:
                kwords.append(k.text)
            if len(kwords) > 0:
                keywords = ", ".join(kwords)
            else:
                keywords = "None"
        except NoSuchElementException:
            keywords = "None"

        try:
            codes = []
            jels = driver.find_elements_by_xpath("//strong[contains(text(), 'JEL')]/following-sibling::div[1]/ul/li/a")
            for j in jels:
                codes.append(j.text)
            if len(codes) > 0:
                jel_classification = ", ".join(codes)
            else:
                jel_classification = "None"
        except NoSuchElementException:
            jel_classification = "None"

        temp_article_list = [volume, issue, document_title, issue_date, publication_date, published_date, manuscript_received_date, manuscript_accepted_date, digital_object_identifier, abstract, keywords, jel_classification]
        article_list = article_data + temp_article_list

        print('\n'.join(article_list))
        article_writer.writerow(article_list)

        try:
            j = 1
            authors = driver.find_elements_by_xpath("//a[contains(@class, 'author-name')]/span")
            for a in authors:
                author_data = [digital_object_identifier, a.text, j]
                j += 1
                print(author_data)
                author_writer.writerow(author_data)
                author_data.clear()
        except NoSuchElementException:
            author_data = [digital_object_identifier, "None", "None"]
            author_writer.writerow(author_data)

# Close the driver and csv files when we're done.

articles_file.close()
authors_file.close()
driver.close()
