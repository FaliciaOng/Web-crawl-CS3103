from bs4 import BeautifulSoup
import requests
from multiprocessing import Process
import time
from colorama import Fore
# pip install lxml



def find_jobs(url, post_name, color):
    unfamiliar_skill = 'css'
    html_text = requests.get(url).text
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

                with open(f'{post_name}/{index}.txt', 'w') as f:
                    f.write(f'Company Name: {company_name.strip()} \n')
                    f.write(f'Req skills: {skills.strip()} \n')
                    f.write(f"More info: {more_info}\n")
                print(color+f'File svae: {index}.txt')
            time.sleep(0.5)
                    


if __name__ == '__main__':
    # print("Put skill not familiar with")
    # unfamiliar_skill = input('>')

    # print(f'filtering out {unfamiliar_skill}')
    process1 = Process(target=find_jobs, args=('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=python&txtLocation=', 'posts', Fore.RED))
    process2 = Process(target=find_jobs,args=('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=java&txtLocation=', 'posts_two',Fore.YELLOW))
    # process3 = Process(target=find_jobs,args=('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=java&txtLocation=', 'posts_two',Fore.))
    process2.start()
    # process3.start()
    process1.start()
    process1.join()
    process2.join()
    # process3.join()
    print("process ended")


    # while True:
        
    #     time_wait = 10
    #     # print(f'waiting for for {time_wait} minutes..')
    #     # time.sleep(time_wait*60)

