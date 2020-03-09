# import DBOperater
# import Constant

def mongodatanull():
    result = DBOperater.Find(Constant.HANDSDB,Constant.HANDSCLT,{"_id":"35357006093039820170308115456"})
    for data in result:
        print type(data["data"][4])

class A:
    def __init__(self,c):
        self.m_c = c

    def getc(self):
        return self.m_c

    def getb(self):
        return 1

class B(A):
    def __init__(self):
        # A.__init__(self,4)

        print self.getb()


if __name__ == "__main__":
    B()