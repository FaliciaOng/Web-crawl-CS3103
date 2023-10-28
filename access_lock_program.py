import multiprocessing
from multiprocessing import Process
import pandas
# importing the random module
import random
import os
import time
cwd = os.getcwd()
print(cwd)

def write_to_file(local_url_index,num_of_url,new_urls,df_row,access_lock):
    access_lock.acquire()
    df = pandas.read_csv('C:/Users/Siew Yang Zhi/Desktop/Uni Stuff/Y4 Sem 1/CS3103/Assignment/Assignment 4/url_links.csv') #Get updated content of file
    df.iloc[local_url_index] = df_row
    for i in range(len(new_urls)):
        df = df.append(new_urls.iloc[i],ignore_index=True) 
        num_of_url.value += 1
    df.to_csv('C:/Users/Siew Yang Zhi/Desktop/Uni Stuff/Y4 Sem 1/CS3103/Assignment/Assignment 4/url_links.csv',index=False)
    access_lock.release()

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

def getURLContent(df_row):
    new_urls = pandas.DataFrame(columns=('URL', 'Respond Time', 'IP Of Server'))
    num = random.randint(0,100)
    url = df_row['URL']
    df_row['Respond Time'] = num
    df_row['IP Of Server'] = num

    list_row = [url+" "+str(num), 0, 0]
    new_urls.loc[len(new_urls)] = list_row
    
    num = random.randint(0,100)

    list_row = [url+" "+str(num), 0, 0]
    new_urls.loc[len(new_urls)] = list_row
    return new_urls,df_row
    
if __name__ == '__main__':
    url_index = multiprocessing.Value("i",0)
    num_of_url = multiprocessing.Value("i",1)
    access_lock = multiprocessing.Lock()
    print("begin program")
    while (True):
        #There is uncrawled URL within the file.
        print("check")
        print("num of url:" + str(num_of_url.value))
        if (num_of_url.value > 10):
            break
        if (num_of_url.value != url_index.value):
            print("values not the same")
            p = Process(target=read_from_file, args=(url_index,num_of_url,access_lock))
            p.start()
        print("finish check")
        time.sleep(1)
