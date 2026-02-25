import glob
import os                               # for setting and reading environment variables
from google.cloud import pubsub_v1, bigquery     # pip install google-cloud-pubsub  ##to install
import json;                            # to deal with json objects
 
# search for JSON key token
files=glob.glob("*.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=files[0]

# get environment variables
project_id = os.environ["GCP_PROJECT"]
subscription_id = os.environ["TOPIC_SUB_ID"]
topic_name = os.environ["TOPIC_NAME"]
bq_dataset = os.environ["BQ_DATASET"]
bq_table = os.environ["BQ_TABLE"]

# get topic path. Close publisher. We don't use it
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)
publisher.stop()

# create subscriber and get subscription path
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
sub_filter = "attributes.function=\"converted-data\""  # the condition used for filtering the messages to be recieved

# create a BigQuery client
bq = bigquery.Client()
table = bq.dataset(bq_dataset).table(bq_table)

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    # get the message content
    msg_data = json.loads(message.data.decode("utf-8"))

    # attempt send to BigQuery
    try:
        errors = bq.insert_rows_json(table, [msg_data])
        if errors:
            print(f"Encountered errors while inserting rows: {errors}")           
    except Exception as e:
        print(f"An error occurred while inserting rows: {e}")
    
    message.ack()

print(f"Listening for messages on {subscription_path}..\n")

with subscriber:
    # Create a subscription with the given ID and filter
    try:
        subscription = subscriber.create_subscription(
            request={"name": subscription_path, "topic": topic_path, "filter": sub_filter}
        )
    except:
        pass
    
    # The call back function will be called for each message match the filter from the topic.
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()