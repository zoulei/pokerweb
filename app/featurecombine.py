
import sys

ifilename = sys.argv[1]
ofilename = sys.argv[2]

ifile = open(ifilename)
ofile = open(ofilename, "w")
for line in ifile:
    data = line.strip().split(" ")
    odata = data[:22]
    for i in range(100):
        odata.append(0)
        for j in range(10):
            # print (data)
            # print (22 + i * 10 + j, len(data))
            odata[-1] += float(data[22 + i * 10 + j])
    odata.append(data[-2])
    odata.append(data[-1])
    ofile.write(" ".join([str(v) for v in odata]) + "\n")

ifile.close()
ofile.close()
