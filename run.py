import btranslate
import json

translator = btranslate.Translator()
translator.fetchGlobalConfig()
print(translator.Translate("Hello World. How are you?", 'en', 'dv'))