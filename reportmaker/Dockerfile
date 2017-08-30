FROM ubuntu
RUN apt-get update
RUN apt-get -y install python3-pip build-essential libssl-dev libffi-dev libpango1.0-0 libcairo2 locales && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8
COPY ./ /
RUN pip3 install -r requirements.txt
CMD python3 reporter.py
