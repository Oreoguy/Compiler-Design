# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 22:01:50 2022

@author: Vansh
"""

def crc(msg,div,code= '000'):
    msg= msg +code
    
    msg = list(msg)
    div = list(div)
    for i in range (len(msg)-len(code)):
        if msg[i] == '1' :
            for j in range (len(div)):
                msg[i+j] = str((int(msg[i+j])+ int(div[j]))%2)
                
        return ''.join(msg[-len(code):])

dis = input ("Enter a binary string as divisor:")
m = input ("Enter message to be sent :")
print ('Message :',m)
print ('Divisor:',dis)
code = crc(m,dis)
print('Remainder :',code)
chkoutput= m + code

receivercode = input("Enter the receiver code :")
if (chkoutput == receivercode):
    print ("Correct")
else:
    print ('false')