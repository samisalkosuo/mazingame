
FROM python:3.6.4

#install game files
RUN git clone https://github.com/samisalkosuo/mazepy.git \
    && cd mazepy \
    && python setup.py install \
    && cd .. \
    && git clone https://github.com/samisalkosuo/mazingame.git 
    #\
    #&& cd mazingame 
    #\
    #&& python setup.py install

ENV TERM xterm 

WORKDIR /mazingame

#full screen: make sure that terminal window is large, otherwise error occurs
#CMD ["python","mazingame-runner.py","-f"]

#no full screen
CMD ["python","mazingame-runner.py"]

#CMD ["/bin/bash"]  
