#Project2_serializeImageData
import json
import boto3
import base64

s3 = boto3.resource('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    s3.Bucket(bucket).download_file(key, '/tmp/image.png')
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        "image_data": image_data,
        "s3_bucket": bucket,
        "s3_key": key,
        "inferences": []
    }

#Project2_Classification
import json
import sagemaker
import base64
from sagemaker.serializers import IdentitySerializer

# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2023-02-04-17-51-28-694'

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['image_data'])

    # Instantiate a Predictor
    predictor = sagemaker.predictor.Predictor(
        ENDPOINT,
        sagemaker_session=sagemaker.Session()
        )

    # For this model the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")

    # Make a prediction:
    inferences = predictor.predict(image)
    
    # We return the data back to the Step Function    
    event["inferences"] = inferences.decode('utf-8')
    return {
        'statusCode': 200,
        "image_data": event['image_data'],
        "s3_bucket": event['s3_bucket'],
        "s3_key": event['s3_key'],
        "inferences": event['inferences']
    }

#Project2_filterResults
import json


THRESHOLD = .89


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = [float(x) for x in  event["inferences"][1:-1].split(',')]
    
    # Check if any values in our inferences are above THRESHOLD
    threshold = any (x >= THRESHOLD for x in inferences)
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        "image_data": event['image_data'],
        "s3_bucket": event['s3_bucket'],
        "s3_key": event['s3_key'],
        "inferences": event['inferences']
    }
