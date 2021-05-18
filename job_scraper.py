# Imports
from datetime import datetime
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from urllib.request import Request, urlopen

class JobPostingScraper:
    """
    A scraper for Indeed US that populates job postings into a DataFrame.
    """
    def __init__(self):
        pass

    def create_job_urls(self, companies) -> list:
        '''
        Generates the URLS for each search term given
        '''
        url_list = []
        for company in companies:
            company = company.replace(" ", "+")
            url = "https://www.indeed.com/jobs?q={}&l=".format(company)
            url_list.append(url)
        return url_list

    def get_data_from_page(self, data_collected: list, soup) -> list:
        '''
        Collects all page information depending on number of pages selected 
        '''
        job_posts = []
        for div in soup.findAll('div', attrs={'class': 'jobsearch-SerpJobCard unifiedRow row result'}):
            job = dict()
            job = self.extract_data_points(job, div)
            job_posts.append(div['data-jk'])
            single_job_post_extension_url = "https://www.indeed.com/viewjob?jk=" + div['data-jk']
            job['url'] = single_job_post_extension_url
            req = Request(single_job_post_extension_url)
            job_page = urlopen(req).read()
            # job_page = requests.get(single_job_post_extension_url)
            job_soup = BeautifulSoup(job_page, 'html.parser')

            for inside_div in job_soup.findAll('div', attrs={"class": "jobsearch-jobDescriptionText"}):
                details = inside_div.text.strip() + "..." # change for longer description
                job['details'] = re.sub(' +', ' ', details.replace("\n", " "))
                data_collected.append(job)
        return data_collected


    def scrape_data(self, url_to_scrape: str, number_of_pages: int) -> list:
        '''
        Scrapes data from Indeed page.
        '''
        data_collected = []
        for i in range(0, number_of_pages):
            extension = ''
            if i is not 0:
                extension = "&start".format(i*10)
            url = url_to_scrape + extension
            req = Request(url)
            page = urlopen(req).read()
            soup = BeautifulSoup(page, 'html.parser')
            data_collected = self.get_data_from_page(data_collected, soup)
        return data_collected, soup

   
    def extract_data_points(self, job, div) -> dict:
        '''
        Searches for specific information on page
        '''
        for a in div.findAll(name='a', attrs={'data-tn-element': 'jobTitle'}):
            job['title'] = a['title']
        for a1 in div.findAll('a', attrs={'data-tn-element': 'companyName'}):
            job['companyName'] = a1.text.strip()
        for span in div.findAll('span', attrs={'class': 'ratingsContent'}):
            job['rating'] = span.text.strip()
        for span1 in div.findAll('span', attrs={'class': 'location accessible-contrast-color-location'}):
            job['location'] = span1.text.strip()
        for div1 in div.findAll('div', attrs={'class': 'summary'}):
            summary = div1.text.strip()
            job['summary'] = summary
            # job['summary'] = re.sub(' +', ' ', summary.replace("\n", ""))
        for span2 in div.findAll('span', attrs={'class': 'date'}):
            job['date'] = span2.text.strip()
        return job

    def create_job_dataset(self, url_list):
        '''
        Returns each company search into list.
        '''
        jobs_data = []
        for url in url_list:
            jobs = self.scrape_data(url, 3)
            jobs_data.append(jobs)
        return jobs_data
        
    def join_job_dataset(self, jobs_list) -> DataFrame:
        '''
        Takes nested dictionaries and concatenates into one DataFrame object
        '''
        jobs_df = pd.DataFrame()
        for data in jobs_list:
            jobs_df = pd.concat([jobs_df, pd.DataFrame(data)], ignore_index=True)
        return jobs_df