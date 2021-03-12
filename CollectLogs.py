import json

import json
import boto3
import paramiko
import os
import datetime


def btos(by):
    return (str(by, 'utf-8'))
    

def log(txt):
    s3_logger = boto3.client('s3')
    x = datetime.datetime.now()
    date = x.strftime("%d-%m-%Y %H:%M:%S")
    data=s3_logger.get_object(Bucket='assignments3toec2', Key='Activitylog.txt')
    contents = data['Body'].read()
    print(contents)
    msg=str(contents)+date+ ' ' +txt
    s3_logger.put_object(Body=msg, Bucket='assignments3toec2', Key='Activitylog.txt')

def lambda_handler(event, context):
    
    x = datetime.datetime.now()
    date = x.strftime("%d-%b-%Y")

    # boto3 client
    client = boto3.client('ec2')
    s3_client = boto3.client('s3')
    
    # getting instance information
    describeInstance = client.describe_instances()

    
    hostPublicIP=[]
    # fetchin public IP address of the running instances
    for i in describeInstance['Reservations']:
        for instance in i['Instances']:
            if instance["State"]["Name"] == "running":
                hostPublicIP.append(instance['PublicIpAddress'])
    
    print(hostPublicIP)
    
    # downloading pem filr from S3
    s3_client.download_file('assignments3toec2','lseg2.pem', '/tmp/file.pem')

    # reading pem file and creating key object
    key = paramiko.RSAKey.from_private_key_file("/tmp/file.pem")
    # an instance of the Paramiko.SSHClient
    ssh_client = paramiko.SSHClient()
    # setting policy to connect to unknown host
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host=hostPublicIP[0]
    print("Connecting to : " + host)
    # connecting to server
    ssh_client.connect(hostname=host, username="ubuntu", pkey=key)
    print("Connected to :" + host)

    # command list
    #command = f'cat /var/log/nginx/access.log | grep "{date}"'
    
   
    stdin , stdout, stderr = ssh_client.exec_command(f'cat /var/log/nginx/access.log | grep "{date}"')
    out = btos(stdout.read()).split("\n")
    #output1 = out[5]
    print(out)
    #log(f'Status of Server: {output1}')
    
    for i in out:
        print(i)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Thanks!')
    }
