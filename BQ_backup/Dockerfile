FROM python:3.9
RUN pip install google-cloud-pubsub google-cloud-bigquery
COPY *.json .
ADD BQ_backup.py .
CMD ["python","-u", "./BQ_backup.py"] 