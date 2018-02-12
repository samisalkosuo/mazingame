
FROM python:3.6.4

WORKDIR /mazingame

#install mazepy requirement and makes gamedata-directory that holds game scores
RUN pip install mazepy && mkdir gamedata

#copy mazingame files
COPY mazingame/ ./mazingame/
COPY mazingame-runner.py ./

#set TERM so that console works correctly
ENV TERM xterm 

VOLUME [ "/mazingame/gamedata" ]

COPY scripts/run_mazingame.sh ./

#set correct permissions
RUN chmod 755 *.sh

ENTRYPOINT ["/bin/bash", "-c", "./run_mazingame.sh \"$@\"", "--"]

#CMD ["/bin/bash"]  
