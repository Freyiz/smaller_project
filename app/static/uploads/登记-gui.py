import easygui as g

def fun():
    list = g.multenterbox('\n\n信息登记系统\n\n带*号为必填项\n','账号中心',['*用户名','*真实姓名','固定电话','*手机号码','QQ','*E-mail'],['小甲鱼',' ','',' ','',' '])
    for i in [1,3,5]:
        if list[i].isspace():
            g.msgbox('带*号项不能为空！请重新填写。','出错了出错了','好')
            fun()

fun()
