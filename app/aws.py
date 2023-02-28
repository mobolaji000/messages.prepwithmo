import json
import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

class AWSInstance():
    def __init__(self):
        pass

    def getInstance(self, service_name):
        region_name = "us-east-2"

        aws_access_key_id = os.environ.get('aws_access_key_id','')
        aws_secret_access_key = os.environ.get('aws_secret_access_key', '')

        #print("aws_access_key_id is: "+str(aws_access_key_id))

        if aws_access_key_id != '' and aws_secret_access_key != '':
            session = boto3.session.Session(aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
        else:
            session = boto3.session.Session()
        client = session.client(
            service_name=service_name,
            region_name=region_name
        )

        return client

    def get_secret(self, secret_name, secret_key):

        secret_name = secret_name
        client = self.getInstance('secretsmanager')
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = json.loads(get_secret_value_response['SecretString'])[secret_key]
            else:
                print("secret is not string!")


        return secret


    def send_email(self, to_addresses=['mo@vensti.com'], message='perfectscoremo', subject='perfectscoremo',email_attachments_and_their_details={}):
        SENDER = "Perfect Score Mo <mo@info.perfectscoremo.com>"
        RECIPIENT = to_addresses#+['mo@vensti.com'], #TODO uncomment this after you are done testing; this ensures you are copied in every email so you can catch errors. After a while, you can set up a Gmail filter for these to go to so your inbox is not overwhelmed
        SUBJECT = subject

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = "Hello,\r\nYour email client can't read this message."

        BODY_HTML = message

        CHARSET = "UTF-8"
        client = self.getInstance('ses')
        # Create a multipart/mixed parent container.
        msg = MIMEMultipart('mixed')
        # Add subject, from and to lines.
        msg['Subject'] = SUBJECT
        msg['From'] = SENDER
        msg['To'] = ', '.join(RECIPIENT)

        # Create a multipart/alternative child container.
        msg_body = MIMEMultipart('alternative')

        # Encode the text and HTML content and set the character encoding. This step is
        # necessary if you're sending a message with characters outside the ASCII range.
        textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
        htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

        # Add the text and HTML parts to the child container.
        msg_body.attach(textpart)
        msg_body.attach(htmlpart)

        for attachment_id,(attachment_name,attachment) in email_attachments_and_their_details.items():
            ATTACHMENT = attachment_name

            #att = MIMEApplication(open(ATTACHMENT, 'rb').read())
            att = MIMEApplication(attachment.getvalue())

            #att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(ATTACHMENT))
            att.add_header('Content-Disposition', 'attachment', filename=ATTACHMENT)

            # Add the attachment to the parent container.
            msg.attach(att)
        # print(msg)

        # Attach the multipart/alternative child container to the multipart/mixed
        # parent container.
        msg.attach(msg_body)

        try:
            # Provide the contents of the email.
            response = client.send_raw_email(
                Source=SENDER,
                Destinations=[
                    ', '.join(RECIPIENT)
                ],
                RawMessage={
                    'Data': msg.as_string(),
                },
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            #TODO print job id in logs that same email is sent. Same for sms. Will make debugging easier.
            print("Email sent! Message ID:"),
            print(response['MessageId'])
