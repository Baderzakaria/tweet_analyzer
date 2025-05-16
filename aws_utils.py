import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

POSITIVE_TABLE = "PositiveTweets"
NEGATIVE_TABLE = "NegativeTweets"
NEUTRAL_TABLE = "NeutralTweets"

# Connexion à DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=os.getenv("AWS_REGION"))

def save_comment_to_dynamodb(table_name, text, sentiment):
    try:
        table = dynamodb.Table(table_name)
        table.put_item(
            Item={
                'TweetID': str(hash(text)),
                'Text': text,
                'Sentiment': sentiment
            }
        )
        print(f"Commentaire sauvegardé dans {table_name}")
    except ClientError as e:
        print(f"Erreur lors de l'enregistrement dans {table_name} : {e}")

def get_comments_from_dynamodb(table_name, limit=5):
    try:
        table = dynamodb.Table(table_name)
        response = table.scan(Limit=limit)
        return response.get('Items', [])
    except ClientError as e:
        print(f"Erreur lors de la récupération des commentaires depuis {table_name} : {e}")
        return []

