
from bs4 import BeautifulSoup
import requests
import multiprocessing
import time
from colorama import Fore
from http import cookiejar
import pandas
import os
from multiprocessing import Manager
from multiprocessing.pool import Pool
from signal import signal, SIGINT
import warnings
import csv
from collections import deque

warnings.simplefilter('ignore')

csv_filename = "url_links.csv"
# csv_filename = "C:\\Users\\Siew Yang Zhi\\Desktop\\Uni Stuff\\Y4 Sem 1\\CS3103\\Assignment\\Assignment 4\\url_links.csv"

list_of_urls = deque()
def main():
    global list_of_urls
    pool = Pool() 
    manager = Manager()
    
    url_index = manager.Value("i",0)
    processed_url = manager.Value("i",0)
    num_of_url = manager.Value("i",1)
    access_lock = manager.Lock()
    dict_of_jobs = manager.dict()
    exit_prog = manager.Value("i",0) # 0 = False, 1 = True

    dict_of_jobs['project'] = 0
    dict_of_jobs['software'] = 0
    dict_of_jobs['chemical'] = 0
    dict_of_jobs['electrical'] = 0
    
    numer_of_processes = 3
    print(type(url_index),url_index)
    color = [Fore.RED,Fore.BLUE,Fore.CYAN]
    v = 0
    visited = set()
    
    try:
        # allow us to end the code
        signal(SIGINT, handler)
        with Pool(numer_of_processes) as pool:
            while True:
                v = v%3
                if (processed_url.value > 3):
                    break
                
                #url_index == num of url in dequeue and num_of_url = num of url in the file.
                if (url_index.value != num_of_url.value):
                    read_from_file(url_index,num_of_url,access_lock,color,dict_of_jobs)

                if list_of_urls:
                    (df_row,index) = list_of_urls.popleft()
                    print("Process " + str(df_row['URL']))
                    pool.apply_async(process_url,(df_row,num_of_url,color[v],access_lock,dict_of_jobs,index))
                    visited.add(url_index.value)
                    processed_url.value += 1
                    v += 1
                time.sleep(1)

            print("Abouting to close pool..")
            pool.close()
            print("sucessfully close")
            pool.join()
            print("sucessfully close join")
            
            
    except Exception as e:
        print(e, "tye")

    print(dict_of_jobs)
    

    header = ['electrical', 'software', 'chemical', 'project']
    data = [dict_of_jobs['electrical'], dict_of_jobs['software'], dict_of_jobs['chemical'], dict_of_jobs['project']]

    with open('findings.csv', 'w', encoding='UTF8',newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write the data
        writer.writerow(data)

def handler(signalnum, frame):
    raise TypeError


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False

def write_to_file(local_url_index,num_of_url,new_urls,df_row,access_lock):
    access_lock.acquire()
    df = pandas.read_csv(csv_filename) #Get updated content of file
    df.iloc[local_url_index] = df_row
    #print(df)
    #all_new_url = pandas.concat([pandas.DataFrame([new_urls.iloc[i]]) for i in range(len(new_urls))]], ignore_index=True)
    #all_new_url = pandas.concat(new_urls, ignore_index=True)
    df = pandas.concat([df,new_urls],ignore_index = True)
    num_of_url.value += len(new_urls)
    #for i in range(len(new_urls)):
        #print(new_urls.iloc[i])
    #    df = df.append(new_urls.iloc[i],ignore_index=True)
    #    df = pandas.concat([df,new_urls.iloc[i]],ignore_index=True,axis=0)
    #    num_of_url.value += 1
    df.to_csv(csv_filename,index=False)
    access_lock.release()

def find_jobs(main_url,full_url, post_name, color,access_lock,dict_of_jobs):
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
            # print(color+f'{keys}')
            # print(type(keys))

            for key in keys:
                normal_string="".join(ch for ch in key if ch.isalnum())
                # print(normal_string)
                if normal_string == 'chemical':
                    #  print(Fore.YELLOW+"HIT", normal_string)
                     dict_of_jobs['chemical'] +=1 
                elif normal_string == 'project':
                    # print(Fore.WHITE+"HIT", normal_string)
                    dict_of_jobs['project'] +=1 

                elif normal_string == 'software':
                    # print(Fore.GREEN+"HIT", normal_string)
                    dict_of_jobs['software'] +=1 

                elif normal_string== 'electrical':
                    # print(Fore.CYAN+"HIT", normal_string)
                    dict_of_jobs['electrical'] += 1
                    
                    


            # if keys in dict_of_jobs:
            #     dict_of_jobs[keys] += 1
                

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

''' TODO add query'''
def getURLContent(df_row,color,access_lock,dict_of_jobs):
    respond_time = 1 #Now hardcode to be 1,to be change with actual value
    server_ip = "127.0.0.1" #Now hardocde to 127.0.0.1 to be change in future.
    url = df_row['URL']
    df_row['Respond Time'] = respond_time
    df_row['IP Of Server'] = server_ip
    full_query = url 
    new_urls = find_jobs(url,full_query, 'posts', color,access_lock,dict_of_jobs)
    return new_urls,df_row

def read_from_file(url_index,num_of_url,access_lock,color,dict_of_jobs):
    # acquire the lock
    global list_of_urls
    try:
        access_lock.acquire()
        local_num_of_url = num_of_url.value
        print("local_num_of_url:",local_num_of_url)
        print("url_index.value:",url_index.value)
        df = pandas.read_csv(csv_filename)
        access_lock.release()
        #Get updated content of file
        for i in range(url_index.value,local_num_of_url):
            list_of_urls.append((df.iloc[i],i))
            url_index.value += 1
    except Exception as e:
        print(e, "@ file ")

"""         print("CALLED Twice",num_of_url.value, url_index.value)
        signal(SIGINT, handler)
        access_lock.acquire()
        local_url_index = url_index.value
        url_index.value += 1
        df = pandas.read_csv(csv_filename) #Get updated content of file
        access_lock.release()
        df_row = df.iloc[local_url_index]
        new_urls,df_row = getURLContent(df_row,color,access_lock,dict_of_jobs)
        write_to_file(local_url_index,num_of_url,new_urls,df_row,access_lock)
        print("THREAD COMPLETED") """

def process_url(df_row,num_of_url,color,access_lock,dict_of_jobs,index):
    new_urls,df_row = getURLContent(df_row,color,access_lock,dict_of_jobs)
    write_to_file(index,num_of_url,new_urls,df_row,access_lock)


# future work
def pool_manager():
    pass  

if __name__ == '__main__':
    main()



