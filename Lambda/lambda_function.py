import json
import urllib.parse
import boto3
import logging
import botostubs



s3 = boto3.client('s3')

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)



def detect_labels(bucket,photo):
    
    rekog =boto3.client('rekognition') # type: botostubs.rekognition
    response = rekog.detect_labels(Image = {'S3Object' : {'Bucket': bucket, 'Name': photo}},MinConfidence=80,MaxLabels=3)

    #keep labels in dictionary
    result={}
    for labels in response['Labels']:
        result.update({labels['Name']:round(labels['Confidence'],2)})
    print('Detected labels for ',photo, result)

    return result

    
    
def lambda_handler(event, context):

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    dyndb = boto3.resource('dynamodb')
    
    table = dyndb.Table('detected_labels')

    try:
        
        print('Bucket: ' + bucket + ' Key: ' + key)
        
        labels = detect_labels(bucket, key)

        for label in labels:
            item = {}
            print("Label:", label)
            
            item['Label'] =  label
            item['Confidence'] = str(labels[label])
            item['Image'] = bucket+"/"+key
            
            print(item)
            
            table.put_item(
                Item=item
            )
        
    except Exception as e:
        print(str(e))
        print(f'Error getting object {key} from bucket {bucket}. Make sure they exist and your bucket is in the same region as this function.')
        raise e
    
    return {
        'statusCode': 200,
        'body': json.dumps('operation success')
    }
