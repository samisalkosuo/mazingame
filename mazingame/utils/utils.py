#Generic utility functions.
#
# The MIT License (MIT)

# Copyright (c) 2015 Sami Salkosuo

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from datetime import datetime
import sys
import time
import sqlite3
import hashlib

#TODO: make this as class
#class Utils:

pythonV2 = sys.version_info[0] == 2

DEBUG=True
DEBUG_FILE="debug.log"
ERROR_FILE="error.log"

def debug(str):
    if DEBUG:
        msg="%s: %s" % (datetime.now(),str)
        if DEBUG_FILE is not None:
            file=open(DEBUG_FILE,"a")
            file.write("%s\n" % msg)
            file.close()
        #print msg

def prompt(str):
    if pythonV2:
        inputStr = raw_input(str)
    else:
        inputStr = input(str)
    inputStr=unicode(inputStr,"UTF-8")
    return inputStr

def boolValue(value):
    string=str(value)
    return string.lower() in ("yes","y","true", "on", "t", "1")

def error():
    import traceback
    str=traceback.format_exc()
    print(str)
    msg="%s: %s" % (datetime.now(),str)
    appendToFile(ERROR_FILE,msg)

def appendToFile(filename, lines=[]):
    for line in lines:
        appendToFile(filename,line)

def appendToFile(filename, str):
    file=open(filename,"a")
    file.write(str)
    file.write("\n")
    file.close()

def appendToLogFile(str):
    file=open("mazingame_log.txt","a")
    file.write(str)
    file.write("\n")
    file.close()


def readFileAsString(filename):
    file=open(filename,"r")
    lines=[]
    for line in file:
        lines.append(line)
    file.close()
    return "".join(lines)

def sha256(str):
    sha=hashlib.sha256(str)
    return sha.hexdigest()

def currentDate():
    cTime=currentTimestamp()
    return datetime.fromtimestamp(cTime).strftime('%Y-%m-%d')

def currentTimeMillis():
    return int(round(time.time() * 1000))

def currentTimestamp():
    return time.time()

def formatTimestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def currentTimeISO8601():
    """Return current time as ISO8601 timestamp YYYY-MM-DD HH:MM:SS.SSS"""
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

#SQLITE
def openDatabase(file,inMemory=False):
    """Open SQLite db and return tuple (connection,cursor)"""
    if inMemory==True:
        conn=sqlite3.connect(':memory:')
    else:
        conn=sqlite3.connect(file)
    conn.row_factory = sqlite3.Row
    cursor=conn.cursor()    
    return (conn,cursor)


def closeDatabase(connection):
    """Close SQLite db connection"""
    if connection is not None:
        connection.close()

