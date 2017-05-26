import DBOperater
import Constant

def mongodatanull():
    result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{"_id":"35357006093039820170308115456"})
    for data in result:
        print type(data["data"][4])

if __name__ == "__main__":
    mongodatanull()