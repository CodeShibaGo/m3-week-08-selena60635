import requests
from flask import current_app
from flask_babel import _


def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in current_app.config or \
            not current_app.config['MS_TRANSLATOR_KEY']:
        return _('錯誤：翻譯服務未配置。')
    auth = {
        'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'japaneast',
    }
    r = requests.post(
        'https://api.cognitive.microsofttranslator.com'
        '/translate?api-version=3.0&from={}&to={}'.format(
            source_language, dest_language), headers=auth, json=[{'Text': text}])
    if r.status_code != 200:
        return _('錯誤：翻譯服務失敗。')
    return r.json()[0]['translations'][0]['text']