# Imports

import re
import csv
import sys
import time
from os import path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# CSV Header and Data Lists

article_header = ["issn", "e_issn", "publication_name", "volume", "issue", "document_title", "document_type", 
                "issue_date", "publication_date", "manuscript_received_date", "manuscript_accepted_date", 
                "digital_object_identifier", "abstract", "jel_classification"]
article_data = ["0022-166X", "1548-8004", "Journal of Human Resources"]

author_header = ["digital_object_identifier", "co_author_name", "co_author_order", "co_author_affiliation"]

# Write to CSV files

try:
    # Article Writer
    if path.exists('Articles-Journal of Human Resources.csv') == False:
        articles_file = open('Articles-Journal of Human Resources.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)
        article_writer.writerow(article_header)
    else:
        articles_file = open('Articles-Journal of Human Resources.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)

    # Author Writer
    if path.exists('Authors-Journal of Human Resources.csv') == False:
        authors_file = open('Authors-Journal of Human Resources.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
        author_writer.writerow(author_header)
    else:
        authors_file = open('Authors-Journal of Human Resources.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
except Exception as e:
    articles_file.close()
    authors_file.close()
    print(e)

# Browse

driver = webdriver.Chrome(executable_path="C:\\Users\\User\\Desktop\\Scraping\\chromedriver")

url = "http://jhr.uwpress.org/content/by/year"
driver.get(url)

def browse_volumes_page():
    issue_url_list = []
    
    rows = driver.find_elements_by_xpath("//table[@class='proxy-archive-content-year-list']/tbody/tr")
    for r in rows[3:]:
        volumes = r.find_elements_by_xpath(".//td[@class='proxy-archive-year']/a")
        for v in volumes:
            url = v.get_attribute("href")
            issue_url_list.append(url)

    issue_url_list.sort(reverse=True)
    return issue_url_list

issue_urls = browse_volumes_page()
print('\n'.join(issue_urls))

latest_year = issue_urls[0]
if len(sys.argv) > 1 and sys.argv[1] == 'scrape_latest':
    with open('recent_year.txt', 'r') as f:
        last_year = f.read()
    y = issue_urls.index(last_year)
    issue_urls = issue_urls[:y]
    
    print(issue_urls)

issue_list = []
for url in issue_urls:
    driver.get(url)
    issues = driver.find_elements_by_xpath("//td[@class='proxy-archive-by-year-month']/p/strong/a")
    for i in issues:
        url = i.get_attribute("href")
        issue_list.append(url)

    issue_list.sort(reverse=True)

    if (url == latest_year):
        latest_issue = issue_list[0]
        if len(sys.argv) > 1 and sys.argv[1] == 'scrape_latest':
            with open('recent.txt', 'r') as f:
                last_issue = f.read()
            y = issue_list.index(last_issue)
            issue_list = issue_list[:y]
            with open('recent.txt', 'w') as f:
                f.write(latest_issue)
            with open('recent_year.txt', 'w') as f:
                f.write(latest_year)
            
            print(issue_list)

    print('\n'.join(issue_list))

    time.sleep(5)
    for url in issue_list:
        driver.get(url)
        try:
            date = driver.find_element_by_xpath("//span[@class='toc-top-pub-date']").text
            issue_date = date.replace(";", "")
            publication_date = issue_date
        except NoSuchElementException:
            issue_date = "None"
            publication_date = "None"

        try:    
            volume = driver.find_element_by_xpath("//span[@class='toc-citation-volume']").text
        except NoSuchElementException:
            volume = "None"

        try:
            issue = driver.find_element_by_xpath("//span[@class='toc-citation-issue']").text
            issue = issue.strip("()")
        except NoSuchElementException:
            issue = "None"

        try:
            document_type = driver.find_element_by_xpath("//h2[@id='Articles']/span").text
        except NoSuchElementException:
            document_type = "Articles"

        time.sleep(5)
        article_urls = []
        dois = []
        articles = driver.find_elements_by_xpath("//ul[@class='cit-list']/li/div[3]/ul/li[@class='first-item']/a")
        doi = driver.find_elements_by_xpath("//ul[@class='cit-list']/li/div[2]/cite/span[@class='cit-doi']")
        for a in articles:
            url = a.get_attribute("href")
            article_urls.append(url)

        for d in doi:
            identifier = re.search("doi:(.*)", d.text, re.IGNORECASE)
            dois.append(identifier.group(1))

        print('\n'.join(article_urls))
        print('\n'.join(dois))

        i = 0
        for url in article_urls:
            driver.get(url)
            try:
                headline = driver.find_element_by_xpath("//h1[@id='article-title-1']").text
                try:
                    subtitle = driver.find_element_by_xpath("//h2[@class='subtitle']").text
                except NoSuchElementException:
                    subtitle = ""
                document_title = headline + " " + subtitle
                document_title.strip()
            except NoSuchElementException:
                document_title = "None"

            try:
                abstract = driver.find_element_by_xpath("//div[@id='abstract-1']/p").text
            except NoSuchElementException:
                abstract = "None"

            try:
                received = driver.find_element_by_xpath("//li[@class='received']").text
                date = re.search("Received([\s\d\w]+)", received, re.IGNORECASE)
                manuscript_received_date = date.group(1).strip()
            except NoSuchElementException:
                manuscript_received_date = "None"

            try:
                accepted = driver.find_element_by_xpath("//li[@class='accepted']").text
                date = re.search("Accepted([\s\d\w]+)", accepted, re.IGNORECASE)
                manuscript_accepted_date = date.group(1).strip()
            except NoSuchElementException:
                manuscript_accepted_date = "None"

            try:
                jels = []
                classes = driver.find_elements_by_xpath("//ul[@class='kwd-group']/li/span")
                if len(classes) == 0:
                    jel_classification = "None"
                else:
                    for c in classes:
                        jels.append(c.text)
                    jel_classification = ", ".join(jels)
            except NoSuchElementException:
                jel_classification = "None"

            try:
                names = []
                auth_names = driver.find_elements_by_xpath("//li[contains(@id, 'contrib')]/span[@class='name']")
                j = 1
                k = 0
                for n in auth_names:
                    names.append(n.text)

                affiliations = []
                show_affs = driver.find_element_by_xpath("//p[@class='affiliation-list-reveal']/a")
                driver.execute_script("arguments[0].click();", show_affs)
                affs = driver.find_elements_by_xpath("//ol[contains(@class,'affiliation-list')]/li/address")
                for a in affs:
                    affiliations.append(a.text)
                
                if len(affiliations) < len(names):
                    affiliations.clear()
                    for name in names:
                        affiliations.append("None")

                for name in names:
                    author_data = [dois[i], name,  j, affiliations[k]]
                    j += 1
                    k += 1
                    print(author_data)
                    author_writer.writerow(author_data)
                    author_data.clear()
            except NoSuchElementException:
                for name in names:
                    author_data = [dois[i], name, j, "None"]
                    print(author_data)
                    author_writer.writerow(author_data)
                    author_data.clear()
                    j += 1

            temp_article_list = [volume, issue, document_title, document_type, issue_date, publication_date, manuscript_received_date, manuscript_accepted_date, dois[i], abstract, jel_classification]
            article_list = article_data + temp_article_list
            i += 1

            print('\n'.join(article_list))
            article_writer.writerow(article_list)
    
        article_urls.clear()
    issue_list.clear()

# Close the driver and csv files when we're done.

articles_file.close()
authors_file.close()
driver.close()
