FROM tiangolo/uwsgi-nginx:python3.8
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python3", "-m" , "flask", "run", "-h", "0.0.0.0", "-p", "8080"]