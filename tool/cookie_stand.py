import os

with open('cook.txt', 'r') as f:
    con = f.readlines()
    res = ""
    for e in con:
        e = e.replace("\n", "")
        x = e.split(':')
        res = res +  "\'" + x[0] + '\'' + ":\'" + "".join(x[1:]) + "\',\n"
    print(res)