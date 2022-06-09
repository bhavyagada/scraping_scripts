# Imports

import re
import csv
import sys
import time
from random import choice
from os import path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# CSV Header and Data Lists

article_header = ["issn", "e_issn", "publication_name", "volume", "issue", "document_title", 
                "issue_date", "publication_date", "manuscript_received_date", "manuscript_revised_date", 
                "manuscript_accepted_date", "digital_object_identifier", "abstract", "keywords"]
article_data = ["0013-936X", "1520-5851", "Environmental Science and Technology"]

author_header = ["digital_object_identifier", "co_author_name", "co_author_order", "co_author_affiliation"]

# Write to CSV files

try:
    # Article Writer
    if path.exists('Articles-Environmental Science and Technology.csv') == False:
        articles_file = open('Articles-Environmental Science and Technology.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)
        article_writer.writerow(article_header)
    else:
        articles_file = open('Articles-Environmental Science and Technology.csv', mode='a+', newline='', encoding='UTF-8')
        article_writer = csv.writer(articles_file)

    # Author Writer
    if path.exists('Authors-Environmental Science and Technology.csv') == False:
        authors_file = open('Authors-Environmental Science and Technology.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
        author_writer.writerow(author_header)
    else:
        authors_file = open('Authors-Environmental Science and Technology.csv', mode='a+', newline='', encoding='UTF-8')
        author_writer = csv.writer(authors_file)
except Exception as e:
    articles_file.close()
    authors_file.close()
    print(e)

# Browse

# Function to use proxy IPs

# def get_proxy_driver():
#   while True:
#     try:
#         proxies = ['107.152.142.167:8000', '107.152.142.221:8000', '107.152.142.250:8000', '104.227.99.65:8000']
#         proxy = choice(proxies)
#         print(proxy)
#         options = webdriver.ChromeOptions()
#         options.add_argument('--proxy-server={}'.format(proxy))
#         driver = webdriver.Chrome(executable_path=r'C:\Users\User\Desktop\Scraping\chromedriver', options=options, service_args=["--verbose", "--log-path=C:\\Users\\User\\Desktop\\Scraping\\NOT DONE\\EST"])
#         options = webdriver.FirefoxOptions()
#         options.add_argument('--proxy-server={}'.format(proxy))
#         driver = webdriver.Firefox(executable_path=r'C:\Users\User\Desktop\Scraping\geckodriver')
#         return driver
#     except Exception as e:
#       print(e)

driver = webdriver.Chrome(executable_path=r'C:\Users\User\Desktop\Scraping\chromedriver')
url = "https://pubs.acs.org/loi/esthag"
driver.get(url)

year_url_list = []
years = driver.find_elements_by_xpath("//div[@class='scroll']/ul/li/a")
for y in years:
    yearurl = y.get_attribute("href")
    if yearurl != "":
        year_url_list.append(yearurl)

print('\n'.join(year_url_list))
for year in year_url_list:
    driver.get(year)

    issue_urls = []
    volumes = driver.find_elements_by_xpath("//div[@class='tab__content']/div/ul/li/div/a")
    for v in volumes:
        url = v.get_attribute("href")
        issue_urls.append(url)

    print('\n'.join(issue_urls))

    for url in issue_urls:
        driver.get(url)
        # time.sleep(5) # Time Delay
        try:
            volume_and_issue = driver.find_element_by_xpath("//div[@class='niHeader_about-meta']/span[2]").text
            vid_list = volume_and_issue.split(",")
            volume_num = re.search("Volume(.[\s\d\w-]+)", vid_list[0], re.IGNORECASE)
            issue_num = re.search("issue(.[\s\d\w-]+)", vid_list[1], re.IGNORECASE)
            volume = volume_num.group(1).strip()
            issue = issue_num.group(1).strip()
        except NoSuchElementException:
            volume = "None"
            issue = "None"

        article_urls = []
        articles = driver.find_elements_by_xpath("//h5[@class='issue-item_title']/a")
        for a in articles:
            aurl = a.get_attribute("href")
            article_urls.append(aurl)

        for url in article_urls:
            driver.get(url)
            # time.sleep(5) # Time Delay
            if len(article_urls) < 1:
                break
            else:
                try:
                    document_title = driver.find_element_by_xpath("//h1[@class='article_header-title']/span").text
                    document_title = re.sub("\n", "", document_title)
                except NoSuchElementException:
                    document_title = "None"

                try:
                    digital_object_identifier = driver.find_element_by_xpath("//div[@class='article_header-doiurl']/a").text
                except NoSuchElementException:
                    digital_object_identifier = "None"

                try:
                    abstract = driver.find_element_by_xpath("//p[@class='articleBody_abstractText']").text
                    abstract = re.sub("\n", "", abstract)
                except NoSuchElementException:
                    abstract = "None"

                try:
                    all_dates = []
                    dates = driver.find_element_by_xpath("//div[@class='article_header-history base dropBlock']/a")
                    driver.execute_script("arguments[0].click();", dates)
                    all = driver.find_elements_by_xpath("//div[@class='dropBlock__holder js--open']//div/ul/li")
                    for a in all:
                        all_dates.append(a.text)

                    for date in all_dates:
                        mrd = re.search("Received", date, re.IGNORECASE)
                        if mrd:
                            manuscript_received_date = re.sub("Received", "", date).strip()
                            break
                        else:
                            manuscript_received_date = "None"
                    
                    for date in all_dates:
                        mred = re.search("Revised", date, re.IGNORECASE)
                        if mred:
                            manuscript_revised_date = re.sub("Revised", "", date).strip()
                            break
                        else:
                            manuscript_revised_date = "None"
                    
                    for date in all_dates:
                        mad = re.search("Accepted", date, re.IGNORECASE)
                        if mad:
                            manuscript_accepted_date = re.sub("Accepted", "", date).strip()
                            break
                        else:
                            manuscript_accepted_date = "None"
                    
                    for date in all_dates:
                        pd = re.search("Published online", date, re.IGNORECASE)
                        if pd:
                            publication_date = re.sub("Published online", "", date).strip()
                            break
                        else:
                            publication_date = "None"
                    
                    for date in all_dates:
                        id = re.search("Published inissue", date, re.IGNORECASE)
                        if id:
                            issue_date = re.sub("Published inissue", "", date).strip()
                            break
                        else:
                            issue_date = "None"
                except NoSuchElementException:
                    manuscript_received_date = "None"
                    manuscript_revised_date = "None"
                    manuscript_accepted_date = "None"
                    publication_date = "None"
                    issue_date = "None"

                try:
                    key_words = []
                    keys = driver.find_elements_by_xpath("//div[@class='article_keywords-container']/ul/li/a")
                    for k in keys:
                        key_words.append(k.text)

                    if len(key_words) == 0:
                        keywords = "None"
                    else:
                        keywords = ", ".join(key_words)
                except NoSuchElementException:
                    keywords = "None"

                temp_article_list = [volume, issue, document_title, issue_date, publication_date, manuscript_received_date, manuscript_revised_date, manuscript_accepted_date, digital_object_identifier, abstract, keywords]
                article_list = article_data + temp_article_list

                article_writer.writerow(article_list)

                try:
                    authors = driver.find_elements_by_xpath("//ul[contains(@class,'loa')]/li/span/span[@class='hlFld-ContribAuthor']")
                    author_data = None
                    auth_data = None
                    if len(authors) == 0:
                        author_data = [digital_object_identifier, "None", "None", "None"]
                        author_writer.writerow(author_data)
                    else:
                        for i in range(len(authors)):
                            i += 1
                            try:
                                hover = driver.find_element_by_xpath("//ul[contains(@class,'loa')]/li["+str(i)+"]/span/span")
                                ActionChains(driver).move_to_element(hover).perform()
                                author_name = driver.find_element_by_xpath("//ul[@class='loa']/li["+str(i)+"]/span/div/div").text
                                author_order = i
                                author_affiliation = driver.find_element_by_xpath("//ul[@class='loa']/li["+str(i)+"]/span/div/div[2]/div").text
                                author_data = [digital_object_identifier, author_name, author_order, author_affiliation]
                                print(author_data)
                                author_writer.writerow(author_data)
                                author_data.clear()
                            except Exception as e:
                                auth_data = [digital_object_identifier, "None", "None", "None"]

                        if author_data is None and auth_data is None:
                            try:
                                for i in range(len(authors)):
                                    author_name = driver.find_element_by_xpath("//ul[contains(@class,'loa')]/li["+str(i)+"]/span/span[1]/a").text
                                    author_order = i
                                    author_data = [digital_object_identifier, author_name, author_order, "None"]
                                    print(author_data)
                                    author_writer.writerow(author_data)
                                    author_data.clear()
                            except Exception as e:
                                author_data = [digital_object_identifier, "None", "None", "None"]
                                author_writer.writerow(author_data)
                        elif author_data is not None:
                            break
                        else:
                            author_writer.writerow(auth_data)
                except NoSuchElementException:
                    author_data = [digital_object_identifier, "None", "None", "None"]
                    author_writer.writerow(author_data)

# Close the driver and csv files when we're done.

articles_file.close()
authors_file.close()
driver.close()
