import argparse
import requests
import json
import os


def send_email(recipient_email: str, subject: str, content: str) -> None:
    token = os.environ.get('POSTMARK_API_KEY')  # Get Postmark API token from environment
    if not token:
        raise ValueError("POSTMARK_API_KEY environment variable not set")
    outbound_email = os.environ.get('PERSONAL_EMAIL', 'jcran@0x0e.org')

    headers = {
        'user-agent': 'my-app/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Postmark-Server-Token': token
    }

    data = json.dumps({
        'From': outbound_email,
        'To': recipient_email,
        'Subject': subject,
        'HtmlBody': content
    })

    r = requests.post('https://api.postmarkapp.com/email', headers=headers, data=data)
    response = json.loads(r.text)
    
    if response['ErrorCode'] == 0:
        print(f'Message ID = {response["MessageID"]}')
    else:
        print('Message not sent')


# def main():
#     parser = argparse.ArgumentParser(description='Send an email using the Postmark API')
#     parser.add_argument('--email', required=True, help='Recipient email address')
#     parser.add_argument('--topic', required=True, help='Email subject')
#     parser.add_argument('--content', required=True, help='Email content')

#     args = parser.parse_args()
#     send_email(args.email, args.topic, args.content)


# if __name__ == '__main__':
#     main()

