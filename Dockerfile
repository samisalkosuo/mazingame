
FROM python:3.6.4

WORKDIR /mazingame

#install mazepy requirement and makes gamedata-directory that holds game scores
RUN pip install mazepy && mkdir gamedata
#git clone https://github.com/samisalkosuo/mazepy.git \
#    && cd mazepy \
#    && python setup.py install 


#copy mazingame files
COPY mazingame/ ./mazingame/
COPY mazingame-runner.py ./

#set TERM so that console works correctly
ENV TERM xterm 

VOLUME [ "/mazingame/gamedata" ]

COPY scripts/run_mazingame.sh ./

#set correct permissions
RUN chmod 755 *.sh


#note: to use full screen -f - make sure that terminal window is large, otherwise error occurs
ENTRYPOINT ["/bin/bash", "-c", "./run_mazingame.sh \"$@\"", "--"]

#CMD ["/bin/bash"]  
