FROM python:3.11

COPY ./src /internal

WORKDIR /internal

RUN python3 -m pip install -r requirements.txt
RUN groupadd -r internal && useradd internal -g internal && mkdir /home/internal && chown -R internal:internal /home/internal

USER internal

CMD ["python3", "/internal/app.py"]