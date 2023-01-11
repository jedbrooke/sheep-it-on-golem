FROM openjdk:11
RUN wget -q https://www.sheepit-renderfarm.com/media/applet/client-latest.php -O sheepit.jar
RUN echo deb-src http://deb.debian.org/debian bullseye main >> /etc/apt/sources.list
RUN apt-get -y update
RUN apt-get -y upgrade
# sheepit deps
RUN apt-get install --no-install-recommends -y \
    curl \
    libsdl1.2debian \
    libxxf86vm1 \
    libxi6 \
    libxrender1 \
    libxfixes3

# # network deps
# RUN apt-get install --no-install-recommends -y \
#     net-tools \
#     iputils-ping \
#     cargo \
#     libssl-dev \
#     pkg-config \
#     python3 \
#     jq

# # ssh deps
# RUN apk add --no-cache --update bash openssh iproute2 tcpdump screen
# RUN echo "UseDNS no" >> /etc/ssh/sshd_config && \
#     echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
#     echo "PasswordAuthentication no" >> /etc/ssh/sshd_config

# RUN cargo install -f websocat
# ENV PATH "$PATH:/root/.cargo/bin"


VOLUME /golem/input /golem/output /golem/work
WORKDIR /golem/work
# RUN mv /sheepit-client-*.jar /sheepit-client.jar

# COPY proxy_server.py /proxy_server.py
# RUN ls /golem/input
