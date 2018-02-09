
FROM python:3.6.4

#install mazepy requirement
RUN git clone https://github.com/samisalkosuo/mazepy.git \
    && cd mazepy \
    && python setup.py install 

WORKDIR /mazingame

#copy mazingame files
COPY mazingame/ ./mazingame/
COPY mazingame-runner.py ./

#set TERM so that console works correctly
ENV TERM xterm 

#full screen: make sure that terminal window is large, otherwise error occurs
#CMD ["python","mazingame-runner.py","-f"]

#no full screen
CMD ["python","mazingame-runner.py"]

CMD ["/bin/bash"]  
