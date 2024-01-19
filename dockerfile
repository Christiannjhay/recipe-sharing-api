FROM python:3.9

WORKDIR /app

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       unixodbc-dev \
       odbcinst \
       odbcinst1debian2 \
       msodbcsql17

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "app.py" ]
