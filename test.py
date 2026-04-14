from util.print import get_async_print
import time,numpy

X=50000
ITER=5

def bench_async() -> int:
    aprint=get_async_print()
    start=time.perf_counter_ns()
    for i in range(X):
        aprint('値:',i)
    aprint.close()
    return time.perf_counter_ns()-start

def bench_normal() -> int:
    start=time.perf_counter_ns()
    for i in range(X):
        print('値:',i,flush=True)
    return time.perf_counter_ns()-start

if __name__ == '__main__':
    print('Test start')
    time.sleep(1)
    async_times=[]
    normal_times=[]
    bench_normal()
    bench_async()
    for _ in range(ITER):
        async_times.append(bench_async())
        normal_times.append(bench_normal())
    a=numpy.array(async_times)
    b=numpy.array(normal_times)

    print('===Info===')
    print(f'X:{X}')
    print(f'ITER:{ITER}')
    print('===Average===')
    print(f'async : {int(a.mean())} ns')
    print(f'normal: {int(b.mean())} ns')
    print(f'diff  : {int(a.mean() - b.mean())} ns')
    print('===Detail===')
    print(f'async : {a}')
    print(f'normal: {b}')
    print(f'diff  : {a - b}')
