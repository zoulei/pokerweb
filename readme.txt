各个文件的主要作用：
1. tongjihandsinfo.py
此文件中的函数用于统计各种引申信息,比如各玩家的盈亏
tongjiinfo 函数检查该牌局信息是否正确记录

2. completehands.py
此文件中的函数用于识别玩家的名字并清理图片

3. collecthands.py
此文件中的函数用于收集数据相关的函数，就是各种URL的后台处理函数

4. printtongjiinfo.py
此文件用于输出数据库中的数据到屏幕

5. prefloprange.py
此文件用于计算preflop的range

6. privatecardsstrength.py
此文件用于计算手牌的强弱关系

/*
4. tongjicumuinfo.py
此文件中的函数用于统计累积信息，如玩家玩了多少局，总计输赢多少等
其最大的特色是这些信息能够实时更新，就是每次来了新数据之后能够使用以前的计算结果，而不需要重新处理以前的数据
*/



牌局信息记录的特点：
牌局进行的信息记录在"data"域中，这个数据是一个list,第一个元素记录了位置小大盲后手等信息。
接下来依次是从翻牌前直接到牌局结束的行动数据，每一轮为一个元素。
秀牌信息永远在第6个元素，也就是下标为5的位置。
牌面信息一般是在行动数据之后，但是也有特例。对于turn上就all in的牌局，牌面信息会在第7个元素，
我也不知道为什么，如果想知道可以去看收集牌局信息的代码。

"showcard" 域的意义，"showcard" 域是在tongjihandsinfo函数中加入的，是对牌局信息进行的基本检查，其值的意义如下：
负数意味着存在某些错误，正数意味着没有错误（这里没有检查后手信息是否有误）
-2  ：   action record error
-3  ：   empty payoff, payoff cannot be calculated, this means show card is not recorded
-1  ：   reason not known, check for specific reason
-4  ：   error found in the fifth step below
0   ：   hands is normal, but donot play to show card
1   ：   hands is normal and play to show card



数据从原始数据开始的数据处理过程：
第一步：
首先用removestraddle.py移除掉那些straddle的手牌
第二步：
首先用handinforrepairer.py修复那种后位提前fold牌的情况
第三步：
用staeinfocalculator.py来计算手牌的状态等信息，并移除掉错误的手牌
第四步：
用prefloprange.py来计算翻前入池率

# =======以下是旧版代码
第一步：
collecthands.uploadHandsInfo
从客户端接收数据并存储

第二步：
completehands.maincompletehands
识别玩家名字，并存储到数据库中新的collection中

第三步：
tongjihandsinfo.tongjimain
统计玩家的输赢以及每一轮的投入，以及玩家每一轮的行为数量，并统计每个玩家的总输赢，以及每个玩家的总手牌数，
并将结果存储到新的collection中
注：当系统完整运行时，该程序需要移除已经处理的数据，现在还没有进行这些处理;在 __main__ 函数中前两个函数移除
存储统计信息的document，系统完整运行之后不能移除这些信息

第四步：
handinforepairer.py
RepaireAllStack(Constant.HANDSDB, Constant.TJHANDSCLT).traverse()
修复stack记录错误。
RepaireLastAllin(Constant.HANDSDB, Constant.TJHANDSCLT).traverse()
修复最后一个动作为all in时，来不及记录all in 值就收POT的情况。
修复后的结果存储在原数据中。

第五步：
handcheck.py
CheckHand(Constant.HANDSDB, Constant.TJHANDSCLT).traverse()
再次检查牌局是否有错误，如果有错误，showcard置为-4
对于check after raise 类错误，有一部分可以将check替换为call，但是不知道当时为什么会记录为check，今后
如果有精力可以修复这一部分能用的数据。

第六步：
prefloprange.py
tongjiftmain()
tongjijoinrate()
repairjoinrate()
依次执行这三个方法来更新翻牌前入池率信息， 并存储到新的document中
注：现在这些函数都只能批量处理函数，完整系统运行时还需要简单修改成不断检查源数据并处理

第七步：
afterflopstate.py
calpreflopgeneralstatemain()
更新翻牌前统计信息，统计信息直接存储到源数据中
StateCalculater(Constant.HANDSDB,Constant.HANDSCLT).traverse()
更新翻牌后所有行动的状态，该信息直接存储到源数据中
注：现在这些函数都是批处理，完整系统运行时还需要及时移除数据并通过设置时间间隔等方式来防止对同一个数据的重复计算

