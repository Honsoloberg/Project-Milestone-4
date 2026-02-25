import glob
import os                               # for setting and reading environment variables
from google.cloud import pubsub_v1      # pip install google-cloud-pubsub  ##to install
import json;                            # to deal with json objects
 
# search for JSON key token
files=glob.glob("*.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=files[0]

# get environment variables
project_id = os.environ["GCP_PROJECT"]
subscription_id = os.environ["TOPIC_SUB_ID"]
topic_name = os.environ["TOPIC_NAME"]

# create a publisher and get topic path
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

# create subscriber and get subscription path
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
sub_filter = "attributes.function=\"raw submit\""  # topic message filter

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    # Make sure that the global variables are accessed from within the function.
    
    global publisher, topic_path
    # get the message content
    msg_data = json.loads(message.data.decode("utf-8"))
   
    # ensures all data points are present. If data isn't provided an entry is created as null.
    # This must be done for easy backup to BigQuery
    time = None if msg_data["time"] == "" else float(msg_data["time"])
    profileName = None if msg_data["profileName"] == "" else str(msg_data["profileName"])
    temperature = None if msg_data["temperature"] == "" else float(msg_data["temperature"])
    humidity = None if msg_data["humidity"] == "" else float(msg_data["humidity"])
    pressure = None if msg_data["pressure"] == "" else float(msg_data["pressure"])

    send = {"time" : time, "profileName" : profileName, "temperature" : temperature, "humidity" : humidity, "pressure" : pressure}

    bin_msg = json.dumps(send).encode("utf-8")

    publisher.publish(topic_path, bin_msg, function="filtered data")
    
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