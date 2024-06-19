FROM python:3.11

COPY ./src /report

WORKDIR /report

RUN python3 -m pip install -r requirements.txt
RUN groupadd -r report && useradd report -g report && mkdir /home/report && chown -R report:report /home/report

USER report

CMD ["python3", "/report/app.py"]