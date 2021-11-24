import requests
import re
import ast
import json
import urllib
from requests.models import Response

from requests.sessions import Request

class Translator:
    # Python port of https://github.com/plainheart/bing-translate-api

    TRANSLATE_API_ROOT = 'https://bing.com'
    TRANSLATE_WEBSITE = TRANSLATE_API_ROOT + '/translator'
    TRANSLATE_API = TRANSLATE_API_ROOT + '/ttranslatev3?isVertical=1\u0026'
    TRANSLATE_SPELL_CHECK_API = TRANSLATE_API_ROOT + '/tspellcheckv3?isVertical=1\u0026'
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    CONTENT_TYPE = 'application/x-www-form-urlencoded'

    MAX_TEXT_LEN = 1000
    MAX_CORRECT_TEXT_LEN = 50
    tokenExpiryInterval = 0
    RequestCount = 0

    IG = ''
    IID = ''
    Token = ''
    Key = ''
    Cookies = ''

    isVertical = False
    RequestSession = None

    
    def Translate(self, text:str, from_l:str, to_l:str):
        if len(text) > self.MAX_TEXT_LEN:
            raise Exception("The max length of the text must be " + self.MAX_TEXT_LEN + ". Please shorten the text.")
        req_body = urllib.parse.urlencode(self.MakeRequest(False, text, from_l, to_l))
        req_url = self.MakeRequestUrl(False)
        resp = self.RedirectedPost(req_url, req_body)
        resp.encoding = 'utf-8'
        return resp.json()

        
    
    def RedirectedPost(self, url:str, data:str) -> Response:
        # Keep trying to access the actual POST end point
        # because my default requests library will try use
        # GET once it hits a redirect
        while True:
            rep = requests.post(url,
                data=data,
                allow_redirects=False,
                headers={
                    'Content-Type' : 'application/x-www-form-urlencoded',
                    'User-Agent' : self.USER_AGENT,
                    'Referer' : self.TRANSLATE_WEBSITE,
                    'Accept' : 'application/json',
                    'Accept-Encoding' : 'gzip, deflate',
                    'Connection':'close',
                    'Cookie' : json.dumps(self.Cookies)
                })
            if rep.status_code in [301, 302]:
                url = rep.headers.get('location')
                continue
            return rep

    def fetchGlobalConfig(self) -> None:
        # Fetch tokens from the bing website and store them in this
        # class so it can be used later... 
        try:
            self.RequestSession = requests.Session()
            response = self.RequestSession.get(self.TRANSLATE_WEBSITE, headers={'user-agent' : self.USER_AGENT})
            self.IG = re.findall('IG:"([^"]+)"', response.text)[0]
            self.IID = re.findall('data-iid="([^"]+)"', response.text)[0]
            self.Key, self.Token, self.tokenExpiryInterval, self.IsVertical = json.loads(re.findall('params_RichTranslateHelper\s?=\s?([^\]]+\])', response.text)[0])
            self.RequestCount = 0

            # Get the cookies from the response header and parse them with
            # regex because request doesn't have in built functions to properly parse
            # set-cookie headers. Either that or I didn't read the docs properly
            self.Cookies = response.request.headers['cookie']  + ', ' + response.headers['set-cookie']
            self.Cookies = re.split('[,;] ([A-Z_][A-Z])', self.Cookies)
            for x in range(1, int((len(self.Cookies) - 1) / 2) + 1):
                self.Cookies[x] = self.Cookies[x] + self.Cookies[x + 1]
                del self.Cookies[x + 1]
        except: 
            print("Failed to get configuration data.")


    def MakeRequest(self, isSpellCheck:bool, text:str, fromLang:str, toLang:str) -> dict:
        # Make a request for the server to handle. This doesn't need its own function
        # but the original npm module did, so Im gonna include this
        body = {
            'fromLang' : fromLang,
            'text' : text,
            'token' : self.Token,
            'key' : str(self.Key),
            'to' : toLang   
        }
        if (not isSpellCheck): body['to'] = toLang
        return body

    def MakeRequestUrl(self, isSpellCheck:bool) -> str:
        # Get the url to request to based on whether or not this a spell check request.
        url = self.TRANSLATE_SPELL_CHECK_API if isSpellCheck else self.TRANSLATE_API + ('' if self.IG.isspace() else '&IG=' + self.IG) + ('' if self.IID.isspace() else '&IID=' + self.IID + '.' + str(self.RequestCount))
        self.RequestCount += 1
        return url


        