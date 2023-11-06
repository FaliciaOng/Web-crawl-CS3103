


import multiprocessing
import signal
from signal import signal, SIGINT
import sys
import time
from multiprocessing import Pool, current_process
from colorama import Fore
# SuperFastPython.com
# example of limiting the number of tasks per child in the process pool
from time import sleep
from multiprocessing.pool import Pool
from multiprocessing import current_process
 
# # task executed in a worker process
# def task(value):
#     # get the current process
#     process = current_process()
#     # report a message
#     print(f'Worker is {process.name} with {value}', flush=True)
#     while value > 0:
#         print(f"{value} seconds remaining from thread ")
#         value -= 1
#         time.sleep(1)

 
# # protect the entry point
# if __name__ == '__main__':
#     work = [5,6,7,8]
#     # create and configure the process pool
#     with Pool(2) as pool:
#         # issue tasks to the process pool
#         for i in range(4):
#             pool.map(task,work)
#         # close the process pool
#         pool.close()
#         # wait for all tasks to complete
#         pool.join()



def handler(signalnum, frame):
    raise TypeError

def square(x, y,color):
    # try:
    #allow ending the code
    signal(SIGINT, handler)
    process = current_process()
    # print(color+process.name, x)
    while y > 0:
        print(color+f"{y} seconds remaining from thread ",x)
        y -= 1
        time.sleep(1)

    return x
    # except KeyboardInterrupt as e:
    #     print("end")
    #     global pool
    #     pool.close()
    #     pool.terminate()
    #     pool.join()
    #     sys.exit() 
        

def close_pool():
    global pool
    pool.close()
    pool.terminate()
    pool.join()


def process_manager():
    pool = Pool()  
    data = [1, 2, 3, 4, 5]
    y = [2,3,2,2,2]


    numer_of_processes = 2
    color = [Fore.RED,Fore.BLUE,Fore.CYAN,Fore.GREEN,Fore.WHITE]
    # https://stackoverflow.com/questions/56911459/how-to-make-for-loop-that-will-create-processes-in-python

    # for i in range (3):
    numer_of_processes = 3
    try:
        # allow us to end the code
        signal(SIGINT, handler)
        v = 0
        with Pool(numer_of_processes) as pool:
            print("hi")
            for i in range (10):
                v = v%3
                pool.apply_async(square,(1,3,color[1]))
                v+= 1

            # pool.apply_async(square,(2,2,color[1]))
            # pool.apply_async(square,(3,1,color[2]))


        
            # pool.starmap(square, zip(data, (y),color))
            pool.close()
    # wait for all tasks to complete
            pool.join()


    except TypeError as e:
        print(e, "tye")


if __name__ == '__main__':
    process_manager()
    