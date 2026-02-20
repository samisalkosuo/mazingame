FROM python:3.11-slim

LABEL maintainer="Sami Salkosuo"
LABEL source_url="https://github.com/samisalkosuo/mazingame"

WORKDIR /mazingame

# Install system dependencies for curses
RUN apt-get update && apt-get install -y --no-install-recommends \
    libncurses5-dev \
    libncursesw5-dev \
    && rm -rf /var/lib/apt/lists/*

# Create data directory for highscores and game history
RUN mkdir /data


VOLUME [ "/data" ]

#copy mazingame files
COPY mazingame/ ./mazingame/
COPY mazingame-runner.py ./

#set TERM so that console works correctly
ENV TERM xterm 

COPY scripts/run_mazingame.sh ./

#set correct permissions
RUN chmod 755 *.sh

ENTRYPOINT ["/bin/bash", "-c", "./run_mazingame.sh \"$@\"", "--"]

#CMD ["/bin/bash"]  
