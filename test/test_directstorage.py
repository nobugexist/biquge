import os

path = os.path.join("d:/asdasd", "dasd.txt")
os.makedirs(os.path.split(path)[0])
with open(path, "a+")as f:
    f.write("dadasda")
