#!/usr/bin/env python3
import os
import sys
import json
import pathlib
import argparse
import traceback

from urllib import parse as urllib
from urllib import request


def send_message(api_url: str, chat_id: str, text: str) -> dict:
    msg = urllib.urlencode({'chat_id': chat_id, 'text': text})

    req = request.Request(
        url=api_url,
        method='POST',
        data=msg.encode()
    )

    with request.urlopen(req) as client:
        return json.loads(client.read().decode())


def print_result(resp: dict) -> None:
    print('status:', resp['ok'])
    print('message_id:', resp['result']['message_id'])
    print('chat_id:', resp['result']['chat']['id'])
    print('chat_type:', resp['result']['chat']['type'])
    print('src_user:', resp['result']['from']['username'])
    print('dst_user:', resp['result']['chat']['username'])


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('chat', help='Set chat ID.')
    parser.add_argument('text', help='Set message text or file.')
    parser.add_argument('-f', dest='is_file', action='store_true', help='Read text from a file.')
    return parser.parse_args()


try:
    TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN', '')
    if not TELEGRAM_API_TOKEN:
        raise ValueError('TELEGRAM_API_TOKEN is not set!')

    TELEGRAM_API_URL = '{}/bot{}/{}'.format('https://api.telegram.org', TELEGRAM_API_TOKEN, 'sendMessage')
    args = get_args()

    if args.is_file:
        file = pathlib.Path(args.text)
        print_result(send_message(TELEGRAM_API_URL, args.chat, file.read_text()))

    else:
        print_result(send_message(TELEGRAM_API_URL, args.chat, args.text))

except Exception:
    traceback.print_exc()
    sys.exit(1)
