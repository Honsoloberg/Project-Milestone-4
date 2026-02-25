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
sub_filter = "attributes.function=\"filtered-data\""  # the condition used for filtering the messages to be recieved 

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    # Make sure that the global variables are accessed from within the function.
    global publisher, topic_path
    
    # get the message content
    msg_data = json.loads(message.data.decode("utf-8"))
   
    # checks for entries of temperature and pressure.
    temp = msg_data.get("temperature")
    pressure = msg_data.get("pressure")

    # If the entries exist, then convert them.
    if temp is not None:
        # convert temp from C to F
        msg_data["temperature"] = temp * (9/5) + 32

    if pressure is not None:
        # convert pressure from kPa to psi
        msg_data["pressure"] = pressure/6.895

    bin_msg = json.dumps(msg_data).encode("utf-8")

    publisher.publish(topic_path, bin_msg, function="converted-data")
    
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