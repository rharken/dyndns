FROM quay.io/centos/centos:stream9

COPY requirements.txt dyndns.py /usr/local/bin/
RUN dnf update -y && \
    dnf upgrade -y && \
    dnf install python3.12 python3.12-pip xorg-x11-server-Xvfb firefox -y && \
    python3.12 -m pip install --upgrade pip && \
    python3.12 -m pip install -r /usr/local/bin/requirements.txt
ENTRYPOINT ["/usr/bin/python3.12", "/usr/local/bin/dyndns.py"]
