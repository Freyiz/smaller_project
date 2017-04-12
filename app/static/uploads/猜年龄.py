import random
a = random.randint(31,33)
temp = input('猜猜我的年龄，猜中了有奖哦！\n')
guess = int(temp)
while guess != a:
    guess = int(temp)
    if guess > a:
        temp = input('大了大了,往年轻了猜嘛！\n')           
    elif guess == a:
        print('可算猜对了!')
        print('给你一个飞吻~')
    else:
        temp = input('有点小了，再给你一次机会！\n')
        
