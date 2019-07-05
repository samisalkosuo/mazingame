FROM nikolaik/python-nodejs:python3.7-nodejs8 as build-stage 

LABEL maintainer="Sami Salkosuo"
LABEL source_url="https://github.com/samisalkosuo/mazingame"

WORKDIR /mazingame

#install mazepy requirement and make data-directory that holds scores and game history
RUN pip install mazepy \
    && pip install pg8000 \
    && pip install pyinstaller \
    && mkdir /data

#copy mazingame files
COPY mazingame/ ./mazingame/
COPY mazingame-runner.py ./

RUN pyinstaller --onefile mazingame-runner.py

#CMD ["/bin/bash"]  

FROM nikolaik/python-nodejs:python3.7-nodejs8

#volume for highscores
VOLUME [ "/data" ]

WORKDIR /mazingame_server

#shamelessly uses demos at https://github.com/jupyter/terminado
COPY web/requirements.txt ./
RUN pip install -r requirements.txt
COPY web/ ./

#copy files
COPY web/bin ./
COPY web/help.txt ./

RUN chmod 755 bin/*

#start script executed when terminal is started
COPY web/start_script.sh ./
RUN chmod 755 start_script.sh

RUN mkdir /mazingame

COPY --from=build-stage /mazingame/dist/mazingame-runner /usr/local/bin/mazingame


CMD ["python","mazingame_server.py"]  
