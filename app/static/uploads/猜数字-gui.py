import random
import easygui as g

def num1():
    num_real = random.randint(1,10)
    try:
        num = g.enterbox('不妨猜一下小甲鱼现在心里想的是那个数字（1~10）','数字小游戏')
        if int(num) == num_real:
            if g.ccbox('猜对啦！还要再玩一次吗？','',('好啊','不玩了')):
                return num1()
        else:
            if g.ccbox('差一点就被你猜中了！还要再玩一次吗？','',('好啊','不玩了')):
                return num1()
    except (TypeError,ValueError):
        return 1
    
num1()
