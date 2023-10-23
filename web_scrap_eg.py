from bs4 import BeautifulSoup
import requests
import time
# pip install lxml

print("Put skill not familiar with")
unfamiliar_skill = input('>')

print(f'filtering out {unfamiliar_skill}')

def find_jobs():
    html_text = requests.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=python&txtLocation=').text
    # print(html_text)
    soup = BeautifulSoup(html_text,'lxml')
    jobs = soup.find_all('li', class_ = 'clearfix job-bx wht-shd-bx')
    # print(job)

    for index,job in enumerate(jobs):
        publish_date = job.find('span', class_="sim-posted").span.text
        # print(publish_date)

        if 'few' in publish_date:
            company_name = job.find('h3',class_ = 'joblist-comp-name').text.replace(" ", "")
            # print(company_name)
            skills = job.find('span',class_ = 'srp-skills').text.strip().replace(" ","")
            # print(skills)

            more_info = job.header.h2.a['href']
            if unfamiliar_skill not in skills:

                with open(f'posts/{index}.txt', 'w') as f:
                    f.write(f'Company Name: {company_name.strip()} \n')
                    f.write(f'Req skills: {skills.strip()} \n')
                    f.write(f"More info: {more_info}\n")
                print(f'File svae: {index}.txt')
                    


if __name__ == '__main__':
    while True:
        find_jobs()
        time_wait = 10
        print(f'waiting for for {time_wait} minutes..')
        time.sleep(time_wait*60)

