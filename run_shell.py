#-*- coding : utf-8-*-
'''
调用cmd执行
'''
import subprocess, datetime, os, inspect, ctypes, signal, sys
import psutil
from threading import Timer

# 在线程中抛出异常，使线程退出
def async_raise(tid, exctype):
    """Raises an exception in the threads with id tid"""
    try:
        if not inspect.isclass(exctype):
            raise TypeError("Only types can be raised (not instances)")
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
    except Exception as e:
        print(e)
        pass

def kill_command(p):
    """终止命令的函数"""
    print('kill command')

    # kill所有子进程
    proc_pid = p.pid
    parent_proc = psutil.Process(proc_pid)
    for child_proc in parent_proc.children(recursive=True):
        child_proc.kill()
    parent_proc.kill()

def execute(command, timeout, cwd=''):
    '''执行命令，一次返回一行数据'''
    if (cwd == ''):
        app = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, \
                               stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        app = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, \
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd = cwd)

    # 设置定时器去终止这个命令
    if timeout != 0:
        timer = Timer(timeout, kill_command, args=(app,))
        timer.start()

    for i in iter(app.stdout.readline,'b'):   
        if not i:
            break
        yield(i.decode('gbk', 'replace'))
        # yield (i.decode('utf-8', 'replace'))

    if timeout != 0:
        # 判断超时定时器是否执行
        if timer.is_alive() == False:
            yield (f"执行时间:{timeout}s 已超时")
            yield(408)
        else:
            timer.cancel()

    # 返回最终执行结果
    stdout, stderr = app.communicate()
    yield(app.returncode)

    return 0

def execute_retapp(command, timeout):
    '''
    执行命令，一次返回一行数据
    第一次返回subprocess的对象, 用于外部kill 命令
    '''
    app = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, \
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    yield(app)

    # 设置定时器去终止这个命令
    if timeout != 0:
        timer = Timer(timeout, kill_command, app)
        timer.start()

    for i in iter(app.stdout.readline,'b'):   
        if not i:
            break
        yield(i.decode('gbk'))
    
    if timeout != 0:
        timer.cancel()

    # 返回最终执行结果
    stdout, stderr = app.communicate()   
    yield(app.returncode)

    return 0


def execute_char(command, timeout, cwd=''):
    '''
     执行命令，每次输出一个字符, 按照gbk编码
    '''
    if (cwd == ''):
        app = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, \
                               stdout = subprocess.PIPE, stderr=subprocess.STDOUT, encoding = "gbk")
    else:
        app = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, \
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd = cwd, encoding = "gbk")

    # 设置定时器去终止这个命令
    if timeout != 0:
        timer = Timer(timeout, kill_command, args=(app,))
        timer.start()

    for i in iter(lambda: app.stdout.read(1), ''):   
        if not i:
            break
        yield(i)

    if timeout != 0:
        # 判断超时定时器是否执行
        if timer.is_alive() == False:
            yield (f"执行时间:{timeout}s 已超时")
            yield(408)
        else:
            timer.cancel()

    # 返回最终执行结果
    stdout, stderr = app.communicate()
    yield(app.returncode)

    return 0

if __name__ == '__main__':
    # command = 'ping www.baidu.com'
    command = 'python progress_bar.py'

    f = execute_char(command, 0)

    while True:
        read = next(f)
        if type(read) == type(''):
            print(read, end="")
            # sys.stdout.write(read)
            sys.stdout.flush()
        else:
            # 执行结果
            print(f'执行结果:{read}')
            break
    
    # 一次输出一行
    f = execute(command, 0)

    while True:
        read = next(f)
        if type(read) == type(''):
            # print(read, end="")
            sys.stdout.write(read)
            sys.stdout.flush()
        else:
            # 执行结果
            print(f'执行结果:{read}')
            break