# Imports

import time
import re
import csv
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# CSV Header and Data Lists - Articles

article_data = ["0001-8392", "1930-3815", "Administrative Science Quarterly"]

# Write to CSV files

try:
    # Article Writer
    articles_file = open('Articles-Administrative Science Quarterly.csv', mode='a+', newline='', encoding='UTF-8')
    article_writer = csv.writer(articles_file)

    # Author Writer
    authors_file = open('Authors-Administrative Science Quarterly.csv', mode='a+', newline='', encoding='UTF-8')
    author_writer = csv.writer(authors_file)
except Exception as e:
    articles_file.close()
    authors_file.close()
    print(e)

# Browse

driver = webdriver.Chrome(executable_path="C:\\Users\\User\\Desktop\\GScholar\\chromedriver")

url = "https://journals.sagepub.com/loi/ASQ"
driver.get(url)

def browse_volumes_page():
    issue_url_list = []

    volume_expanders = driver.find_elements_by_css_selector("div.slider")
    for v_e in volume_expanders:
        driver.execute_script("arguments[0].setAttribute('class','slider opened');", v_e)
    
    issue_expanders = driver.find_elements_by_css_selector("a.title.expander")
    for i_e in issue_expanders:
        driver.execute_script("arguments[0].setAttribute('class','title expander open');", i_e)
        driver.execute_script("arguments[0].setAttribute('aria_expanded','true');", i_e)

    issues_visibility = driver.find_elements_by_css_selector("div.js_issue")    
    for i_v in issues_visibility:
        driver.execute_script("arguments[0].setAttribute('class','js_issue');", i_v)
    
    volumes = driver.find_elements_by_xpath("//div[@class='issueGroup h5']/div")
    for v in volumes:
        issues = v.find_elements_by_xpath(".//div")
        for i in issues:
            issue_url = i.find_element_by_xpath(".//a")
            url = issue_url.get_attribute("href")
            issue_url_list.append(url)

    return issue_url_list

issue_urls = browse_volumes_page()
print(issue_urls)

latest_issue = driver.find_element_by_xpath("//div[@class='issueGroup h5']/div/div/a/span/span[@class='currentLabel']/parent::span/parent::a")
latest_url = latest_issue.get_attribute("href")

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
    time.sleep(1)
    document_type = "Articles"
    articles = driver.find_elements_by_xpath("//td/span[contains(text(), 'Article')]/parent::td/div[@class='art_title linkable']/a")

    for a in articles:
        url = a.get_attribute("href")
        article_urls.append(url)
    print(article_urls)

    for url in article_urls:
        driver.get(url)
        url_type = driver.execute_script("return document.contentType")
        time.sleep(1)
        article_info = driver.find_element_by_xpath("//td[@class='articleInfoLink']/a")
        driver.execute_script("arguments[0].click();", article_info)
        volume_issue = driver.find_element_by_xpath("//div[@class='Article information']/div/a").text
        nums = re.findall("[\d]+", volume_issue)
        volume = nums[0]
        issue = nums[1]
        pub_dates = driver.find_element_by_xpath("//div[@class='published-dates']").text
        dates = re.findall("[^:;]+", pub_dates)
        first_published_date = dates[1]
        publication_date = dates[-1]
        issue_published_date = publication_date
        document_title = driver.find_element_by_xpath("//div[@class='publicationContentTitle']/h1").text
        doi = driver.find_element_by_xpath("//div[@class='doiWidgetContainer']/a")
        digital_object_identifier = doi.get_attribute("href")
        try:
            abstract = driver.find_element_by_xpath("//div[@class='abstractSection abstractInFull']/p").text
            kwds = driver.find_elements_by_xpath("//span[@class='kwd']/a")
            kwd_list = []
            for k in kwds:
                kwd_list.append(k.text)
            
            keywords = ", ".join(kwd_list)
        except NoSuchElementException:
            abstract = "No Abstract"
            keywords = "No Keywords"

        # Articles
        temp_article_list = [volume, issue, document_title, document_type, publication_date, issue_published_date, first_published_date, digital_object_identifier, abstract, keywords]
        article_list = article_data + temp_article_list

        if url_type == 'application/pdf':
            article_type_pdf = article_data
            article_writer.writerow(article_type_pdf)
        else:
            article_writer.writerow(article_list)

        # Authors
        author_dict = {}
        affiliation_dict = {}
        co_authors = driver.find_elements_by_xpath("//span[@class='contribDegrees no-aff']")
        affiliations = driver.find_elements_by_xpath("//div[@class='artice-info-affiliation']")

        for ca in co_authors:
            try:
                author_name = ca.find_element(By.XPATH, "./child::a[@class='entryAuthor']")
                author_order = ca.find_elements(By.XPATH, "./child::sup")
                author_dict[author_name.text] = []
                for o in author_order:
                    order = o.text
                    if order.isdigit():
                        author_dict[author_name.text].append(o.text)
            except NoSuchElementException:
                author_dict[author_name.text].append('*')

        for aff in affiliations:
            try:
                affiliation = re.findall("[^\d]+", aff.text)
                aff_order = aff.find_element(By.XPATH, "./child::sup")
                affiliation_dict[aff_order.text] = affiliation[0]
            except NoSuchElementException:
                affiliation_dict['*'] = affiliation[0]

        co_author = []
        for key in author_dict:
            for k in author_dict[key]:
                if k in affiliation_dict:
                    co_author.extend([digital_object_identifier, key, k, affiliation_dict[k]])
                else:
                    co_author.extend([digital_object_identifier, key, k, "No Affiliations"])

                author_writer.writerow(co_author)
                co_author.clear()

    article_urls.clear()

# Close the WebDriver
driver.close()

# Close CSV files
articles_file.close()
authors_file.close()
