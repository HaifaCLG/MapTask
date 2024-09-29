from typing import Tuple
import os
import openai

openai.organization = "ADD YOUR ORG"
openai.api_key = os.environ['OPENAI_API_KEY']

# https://platform.openai.com/docs/api-reference/chat/create
# https://platform.openai.com/docs/guides/chat/introduction


def openai_call(messages: list[dict]) -> Tuple[str, bool]:
    try:
        response = openai.ChatCompletion.create(
          model="gpt-4",
          messages=messages
        )

        cs_resp = response.choices[0].message['content']
        finish_reason = response.choices[0]['finish_reason']

        if finish_reason != 'stop':
            print('openai err: ', finish_reason)
            return 'Something went wrong, try again', False
        return cs_resp, True
    except Exception as e:
        print('open ai err:', e)
        return 'Something went wrong, try again', False