from cv2 import *
import numpy as np
import math

# Initialize a and b numpy arrays with coordinates and weights
def EMD():
    a = np.zeros((5,2))

    for i in range(0,5):
        # a[i][1] = i+1
        a[i][1] = i + 1

    a[0][0] = 1
    a[1][0] = 2
    a[2][0] = 3
    a[3][0] = 4
    a[4][0] = 5

    b = np.zeros((5,2))

    for i in range(0,5):
        # b[i][1] = i+1
        b[i][1] = i + 1

    b[0][0] = 5
    b[1][0] = 5
    b[2][0] = 5
    b[3][0] = 5
    b[4][0] = 5

    # Convert from numpy array to CV_32FC1 Mat
    a64 = cv.fromarray(a)
    a32 = cv.CreateMat(a64.rows, a64.cols, cv.CV_32FC1)
    cv.Convert(a64, a32)

    b64 = cv.fromarray(b)
    b32 = cv.CreateMat(b64.rows, b64.cols, cv.CV_32FC1)
    cv.Convert(b64, b32)

    # Calculate Earth Mover's
    print cv.CalcEMD2(a32,b32,cv.CV_DIST_L2)

    # Wait for key
    cv.WaitKey(0)

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
    EMD()