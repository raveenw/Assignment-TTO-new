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
    data=s3_logger.get_object(Bucket='assignments3toec2', Key='log.txt')
    contents = data['Body'].read()
    #print(contents)
    msg=date+ ' ' +txt
    s3_logger.put_object(Body=msg, Bucket='assignments3toec2', Key='log.txt')

def lambda_handler(event, context):
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
    
    #print(hostPublicIP)
    
    # downloading pem file from S3
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
    log("Connected to :" + host)
    
    # command list
    
    # to get the nginx service status
    stdin , stdout, stderr = ssh_client.exec_command('systemctl is-active nginx.service')
    out = btos(stdout.read()).split("\n")
    output = out[0]
    print("Status of Nginx Service :" +output)
    log(f'Status of Nginx Service : {output}')
    
    # to get the http response
    stdin , stdout, stderr = ssh_client.exec_command('tail -3 /var/log/nginx/access.log')
    out = btos(stdout.read()).split("\n")
    #output3 = out[0]
    #print("Access log :" +output3)
    #log(f'Access log : {output3}')
    for i in out:
        print(i)
    
    if output != 'active':
        stdin , stdout, stderr = ssh_client.exec_command('sudo systemctl start nginx.service')
        output = btos(stdout.read())
       # print(f'errors  {stdout}' )
        stdin , stdout, stderr = ssh_client.exec_command('systemctl is-active nginx.service')
        out = btos(stdout.read()).split("\n")
        output1 = out[0]
        print("Status of Nginx Service after restart :" + output1)
        log(f'Status of Nginx Service after restart : {output1}')
        
        if output1 != 'active':
            print('send mail')
            #mail
       
        else:
            print('Service is restarted')
            print(f"Nginx Service is on {output1} state")
            return {
        'statusCode': 200,
        'body': json.dumps('Thanks!')
    }
