FROM python:3.11-slim
 
RUN apt update

RUN mkdir -p /home/app
WORKDIR /home/app

RUN pip install pipenv==2023.9.8
ENV PIPENV_VENV_IN_PROJECT=1
COPY Pipfile Pipfile.lock ./
RUN pipenv sync
ENV PATH=/home/app/.venv/bin:${PATH}

COPY . ./

CMD gunicorn --workers=5 --threads=1 -b 0.0.0.0:80 app:server
