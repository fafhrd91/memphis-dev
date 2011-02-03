"""

$Id: utils.py 11778 2011-01-30 07:42:47Z fafhrd91 $
"""
import random

# - remove '1', 'l', and 'I' to avoid confusion
# - remove '0', 'O', and 'Q' to avoid confusion
# - remove vowels to avoid spelling words
invalid_password_chars = ['a','e','i','o','u','y','l','q']

def getValidPasswordChars():
    password_chars = []
    for i in range(0, 26):
        if chr(ord('a')+i) not in invalid_password_chars:
            password_chars.append(chr(ord('a')+i))
            password_chars.append(chr(ord('A')+i))
    for i in range(2, 10):
        password_chars.append(chr(ord('0')+i))
    return password_chars

password_chars = getValidPasswordChars()

allchars = '23456qwertasdfgzxcvbQWERTASDFGZXCVB789yuiophjknmYUIPHJKLNM'
lowerchars = '23456qwertasdfgzxcvb789yuiophjknm'
upperchars = '23456QWERTASDFGZXCVB789YUIPHJKLNM'

def genPassword(length=10, chars=allchars):
    password = ''
    nchars = len(chars)
    for i in range(0, length):
        password += chars[random.randint(0,nchars-1)]

    return password

def genPassword2(length=32):
    return genPassword(length, upperchars)
