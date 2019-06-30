import time
start = time.time()
a = 0
for i in range(100000000):
    a += i
print(a)
print(time.time() - start)