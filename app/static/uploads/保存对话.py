import pickle

def fun():
        fb = open('boy_%d.txt' % count,'wb')
        pickle.dump(listb,fb)
        fb.close()
        fg = open('girl_%d.txt' % count,'wb')
        pickle.dump(listg,fg)
        fg.close()

f = open('record.txt')
count = 1
listb = []
listg = []
for each_line in f:
        if each_line[:5] != '=====':
                (role,talk) = each_line.split(':',1)
                if role == '小甲鱼':
                        listb.append(talk)
                else:
                        listg.append(talk)
        else:
                fun()
                listb = []
                listg = []
                count += 1
fun()
f.close()
