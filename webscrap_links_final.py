"""
Source: https://stackoverflow.com/questions/17037668/how-to-disable-cookie-handling-with-the-python-requests-library
"""
from bs4 import BeautifulSoup
import requests
import multiprocessing
import time
from colorama import Fore
from http import cookiejar
import pandas
import os
import socket 
from multiprocessing import Manager
from multiprocessing.pool import Pool
from signal import signal, SIGINT
import warnings
import csv
from collections import deque
import sys
from ip2geotools.databases.noncommercial import DbIpCity
import winsound
warnings.simplefilter('ignore')



def make_noise():
  duration = 2000  # milliseconds
  freq = 440  # Hz
  winsound.Beep(freq, duration)

csv_filename = "url_links.csv"

list_of_urls = deque()


def main():
    global list_of_urls
    startTime = time.time()
    timeToRun = 1800 # 30 minutes
    endTime = startTime + timeToRun

    pool = Pool() 
    manager = Manager()
    
    url_index = manager.Value("i",0)
    processed_url = manager.Value("i",0)
    num_of_url = manager.Value("i",1)
    access_lock = manager.Lock()
    dict_of_jobs = manager.dict()
    dict_visited_links = manager.dict()

    dict_of_jobs['project'] = 0
    dict_of_jobs['service'] = 0
    dict_of_jobs['chemical'] = 0
    dict_of_jobs['electrical'] = 0
    dict_of_jobs['software'] = 0
    dict_of_jobs['mechanical'] = 0

    with open(csv_filename, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        for row in datareader:
            if (row[0] != "URL"):
                dict_visited_links[row[0]] = 1
                
    #print(dict_visited_links)
    
    number_of_processes = 5
    # print(type(url_index),url_index)
    color = [Fore.RED,Fore.BLUE,Fore.YELLOW,Fore.GREEN,Fore.WHITE]
    v = 0
    visited = set()
    
    try:
        # Allow us to end the code
        signal(SIGINT, handler)
        # Ensures at any point of time the number of process running is number_of_processes
        with Pool(number_of_processes) as pool:
            while True:
                v = v%number_of_processes

                if time.time() >= endTime:
                    print(f"=========================TERMINATED AFTER {timeToRun} seconds ================================")
                    break
                
                # Calls the read_from_file when the index of the last URL added to the queue does not match the total number of URLs in the CSV file.
                # When this happens, it means there are new URLs within the CSV file.
                if (url_index.value != num_of_url.value):
                    read_from_file(url_index,num_of_url,access_lock,color,dict_of_jobs)
                
                # If there are entries within the list_of_url, pop the first tuple in the queue which contains the URL and its index in the CSV file.
                # Start a new thread which runs process_url to crawl the URL.
                # Update the num of URL that has been processed by the program.
                if list_of_urls:
                    (df_row,index) = list_of_urls.popleft()
                    print(color[v]+"Process " + str(df_row['URL']))
                    # Start process
                    pool.apply_async(process_url,(df_row,num_of_url,color[v],access_lock,dict_of_jobs,index,dict_visited_links))
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
        print(e, "@ main")

    print(dict_of_jobs)
    
    # Store findings into a new file after terminating all threads
    header = ['electrical', 'service', 'chemical', 'project','mechanical','software']
    data = [dict_of_jobs['electrical'], dict_of_jobs['service'], dict_of_jobs['chemical'], dict_of_jobs['project'],dict_of_jobs['mechanical'],dict_of_jobs['software']]

    with open('findings.csv', 'w', encoding='UTF8',newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write the data
        writer.writerow(data)
    
    make_noise()

def handler(signalnum, frame):
    raise TypeError

"""
Defining a cookie policy to reject all cookies:
"""
class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


""" 
This function updates the csv file to include the new URLs which was extracted from the webpage 
as well as update the geolocation information of the webpage within the file. 
The total num of url's in the file is updated as well.
Access lock is done to ensure that only one thread can read or write to the file at any time. 
"""
def write_to_file(local_url_index,num_of_url,new_urls,df_row,access_lock):
    access_lock.acquire()
    df = pandas.read_csv(csv_filename)
    df.iloc[local_url_index] = df_row
    df = pandas.concat([df,new_urls],ignore_index = True)
    num_of_url.value += len(new_urls)
    df.to_csv(csv_filename,index=False)
    access_lock.release()

"""
This function processes the body of the url and extracts the keywords. It also extracts the links found and append into 
database and make sures that there are no repeated urls.
"""
def find_jobs(main_url,full_url, color,access_lock,dict_of_jobs,dict_visited_links):
    try:
        new_urls = pandas.DataFrame(columns=('URL', 'Respond Time (S)', 'IP Of Server', 'Geolocation'))
        s = requests.Session()
        s.cookies.set_policy(BlockAll())

        html_text = s.get(full_url).text
        soup = BeautifulSoup(html_text,'lxml')
        body = soup.body

        # Process all words in the body
        for keyword in (body.strings):
            keyword_lowercase = keyword.lower().strip()
            if keyword_lowercase != "\n" and keyword_lowercase != "":
                keys = keyword_lowercase.split()
                time.sleep(0.001)
                # print(color+f'{keys}')
                # print(type(keys))

                for key in keys:
                    normal_string="".join(ch for ch in key if ch.isalnum())
                    # print(normal_string)
                    if normal_string == 'chemical':
                        #  print(Fore.YELLOW+"HIT", normal_string)
                        access_lock.acquire()
                        dict_of_jobs['chemical'] +=1 
                        access_lock.release()
                        
                    elif normal_string == 'project':
                        access_lock.acquire()
                        # print(Fore.WHITE+"HIT", normal_string)
                        dict_of_jobs['project'] +=1 
                        access_lock.release()

                    elif normal_string == 'service':
                        access_lock.acquire()
                        # print(Fore.GREEN+"HIT", normal_string)
                        dict_of_jobs['service'] +=1 
                        access_lock.release()

                    elif normal_string == 'electrical':
                        access_lock.acquire()
                        # print(Fore.CYAN+"HIT", normal_string)
                        dict_of_jobs['electrical'] += 1
                        access_lock.release()
                    
                    elif normal_string == 'mechanical':
                        access_lock.acquire()
                        # print(Fore.CYAN+"HIT", normal_string)
                        dict_of_jobs['mechanical'] += 1
                        access_lock.release()
                    
                    elif normal_string == 'software':
                        access_lock.acquire()
                        # print(Fore.CYAN+"HIT", normal_string)
                        dict_of_jobs['software'] += 1
                        access_lock.release()
                        
        time.sleep(0.1)
        # Grabs URL and do processing
        links = soup.find_all("a") 
        for link in links:
            append_url = str(link.get("href"))
            if append_url != 'None':
                append_url.replace('"', '')
                if append_url[0] == "/":
                    append_url = main_url + append_url
                    if append_url[-1] == '/':
                        append_url = append_url[:-1]
                    # Ensures new urls will not be store in database again
                    if append_url not in dict_visited_links:
                        print("Start getting IP using:" + str(append_url))
                        ip = get_server_ip(append_url)
                        print("Got IP:" + str(ip))
                        dict_visited_links[append_url]=1
                        print("Getting Geo Loca using IP:" + str(ip))
                        geoloc = get_geolocation(ip)
                        print("Got Geo Loca :" + str(geoloc))
                        list_row = [append_url, '-', ip, geoloc]
                        new_urls.loc[len(new_urls)] = list_row
    except Exception as e:
        print(e, " @ find jobs")

    return new_urls

""" 
Extract the URL from the selected row in the csv file and calls find_jobs to get the URL content as well as URL geolocation.
Returns a list of new url as well as the updated version of the selected row in the csv file.
"""
def getURLContent(df_row,color,access_lock,dict_of_jobs,dict_visited_links):
    try:
        url = df_row['URL']
        respond_time = get_response_time(url)
        df_row['Respond Time (S)'] = respond_time
        full_query = url 
        server_ip = get_server_ip(full_query)
        df_row['IP Of Server'] = server_ip
        country = get_geolocation(server_ip)
        df_row['Geolocation'] = country
        new_urls = find_jobs(url,full_query, color,access_lock,dict_of_jobs,dict_visited_links)
    except Exception as e:
        print(e, " @ getURL")
    return new_urls,df_row
 

""" 
Reads the newly added URLs from the CSV file and adds them to a queue of URL's for processing.
Updates the url_index variable which points to the row of the URL that was last added to the queue. Index 0 = Row 1 in CSV file.
Access lock is done to ensure that only one thread can read or write to the file at any time.
"""
def read_from_file(url_index,num_of_url,access_lock,color,dict_of_jobs):
    # acquire the lock
    global list_of_urls
    try:
        access_lock.acquire()
        local_num_of_url = num_of_url.value
        # print("local_num_of_url:",local_num_of_url)
        # print("url_index.value:",url_index.value)
        df = pandas.read_csv(csv_filename)
        access_lock.release()
        #Get updated content of file
        for i in range(url_index.value,local_num_of_url):
            list_of_urls.append((df.iloc[i],i))
            url_index.value += 1
    except Exception as e:
        print(e, "@ file ")

"""
Calls the getURLContent method to get the list of new urls extracted from the webpage as well as the webpage's geolocation.
Calls write_to_file to write update the URLs within the CSV file.
"""
def process_url(df_row,num_of_url,color,access_lock,dict_of_jobs,index,dict_visited_links):
    new_urls,df_row = getURLContent(df_row,color,access_lock,dict_of_jobs,dict_visited_links)
    print(color+"THREAD COMPLETE")
    write_to_file(index,num_of_url,new_urls,df_row,access_lock)

"""
Gets the response time of the server using url passed
"""
def get_response_time(url):
    response_time = requests.get(url).elapsed.total_seconds()
    return response_time

"""
Uses IP address to get location details using the IP to City database
"""
def get_geolocation(ip):
    location = DbIpCity.get(ip)
    country = location.country
    return country

"""
Uses the url to get IP of the server
"""
def get_server_ip(full_query):
    host_array = full_query.split('/')
    server_ip = socket.gethostbyname(host_array[2])
    return server_ip


if __name__ == '__main__':
    main()