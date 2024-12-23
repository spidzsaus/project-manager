FROM python:3.12.1-alpine3.19

FROM python:latest 

WORKDIR /server

COPY . /server

RUN python3 -m pip install --no-cache-dir --upgrade -r /server/requirements.txt

ENV SERVER_PORT=8080

# Setting up the server
EXPOSE 8080

# Migrating the database
RUN python3 manage.py migrate


# Running the app
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]