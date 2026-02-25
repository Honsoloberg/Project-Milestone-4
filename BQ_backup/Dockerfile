FROM python:3.9
RUN pip install google-cloud-pubsub google-cloud-bigquery
COPY *.json .
ADD filter.py .
CMD ["python","-u", "./filter.py"] 