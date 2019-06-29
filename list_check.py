#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import webbrowser
from pyraf import iraf
import glob
import numpy as np
import sys	

def check():
    lstlst = ['objlst']
    if os.path.isfile('objlst'):
        webbrowser.open('objlst')
        webbrowser.open('../errfilelst')
        iraf.imexamine(input='@objlst', frame=1)
    print '<<<<<check the list>>>>>'

def save_lst(list_name,contents):
    f=open(list_name,'w')
    contents.sort()
    for content in contents:
        f.write(content+'\n')
    f.close()

def main():
    print '='*50
    print '<<<<<run list_check.py>>>>>'
    alllst=glob.glob('*.fits')

        #创建一个error list用来排除错误文件
    absdir = os.getcwd()
    os.chdir('..')
    if not os.path.isfile('errfilelst'):
        print 'make a errfilelst'
        errlst=[]
        save_lst('errfilelst',errlst)
    errfile=open('errfilelst','r')
    errlst=errfile.readlines()
    errfile.close()
    for i in errlst:
        alllst.remove(i.split()[0])
    os.chdir(absdir)
    save_lst('objlst',alllst)


    if  len(sys.argv)>1:
        if sys.argv[1]!='no':
            check()
    else:
        check()
        
    print '='*50



if __name__ == '__main__':
    main()
    
