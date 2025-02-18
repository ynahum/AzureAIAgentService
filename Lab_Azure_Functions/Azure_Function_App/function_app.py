import azure.functions as func
import logging
import os 
import json
import azure.identity
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient, BinaryBase64EncodePolicy, BinaryBase64DecodePolicy

app = func.FunctionApp()

@app.queue_trigger(arg_name="msg", queue_name="inputqueue",
                               connection="STORAGE_CONNECTION") 
def deathNoteByBatman(msg: func.QueueMessage) -> None:
    logging.info('Python queue trigger function processed a queue item')

    # Queue to send message to
    queue_client = QueueClient(
        os.environ["STORAGE_CONNECTION__queueServiceUri"],
        queue_name="outputqueue",
        credential=DefaultAzureCredential(),
        message_encode_policy=BinaryBase64EncodePolicy(),
        message_decode_policy=BinaryBase64DecodePolicy()
    )

    messagepayload = json.loads(msg.get_body().decode('utf-8'))
    name=messagepayload["name"]

    death_note = str(name) + """ ...

        You’ve made your choices. Walked your path. And now, the shadows have come to collect.

        Justice isn’t always served in the light. Sometimes, it’s delivered in the dark—where no one sees, no one hears. But make no mistake... it comes for everyone.

        Tonight, it comes for you.

        You won’t know when. You won’t know how. But when the darkness takes you, you’ll understand...

        I’m not your savior. I’m not your executioner.

        I’m just the reckoning you never saw coming.

        Goodbye, """ +str(name)

    result_message = {
        'Value': death_note
    }

    queue_client.send_message(json.dumps(result_message).encode('utf-8'))

    logging.info(f"Sent message to queue with message {result_message}")
