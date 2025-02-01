import boto3 
import json
from dorkingFunctions import getAllDOB, getAllBudgetsPrimitifs


# bedrock = session.client('bedrock-runtime', 'us-west-2') 
# response = bedrock.invoke_model( 
#         modelId='mistral.mistral-large-2407-v1:0', 
#         body=json.dumps({
#             'messages': [ 
#                 { 
#                     'role': 'user', 
#                     'content': 'which llm are you?' 
#                 } 
#              ], 
#          }) 
#        ) 

# print(json.dumps(json.loads(response['body']), indent=4))