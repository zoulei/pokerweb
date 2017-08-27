from cv2 import *
import numpy as np
import math

# Initialize a and b numpy arrays with coordinates and weights
def EMD(histogram1, histogram2):
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

def simplediff(histogram1, histogram2):
    totaldif = 0
    for key in histogram1:
        if histogram1[key] == 0 or histogram2[key] == 0:
            continue
        totaldif += abs(histogram1[key] - histogram2[key])
    return totaldif

def compare(histogram1,histogram2):
    for key in histogram1:
        if abs(histogram1[key] - histogram2[key]) < 100:
            continue
        if histogram1[key] != histogram2[key]:
            print key," : ",histogram1[key],histogram2[key]

if __name__ == "__main__":
    EMD([2,2,2,1,3],[2,2,2,2,2])