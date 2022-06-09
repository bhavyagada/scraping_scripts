# Imports

import re
import csv
import sys
import time
from os import path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# CSV Header and Data Lists

article_header = ["issn", "e_issn", "publication_name", "volume", "issue", "document_title", "document_type", 
                "issue_date", "publication_date", "digital_object_identifier", "abstract", "manuscript_received_date", 
                "manuscript_revised_date", "first_published_date", "ver_of_record_online_date", "keywords"]
article_data = ["1050-5164", "2168-8737", "The Annals of Applied Probability"]

author_header = ["digital_object_identifier", "co_author_name", "co_author_order", "co_author_affiliation"]

# Write to CSV files

try:
    # Article Writer
    if path.exists('Articles-The Annals of Applied Probability.csv') == False:
        articles_file = open('Articles-The Annals of Applied Probability.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)
        article_writer.writerow(article_header)
    else:
        articles_file = open('Articles-The Annals of Applied Probability.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)

    # Author Writer
    if path.exists('Authors-The Annals of Applied Probability.csv') == False:
        authors_file = open('Authors-The Annals of Applied Probability.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
        author_writer.writerow(author_header)
    else:
        authors_file = open('Authors-The Annals of Applied Probability.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
except Exception as e:
    articles_file.close()
    authors_file.close()
    print(e)

# Browse

driver = webdriver.Chrome(executable_path="C:\\Users\\User\\Desktop\\Scraping\\chromedriver")

url = "https://projecteuclid.org/journals/annals-of-applied-probability/issues"
driver.get(url)

def browse_volumes_page():
    volume_url_list = []
    issue_url_list = []
    
    volumes = driver.find_elements_by_xpath("//a[@class='IssueByYearInnerText']")
    for v in volumes:
        url = v.get_attribute("href")
        volume_url_list.append(url)
    
    for v_url in volume_url_list:
        driver.get(v_url)
        issues = driver.find_elements_by_xpath("//div[@class='row JournalsBrowseRowPadding1']/div/div/a")
        for i in issues:
            url = i.get_attribute("href")
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

    try:
        document_type = driver.find_element_by_xpath("//span[@id='Articles']").text
        articles = driver.find_elements_by_xpath("//div[@id='divArticlesLINEITEMSTop']/div/div[1]/div[2]/div[2]/a")
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
                active = driver.find_element_by_xpath("//li[@class='dropdown dropdownwidth1 active']").text
                if active != "ABOUT":
                    try:
                        about = driver.find_element_by_xpath("//div[@id='navbar']/ul/li[1]/a")
                        driver.execute_script("arguments[0].click();", about)
                        time.sleep(2)
                    except NoSuchElementException:
                        print(e)

                try:
                    vol_issue_date = driver.find_element_by_xpath("//div[@class='KeyWordsPanel']/div/div[2]").text
                    vid_list = vol_issue_date.split("•")
                    volume_num = re.search("Vol.([\s\d\w]+)", vid_list[0], re.IGNORECASE)
                    issue_num = re.search("No.([\s\d\w]+)", vid_list[1], re.IGNORECASE)
                    volume = volume_num.group(1).strip()
                    issue = issue_num.group(1).strip()
                    issue_date = vid_list[2]
                    publication_date = issue_date
                except NoSuchElementException:
                    volume = "None"
                    issue = "None"
                    issue_date = "None"
                    publication_date = "None"
                
                try:
                    document_title = driver.find_element_by_xpath("//text[@class='ProceedingsArticleOpenAccessHeaderText']").text
                    document_title = re.sub("\n", "", document_title)
                except NoSuchElementException:
                    document_title = "None"
                
                try:
                    abstract = driver.find_element_by_xpath("//text[@class='ArticleContentText'][1]/div").text
                    abstract = re.sub("\n", "", abstract)
                except NoSuchElementException:
                    abstract = "None"
                
                try:
                    doi = driver.find_elements_by_xpath("//div[@class='row ArticleContentRow']/text[2]/p/span")
                    if doi:
                        digital_object_identifier = doi[-1].text
                except NoSuchElementException:
                    doi = driver.find_elements_by_xpath("//div[@class='row ArticleContentRow']/i/text/p/span")
                    if doi:
                        digital_object_identifier = doi[-1].text

                try:
                    mrd = driver.find_element_by_xpath("//span[contains(text(), 'Received')]").text
                    received_date = re.search(": (.*)", mrd, re.IGNORECASE)
                    manuscript_received_date = received_date.group(1).strip()
                except NoSuchElementException:
                    manuscript_received_date = "None"
                
                try:
                    mred = driver.find_element_by_xpath("//span[contains(text(), 'Revised')]").text
                    revised_date = re.search(": (.*)", mred, re.IGNORECASE)
                    manuscript_revised_date = revised_date.group(1).strip()
                except NoSuchElementException:
                    manuscript_revised_date = "None"
                
                try:
                    fpd = driver.find_element_by_xpath("//span[contains(text(), 'Published')]").text
                    published_date = re.search(": (.*)", fpd, re.IGNORECASE)
                    first_published_date = published_date.group(1).strip()
                except NoSuchElementException:
                    first_published_date = "None"
                
                try:
                    rod = driver.find_element_by_xpath("//div[contains(text(), 'First available')]").text
                    online_date = re.search(": (.*)", rod, re.IGNORECASE)
                    ver_of_record_online_date = online_date.group(1).strip()
                except NoSuchElementException:
                    ver_of_record_online_date = "None"

                try:
                    words = driver.find_elements_by_xpath("//div[contains(text(), 'Keywords:')]/a")
                    keys = []
                    for w in words:
                        keys.append(w.text)
                    if len(keys) != 0:
                        keywords = ', '.join(keys)
                        keywords = re.sub("\n", "", keywords)
                    else:
                        keywords = "None"
                except NoSuchElementException:
                    keywords = "None"
                
                temp_article_list = [volume, issue, document_title, document_type, issue_date, publication_date, digital_object_identifier, abstract, manuscript_received_date, manuscript_revised_date, first_published_date, ver_of_record_online_date, keywords]
                article_list = article_data + temp_article_list
                article_writer.writerow(article_list)

                print('\n'.join(article_list))

                try:
                    author_dict = {}
                    order_dict = {}
                    affiliation_dict = {}
                    authors_list = []
                    data = []
                    author_names = driver.find_elements_by_xpath("//text[@class='ProceedingsArticleOpenAccessText']/span")

                    for name in author_names:
                        authors_list.append(name.text)

                    i = 1
                    for a in authors_list:
                        order_dict[a] = i
                        author_dict[a] = []
                        i += 1
                    
                    try:
                        author_details = driver.find_element_by_xpath("//a[@class='ProceedingsArticleOpenAccessAnchorText']")
                        driver.execute_script("arguments[0].click();", author_details)
                        co_authors = driver.find_element_by_xpath("//div[@id='affiliations']/b").text

                        for author in authors_list:
                            order = re.search(author+"([\d,]+)|"+author+".([\d,]+)", co_authors, re.IGNORECASE)
                            if order and order.group(1) != None:
                                for g in order.group(1):
                                    if g.isdigit():
                                        author_dict[author].append(g)
                            elif order and order.group(2) != None:
                                for g in order.group(2):
                                    if g.isdigit():
                                        author_dict[author].append(g)
                            else:
                                author_dict[author] = "None"
                        
                        print(order_dict)

                        affiliation_list = driver.find_element_by_xpath("//div[@id='affiliations']").text
                        affiliations = affiliation_list.split(co_authors, 1)[1]
                        orders = re.findall("[\d]+", affiliations)
                        aff_list = re.findall("[^\d\n]+", affiliations)

                        i = 0
                        for a in range(len(aff_list)):
                            if orders[i].isdigit():
                                affiliation_dict[orders[i]] = aff_list[i]
                            i += 1

                        author_data = []
                        for key in author_dict:
                            all_affiliations = []
                            for k in author_dict[key]:
                                if k in affiliation_dict:
                                    all_affiliations.append(affiliation_dict[k])
                                else:
                                    data = [digital_object_identifier, key, order_dict[key], "No Affiliation"]
                                    author_data.append(data)
                            data = [digital_object_identifier, key, order_dict[key], ", ".join(all_affiliations)]
                            author_data.append(data)

                        for data in author_data:
                            print(data)
                            author_writer.writerow(data)
                    except NoSuchElementException:
                        author_data = []
                        for key in author_dict:
                            data = [digital_object_identifier, key, order_dict[key], "No Affiliation"]
                            author_data.append(data)

                        for data in author_data:
                            print(data)
                            author_writer.writerow(data)

                except NoSuchElementException:
                    author_data = [digital_object_identifier, "None", "None", "None"]
                    author_writer.writerow(author_data)

        article_urls.clear()
    except NoSuchElementException:
        continue

# Close the driver and csv files when we're done.

articles_file.close()
authors_file.close()
driver.close()
