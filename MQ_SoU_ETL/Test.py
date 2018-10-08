import csv

with open('MQ_Hdbk_gdb.csv','w') as f:
    fieldnames = ['from','rel','to']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    
    writer.writeheader()
    