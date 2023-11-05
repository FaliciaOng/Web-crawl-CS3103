
from bs4 import BeautifulSoup
import requests
from multiprocessing import Process
import multiprocessing
import time
from colorama import Fore
from http import cookiejar
import pandas
import os
cwd = os.getcwd()
print(cwd)


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False

def write_to_file(local_url_index,num_of_url,new_urls,df_row,access_lock):
    access_lock.acquire()
    df = pandas.read_csv('C:/Users/Siew Yang Zhi/Desktop/Uni Stuff/Y4 Sem 1/CS3103/Assignment/Assignment 4/url_links.csv') #Get updated content of file
    df.iloc[local_url_index] = df_row
    for i in range(len(new_urls)):
        df = df.append(new_urls.iloc[i],ignore_index=True) 
        num_of_url.value += 1
    df.to_csv('C:/Users/Siew Yang Zhi/Desktop/Uni Stuff/Y4 Sem 1/CS3103/Assignment/Assignment 4/url_links.csv',index=False)
    access_lock.release()

def find_jobs(main_url,full_url, post_name, color):
    new_urls = pandas.DataFrame(columns=('URL', 'Respond Time', 'IP Of Server'))
    s = requests.Session()
    s.cookies.set_policy(BlockAll())

    html_text = s.get(full_url).text
    soup = BeautifulSoup(html_text,'lxml')

    # grab body
    body = soup.body
    for keyword in (body.strings):
        keyword_lowercase = keyword.lower().strip()
        if keyword_lowercase != "\n" and keyword_lowercase != "":
            # must use .contains()
            keys = keyword_lowercase.split()
            print(keys)

    time.sleep(0.1)
    # grab url 
    links = soup.find_all("a") 
    for link in links:
        append_url = str(link.get("href"))
        if append_url[0] == "/":
            append_url = main_url + append_url
        list_row = [append_url, 1, "127.0.0.1"]
        new_urls.loc[len(new_urls)] = list_row
    return new_urls

def getURLContent(df_row):
    respond_time = 1 #Now hardcode to be 1,to be change with actual value
    server_ip = "127.0.0.1" #Now hardocde to 127.0.0.1 to be change in future.
    query = '/Engineer-jobs'
    url = df_row['URL']
    df_row['Respond Time'] = respond_time
    df_row['IP Of Server'] = server_ip
    full_query = url + query
    new_urls = find_jobs(url,full_query, 'posts', Fore.RED)
    return new_urls,df_row

def read_from_file(url_index,num_of_url,access_lock):
    # acquire the lock
    access_lock.acquire()
    local_url_index = url_index.value
    df = pandas.read_csv('C:/Users/Siew Yang Zhi/Desktop/Uni Stuff/Y4 Sem 1/CS3103/Assignment/Assignment 4/url_links.csv') #Get updated content of file
    url_index.value += 1
    access_lock.release()
    df_row = df.iloc[local_url_index]
    new_urls,df_row = getURLContent(df_row)
    write_to_file(local_url_index,num_of_url,new_urls,df_row,access_lock)

# future work
def pool_manager():
    pass  

if __name__ == '__main__':
    url_index = multiprocessing.Value("i",0)
    num_of_url = multiprocessing.Value("i",1)
    access_lock = multiprocessing.Lock()
    while (True):
        if (url_index.value > 2):
            break
        
        if (num_of_url.value != url_index.value):
            p = Process(target=read_from_file, args=(url_index,num_of_url,access_lock))
            p.start()
            p.join()
        
        time.sleep(1)

    url = 'https://www.jobstreet.com.sg'
    #query = '/Engineer-jobs'
    # full_query = 'https://sg.jobsdb.com/j?sp=homepage&trigger_source=homepage&q=engineering&l='
    # full_query = 'https://jobscentral.com.sg/jobs?title=engineer'
    #full_query = url + query

    # print(full_query)
    #process1 = Process(target=find_jobs, args=(url,full_query, 'posts', Fore.RED))

    #process1.start()
    #process1.join()
    #print("process ended")