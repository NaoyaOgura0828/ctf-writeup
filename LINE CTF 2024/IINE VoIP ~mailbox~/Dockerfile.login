FROM python:3.11

WORKDIR /usr/src/app

COPY login_system/ /usr/src/app/login_system

RUN pip install --no-cache-dir -r /usr/src/app/login_system/requirements.txt

EXPOSE 10030

CMD ["uvicorn", "login_system.main:app", "--reload", "--host=0.0.0.0", "--port=10030"]