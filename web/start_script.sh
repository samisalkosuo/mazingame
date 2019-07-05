#!/bin/bash

# config stuff
export PATH=/mazingame_server/bin:$PATH
echo 'export PS1=">"' >> ~/.bashrc 
source ~/.bashrc 
#show help text
cat help.txt


cd /mazingame
#start shell
bash