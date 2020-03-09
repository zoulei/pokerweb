
import sys

ifile = open(sys.argv[1])
line = ifile.readline()
data = line.strip().split(" ")
print(len(data))
for i in range(len(data)):
    if i < 22:
        continue
    print(i - 22, ":", data[i], end="\t")
print ("")
