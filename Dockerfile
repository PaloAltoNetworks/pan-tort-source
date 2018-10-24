FROM python:3.6-alpine

LABEL description="PanTort"
LABEL version="0.3"
LABEL maintainer="sp-solutions@paloaltonetworks.com"

WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY pan-tort-api.py /app/pan-tort
COPY project /app/pan-tort
COPY log /app/pan-tort/

EXPOSE 5010

CMD ["python","/app/pan-tort/pan-tort-api.py"]

