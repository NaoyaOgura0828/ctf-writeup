FROM python:3.11

COPY ./src /external

WORKDIR /external

RUN python3 -m pip install -r requirements.txt
RUN groupadd -r external && useradd external -g external && mkdir /home/external && chown -R external:external /home/external

USER external

CMD ["python3", "/external/app.py"]