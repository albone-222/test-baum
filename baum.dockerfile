FROM python:3.11-rc-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update
RUN apt install -y python3.11 curl

COPY ./entrypoint.sh ./entrypoint.sh
RUN chmod u+x entrypoint.sh

RUN pip install --upgrade pip

RUN pip install poetry
COPY pyproject.toml /code/
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

EXPOSE 8888

COPY ./ .
ENTRYPOINT [ "/code/entrypoint.sh" ]
CMD ["python", "app.py"]

