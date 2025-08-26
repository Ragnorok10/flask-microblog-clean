#this page will be used to hold a function for MS Translator purposes

#imports
import requests
from flask_babel import _
from flask import current_app

#translate function
def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in app.config or \
            not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: The translation service is not configured') #this will use "_" to spit out a warning if the key is not correct/present in the configuration settings
    auth = {
        'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'westus2',
    }
    r = requests.post(
        'https://api.cognitive.microsofttranslator.com'
        '/translate?api-version=3.0&from={}&to={}'.format(
            source_language, dest_language), headers=auth, json=[{'Text': text}])
    if r.status_code != 200:
        return _('Error: The translation service failed')
    return r.json()[0]['translations'][0]['text']