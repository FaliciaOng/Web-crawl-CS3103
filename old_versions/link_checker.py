
from bs4 import BeautifulSoup
import requests
from multiprocessing import Process
import time
from colorama import Fore
from http import cookiejar

class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


def find_jobs(main_url,full_url, post_name, color):
    s = requests.Session()
    s.cookies.set_policy(BlockAll())

    html_text = s.get(full_url).text
    soup = BeautifulSoup(html_text,'lxml')
    
    # grab body
    body = soup.body
    print(body)

    for keyword in (body.strings):
        keyword_lowercase = keyword.lower().strip()
        if keyword_lowercase != "\n" and keyword_lowercase != "":
            # must use .contains()
            keys = keyword_lowercase.split()
            print(keys)

    time.sleep(0.1)

    # grab url 
    links = soup.find_all("a") 
    total_url = 0
    for link in links:
        total_url+= 1
        append_url = str(link.get("href"))
        if append_url[0] == "/":
            append_url = main_url + append_url
        print("Link:", (append_url))

    print("total url:",total_url)

# future work
def pool_manager():
    pass  


if __name__ == '__main__':
    
    url = 'https://www.jobstreet.com.sg'
    query = '/Engineer-jobs'
    # full_query = 'https://sg.jobsdb.com/j?sp=homepage&trigger_source=homepage&q=engineering&l='
    # full_query = 'https://jobscentral.com.sg/jobs?title=engineer'
    full_query = url+query

    # print(full_query)
    
    process1 = Process(target=find_jobs, args=(url,full_query, 'posts', Fore.RED))

    process1.start()
    process1.join()

    print("process ended")