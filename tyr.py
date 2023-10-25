import multiprocessing
import time
def sleepy_man():
    print('Starting to sleep')
    time.sleep(1)
    print('Done sleeping')

if __name__ == '__main__':
    tic = time.time()
    p1 =  multiprocessing.Process(target= sleepy_man)
    p2 =  multiprocessing.Process(target= sleepy_man)
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    toc = time.time()

    print('Done in {:.4f} seconds'.format(toc-tic))