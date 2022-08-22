FROM python
WORKDIR /
RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
RUN apt-get install -y python3 python3-dev git python3-pip python-is-python3 libgl1-mesa-dev build-essential ffmpeg
COPY requirements.txt .
RUN pip install -r requirements.txt