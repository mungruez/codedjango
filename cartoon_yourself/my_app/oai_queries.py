from django.conf import settings
import os
import openai
# OpenAI API Key
openai.api_key = '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'

def get_completion(prompt):
    query = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{"role": "user", "content": prompt }]
    )
    response = query.get('choices')[0]['message']['content']
    return response
