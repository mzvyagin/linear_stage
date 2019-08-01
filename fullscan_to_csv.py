# small script to get a csv output of lds single scan

import lds
import csv

l=lds.lds()

s=lds.create_session('COM4')

l.start(s)

r=l.full_scan(s)

def convert(results,file_name):
        if file_name==None:
            file_name='test_results.csv'
        else:
            file_name=file_name+'.csv'
        with open(file_name,mode='w',newline='') as test_results:
            results_writer=csv.writer(test_results,delimiter=',',quotechar='"')
            for i in results:
                results_writer.writerow(i)
            test_results.close()
            

convert(r,"test_lds_scan")

l.stop(s)

