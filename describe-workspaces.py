import boto3
import csv
import json
import io
from datetime import datetime

def lambda_handler(event, context):
    # Initialize a boto3 client for AWS Workspaces
    workspaces_client = boto3.client('workspaces')
    
    # Initialize a boto3 resource for S3
    s3 = boto3.resource('s3')
    
    # Specify your S3 bucket name
    bucket_name = 'your-s3-bucket-name'
    # Specify the file name with timestamp
    file_name = f'workspace_report_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'

    # Call the describe_workspaces API
    workspaces = workspaces_client.describe_workspaces()
    
    # Call the describe_workspaces_connection_status API
    connection_status = workspaces_client.describe_workspaces_connection_status(
        WorkspaceIds=[ws['WorkspaceId'] for ws in workspaces['Workspaces']]
    )

    # Create a CSV in-memory file
    csv_file = io.StringIO()
    csv_writer = csv.writer(csv_file)
    
    # Write the CSV header
    csv_writer.writerow([
        'WorkspaceId', 'DirectoryId', 'UserEmail', 
        'ClientVersion', 'ClientIpAddress', 
        'LoginTime', 'ClientPlatform'
    ])
    
    # Compile the detailed workspace information
    for ws in workspaces['Workspaces']:
        # Retrieve connection status for the current Workspace
        ws_status = next((status for status in connection_status['WorkspacesConnectionStatus'] if status['WorkspaceId'] == ws['WorkspaceId']), {})
        
        # Compile details for each workspace
        workspace_info = {
            'WorkspaceId': ws['WorkspaceId'],
            'DirectoryId': ws['DirectoryId'],
            'UserEmail': ws['UserName'] + '@example.com',  # Replace logic as needed
            'ClientVersion': ws_status.get('ClientVersion', 'N/A'),
            'ClientIpAddress': ws_status.get('ClientIpAddress', 'N/A'),
            'LoginTime': str(ws_status.get('LastKnownUserConnectionTimestamp', 'N/A')),
            'ClientPlatform': ws_status.get('ClientPlatform', 'N/A'),
        }
        
        # Write row to CSV
        csv_writer.writerow(workspace_info.values())

    # Move the CSV content to the beginning
    csv_file.seek(0)

    # Upload the CSV file to the specified S3 bucket
    s3.Bucket(bucket_name).put_object(Key=file_name, Body=csv_file.getvalue())

    # Return a success message along with the file path in S3
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Report successfully uploaded to s3://{bucket_name}/{file_name}'
        })
    }
