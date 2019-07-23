FROM python:3.7.4-slim-buster

# because openjdk installer fails if there's no man dir
RUN mkdir -p /usr/share/man/man1

# install openjdk and unzip
RUN apt-get update && apt-get install -y \
    openjdk-11-jre-headless \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/share/man

# Install plyj
RUN pip install plyj

WORKDIR /extractor

RUN mkdir -p tools

# Download dex-tools to dex
ADD https://github.com/pxb1988/dex2jar/files/1867564/dex-tools-2.1-SNAPSHOT.zip dex-tools.zip
# --strip-components=1 analogue
RUN unzip -d dex-tmp dex-tools.zip
RUN mv dex-tmp/* tools/dex
RUN rm -rf dex-tools.zip dex-tmp

# Download jd-cli to jd
ADD https://github.com/kwart/jd-cmd/releases/download/jd-cmd-0.9.2.Final/jd-cli-0.9.2-dist.zip jd-cli.zip
RUN unzip -d tools/jd jd-cli.zip
RUN rm -rf jd-cli.zip

COPY extract-tandroid.py .
RUN chmod +x extract-tandroid.py

ENTRYPOINT [ "./extract-tandroid.py" ]
