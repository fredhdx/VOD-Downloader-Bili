import re
import csv

f = open("md_list.md",'r')
fo = open('list.txt','w')

with open("qizhi_MC.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for row in reader:
        fo.write(row[2] + '\n')


