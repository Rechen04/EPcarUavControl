from time import time

t0 = time()

while True:
    if time()-t0 > 3:
        print(time()-t0)
        break