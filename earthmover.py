from cv2 import *
import numpy as np
import math
from pyemd import emd

# Initialize a and b numpy arrays with coordinates and weights
def EMD(histogram1, histogram2, distancematrix = None):
    if distancematrix is not None:
        return EMD_(histogram1,histogram2,distancematrix)
    hislen = len(histogram1)
    a = np.zeros( (hislen,2))
    # a = np.zeros((5,2))

    for i in range(0,hislen):
        # a[i][1] = i+1
        a[i][1] = i + 1
        a[i][0] = histogram1[i]

    b = np.zeros((hislen,2))

    for i in range(0,hislen):
        # b[i][1] = i+1
        b[i][1] = i + 1
        b[i][0] = histogram2[i]

    # Convert from numpy array to CV_32FC1 Mat
    a64 = cv.fromarray(a)
    a32 = cv.CreateMat(a64.rows, a64.cols, cv.CV_32FC1)
    cv.Convert(a64, a32)

    b64 = cv.fromarray(b)
    b32 = cv.CreateMat(b64.rows, b64.cols, cv.CV_32FC1)
    cv.Convert(b64, b32)

    # Calculate Earth Mover's
    return cv.CalcEMD2(a32,b32,cv.CV_DIST_L2)

def EMD_(histogram1, histogram2, distancematrix):
    fh = np.array(histogram1,dtype=float)
    fhsum = sum(fh)
    fh = np.vectorize(lambda t:t / fhsum)(fh)
    sh = np.array(histogram2,dtype=float)
    shsum = sum(sh)
    sh = np.vectorize(lambda t:t / shsum)(sh)

    dm = np.array(distancematrix)
    return emd(fh,sh,dm)


def simplediff(histogram1, histogram2):
    totaldif = 0
    for key in histogram1:
        if histogram1[key] == 0 or histogram2[key] == 0:
            continue
        totaldif += abs(histogram1[key] - histogram2[key])
    return totaldif

# def compare(histogram1,histogram2):
#     for key in histogram1:
#         if abs(histogram1[key] - histogram2[key]) < 100:
#             continue
#         if histogram1[key] != histogram2[key]:
#             print key," : ",histogram1[key],histogram2[key]
#
def testpyemd():
    fh = np.array([2,2,2,2,2],dtype=float)
    sumvalue = fh.sum()
    fh = np.vectorize(lambda t:t / sumvalue)(fh)
    sh = np.array([2.0,2,2,1,3])
    sh = np.vectorize(lambda t:t / sumvalue)(sh)
    dm = np.array([
        [0.0,1,2,3,4],
        [1.0,0,1,2,3],
        [2.0,1,0,1,2],
        [3.0,2,1,0,1],
        [4.0,3,2,1,0],
    ])
    print emd(fh,sh,dm)

def testpyemd1():
    first_histogram = np.array([0.0, 2.0])
    second_histogram = np.array([0.0, 2.0])
    distance_matrix = np.array([[0.0, 1],
                            [1.0, 0]])
    print emd(first_histogram, second_histogram, distance_matrix)

if __name__ == "__main__":
    print EMD([2,2,2,1,3],[2,2,2,2,2],[
        [0.0,1,2,3,4],
        [1.0,0,1,2,3],
        [2.0,1,0,1,2],
        [3.0,2,1,0,1],
        [4.0,3,2,1,0],
    ])

    print EMD([2,2,2,2,2],[2,2,2,1,3],[
        [0.0,1,2,3,4],
        [1.0,0,1,2,3],
        [2.0,1,0,1,2],
        [3.0,2,1,0,1],
        [4.0,3,2,1,0],
    ])

    print EMD([1/3.0,1/3.0,1/3.0,0,0],[0,0,0,1/2.0,1/2.0],[
        [0.0,0,0,3,4],
        [0.0,0,0,2,3],
        [0.0,0,0,1,2],
        [0.0,0,0,0,1],
        [0.0,0,0,1,0],
    ])

    print EMD([5,5,5,0,0],[0,0,0,5,5],[
        [0.0,1,2,3,4],
        [1.0,0,1,2,3],
        [2.0,1,0,1,2],
        [3.0,2,1,0,1],
        [4.0,3,2,1,0],
    ])

    print EMD([0,0,0,1,1],[1/3.0,1/3.0,1/3.0,0,0],[
        [0.0,1,2,3,4],
        [1.0,0,1,2,3],
        [2.0,1,0,1,2],
        [3.0,2,1,0,1],
        [4.0,3,2,1,0],
    ])


    testpyemd()
    print EMD([0,1],[5,3])
    testpyemd1()