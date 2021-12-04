import time
 
#demo1
def process_bar(percent, start_str='', end_str='', total_length=0):
    bar = ''.join(["\033[31m%s\033[0m"%'   '] * int(percent * total_length)) + ''
    bar = '\r' + start_str + bar.ljust(total_length) + ' {:0>4.1f}%|'.format(percent*100) + end_str
    print(bar, end='', flush=True)
 
 
for i in range(101):
    time.sleep(0.01)
    end_str = '100%'
    process_bar(i/100, start_str='', end_str=end_str, total_length=15)
 

#demo2
import sys, time
 
print("正在下载......")
for i in range(11):
    if i != 10:
        sys.stdout.write("==")
    else:
        sys.stdout.write("== " + str(i*10)+"%/100%")
    sys.stdout.flush()
    time.sleep(0.2)
print("\n" + "下载完成")


# demo3
import time
from progressbar import *
 
progress = ProgressBar()
for i in progress(range(100)):
    time.sleep(0.01)

#demo4
from time import sleep
from tqdm import tqdm
 
for i in tqdm(range(20)):
    sleep(0.1)