from multiprocessing import Manager
# import os
#
# def info(title):
#     return
#     print(title)
#     print('module name:', __name__)
#     print('parent process:', os.getppid())
#     print('process id:', os.getpid())
#
# def f(name):
#     #info('function f')
#     s = sum(list(range(name)))
#     print(len(range(name)))
# if __name__ == '__main__':
#     length = 1000000
#     for i in range(length):
#         p = Process(target=f, args=(int(length-i),))
#         p.start()
#         p.join()

import multiprocessing as mp
import psutil


def spawn(gen, f):
    seq = gen()
    try:
        while True:
            n = next(seq)

            procs = list()
            n_cpus = psutil.cpu_count()

            for cpu in range(n_cpus):
                affinity = [cpu]
                d = dict(affinity=affinity, f=f, it=n)
                p = mp.Process(target=run_child, kwargs=d)
                p.start()
                procs.append(p)
            for p in procs:
                p.join()
                print(p.name, 'joined')
    except StopIteration:
        pass

def run_child(affinity, f, it):
    proc = psutil.Process()
    proc.cpu_affinity(affinity)
    _aff = proc.cpu_affinity()
    return f(it)


if __name__ == '__main__':
    spawn()