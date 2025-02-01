FROM python:3.8
LABEL maintainer="xxx@gmail.com"
ENV TZ="America/Los_Angeles"


COPY ./app /app/app/
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 8080

# Command to run your Flask app
ENTRYPOINT ["python"]
CMD ["app/app.py"]
