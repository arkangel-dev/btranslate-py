# btranslate-py
Bing Translation Site Emulator | A thingy to access Bing Translate services without an API key by emulating client side services the Bing Translate website would run in the browser. (Python port of [plainheart/bing-translate-api](https://github.com/plainheart/bing-translate-api))

## Usage
```py
import btranslate
import json

translator = btranslate.Translator()
translator.fetchGlobalConfig()
print(translator.Translate("Hello World. How are you?", 'en', 'dv'))
```

```
[{
    'detectedLanguage': {'language': 'en', 'score': 1.0},
    'translations': [{
    	'text': 'ދުނިޔެއަށް ސަލާމް. ހާލު ކިހިނެއްތަ?',
    	'to': 'dv',
    	'sentLen': {
    		'srcSentLen': [13, 12],
    		'transSentLen': [19, 16]
         }
    }]
}]
```