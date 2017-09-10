import tongjihandsinfo
import handinforepairer
import handcheck
import prefloprange
import afterflopstate
import afterflopwinrate
import Constant

tongjihandsinfo.removecumuinfo()
tongjihandsinfo.removetjinfo()
tongjihandsinfo.tongjimain()

v = handinforepairer.RepaireAllStack(Constant.HANDSDB, Constant.TJHANDSCLT)
v.traverse()
print v.m_cnt

v = handinforepairer.RepaireLastAllin(Constant.HANDSDB, Constant.TJHANDSCLT)
v.traverse()
print v.m_cnt

handcheck.CheckReadcard(Constant.HANDSDB, Constant.TJHANDSCLT, handsid="").traverse()

prefloprange.removepreflopdoc()

prefloprange.tongjiftmain()
prefloprange.tongjijoinrate()
prefloprange.repairjoinrate()

afterflopstate.calpreflopgeneralstatemain()
afterflopstate.StateCalculater(Constant.HANDSDB,Constant.TJHANDSCLT).traverse()

afterflopwinrate.WinrateCalculater(Constant.HANDSDB,Constant.TJHANDSCLT,func=afterflopwinrate.mainfunc,handsid="",sync=False).traverse()
