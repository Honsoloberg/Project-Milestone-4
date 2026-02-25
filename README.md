# Project Milestone 4: Microservices using Google Pub/Sub Communication
## SOFE4630U-MS4

### Objectives
1. Get familiar with microservices
2. Impelement microservice using Python
3. Containerize Python application
4. Configure Pub/Sub Subscription(s) to filter the receiving messages.

### Content
1. Labels.csv
    - Contains simulated Sensor Data

2. producer.py (run locally as a simple producer script)
    - Iterates over the "Labels.csv" and validates each value that it's a float, String or None.
    - Converts each row in CSV into JSON and serializes the message
    - Publishes the JSON objects to a google cloud topic.

3. filter.py (Run as a micro service on Google Cloud)
    - Reads messages from producer.py via a Google Topic (Pub/Sub)
    - Standardizes the data from the producer.py. i.e. adds null values for values that are not defined
    - Publishes the Standardized data back into the Google Topic

4. convert.py (Run as a micro service on Google Cloud)
    - Reads messages from the filter.py via a Google Topic (Pub/Sub)
    - Does unit conversion of specific data fields provided those data fields are defined
    - Publishes the data back to the Google Topic

5. BQ_backup.py
    - Reads messages from the convert.py via a Google Topic (Pub/Sub)
    - Pushes the messages from the topic to a table in a Google BigQuery dataset