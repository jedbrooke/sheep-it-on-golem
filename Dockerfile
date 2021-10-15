FROM openjdk:11
RUN wget -q https://www.sheepit-renderfarm.com/getstarted.php 
RUN wget -q https://sheepit-renderfarm.com/$(grep -m 1 -o -e 'media\/applet\/sheepit-client-.*jar' getstarted.php)
RUN echo deb-src http://deb.debian.org/debian bullseye main >> /etc/apt/sources.list
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install --no-install-recommends -y \
    curl \
    libsdl1.2debian \
    libxxf86vm1 \
    libxi6 \
    libxrender1 \
    libxfixes3

VOLUME /golem/input /golem/output /golem/work
WORKDIR /golem/work
RUN mv /sheepit-client-*.jar /sheepit-client.jar
RUN which java