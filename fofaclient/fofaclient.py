import base64
import json
import re
import time
import urllib

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class TokenInvalid(Exception):
    pass

class FofaError(Exception):
    """docstring for FofaError"""
    def __init__(self, code, message = ""):
        self.code = code
        self.message = message
        super(FofaError, self).__init__(message)
        

class FofaClient(object):
    """docstring for FofaClient"""
    def __init__(self,proxies = None, user_agent =None , captcha_model_path = None):
        super(FofaClient, self).__init__()
        self.API_ENDPOINT = "https://api.fofa.so/v1"
        self.captcha_model_path = captcha_model_path
        self.proxies = proxies
        if user_agent:
            self.ua = user_agent
        else:
            self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
        self.username = None
        self.password = None
        self._display_captcha = False
        self.session =  self.__create_session()


    def __captcha(self,gif):
        import os
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        try:
            # tensorflow full with lite model
            import tensorflow.lite as tflite
        except ImportError:
            try:
                # tensorflow lite with lite model
                # lite  from: pip3 install --index-url https://google-coral.github.io/py-repo/ tflite_runtime
                # Note: no package for python3.9 now (as of 2021.5.31)
                import tflite_runtime.interpreter as tflite 
            except ImportError:
                return None
        try:
            from PIL import Image
        except ImportError:
            return None

        try:
            import importlib_resources
        except ImportError:
            try:
                import importlib.resources as importlib_resources
            except:
                return None

        import numpy as np
        from io import BytesIO

        '''
        lite model
        // full
        import tensorflow.lite as tflite
        //lite  from: pip3 install --index-url https://google-coral.github.io/py-repo/ tflite_runtime
        
        import tflite_runtime.interpreter as tflite 

        img = Image.open(BytesIO(gif)).convert("L")
        img = np.array(img) / 255.0
        np.reshape( img   , input_details[0]['shape'] ).astype('float32')
        interpreter.set_tensor(input_details[0]['index'] , input_data )
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        "".join([ 'abcdfhijklmnopqrstuvwxyz'[i] for i in output_data.argmax(axis=-1)[0] ] )

        '''

        # model = tf.keras.models.load_model("rucaptcha/rucaptcha_model")
        # img = Image.open(BytesIO(gif))
        # img_array = np.array(img) /15.0 # NOTE!!! should same as the data used in training model!!!!
        # res = model(np.array([ img_array ]))
        # return "".join([ CHARLIST[i] for i in res.numpy().argmax(axis = -1)[0]]) 

        CHARLIST = 'abcdfhijklmnopqrstuvwxyz'


        img = Image.open(BytesIO(gif))

        if self.captcha_model_path:
            interpreter = tflite.Interpreter(model_path=self.captcha_model_path)
        else:
            ref = importlib_resources.files("fofaclient") / "model" / "rucaptcha.tflite"
            with importlib_resources.as_file(ref) as path:
                # todo use pkg_resources
                interpreter = tflite.Interpreter(model_path=str(path))

        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Sine our model use 16bits color training, we do not normalize here.
        img_array = np.array(img)
        input_data = np.array(img_array.reshape(input_details[0]['shape'])).astype('float32')
        interpreter.set_tensor(input_details[0]['index'], input_data)

        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        return "".join([ CHARLIST[i] for i in output_data.argmax(axis = -1)[0]])


    def __create_session(self):
        s = requests.session()
        retry = Retry(total=5, status_forcelist=[429, 500, 502, 503, 504],backoff_factor = 0.1)
        s.mount("https",HTTPAdapter(max_retries= retry ))
        s.proxies = self.proxies
        s.headers.update({"User-Agent": self.ua})
        return s

    def login(self , username,password, display_captcha_if_auto_failed = False):
        tmp_session = self.__create_session()
        prelogin = tmp_session.get("https://i.nosec.org/login?service=https%3A%2F%2Ffofa.so%2Flogin")
        para = re.findall(r'''type="hidden" name="((?!authenticity_token).*?)".*value="(.*?)"''',prelogin.text)
        # authenticity_token from csrf-token not from  type="hidden" name="authenticity_token" 
        authenticity_token = re.findall(r'''"csrf-token".*?content="(.*?)"''',prelogin.text)[0]

        gif = tmp_session.get("https://i.nosec.org/rucaptcha").content
        captcha = self.__captcha(gif)

        if not captcha:
            if display_captcha_if_auto_failed:
                import tempfile
                with tempfile.NamedTemporaryFile(prefix="fofa",suffix=".gif") as f:
                    f.write(gif)
                    print("Open ",f.name, " to see the gif")
                    captcha = input(">")
            else:
                raise TokenInvalid("no captcha")


        login_dict = {"username":username,"password":password , "_rucaptcha": captcha  ,"utf8": "✓" }
        for i in para:
            login_dict.update({i[0]:i[1]})
        login_dict["authenticity_token"] = authenticity_token

        resp = tmp_session.post("https://i.nosec.org/login" , data = login_dict)

        if resp.status_code == 200 and len(resp.history) >=1 and resp.history[0].status_code == 303:
            self.access_token = tmp_session.cookies['fofa_token']
            self._userinfo = json.loads(urllib.parse.unquote_plus(tmp_session.cookies['user']))
            self.refresh_token = tmp_session.cookies['refresh_token']
            self.username = username
            self.password = password
            self._display_captcha = display_captcha_if_auto_failed
        elif "登录验证码错误" in resp.text:
            return self.login(username,password,display_captcha_if_auto_failed)
            pass
        else:
            # "用户名或密码错误" in resp.text:
            # 您的登录请求没有包含有效的登录授权 recaptcha expire  after 2min maybe
            raise TokenInvalid("login failed")
        tmp_session.close()
        return self
    

    def userinfo(self):
        '''
        id:
        mid: ???
        is_admin
        username:
        nickname
        email:
        avatar_medium / avatar_thumb
        key: API_KEY // not appear in cookie["user"] ,only appear via APIENDPOINT /me/
        rank_name:
        rank_level: 0-> 注册用户 1-> 普通会员 2-> 高级会员 3-> 企业会员
        company_name:
        coins:
        credits:
        expiration: "-"
        login_at:   0 via /me/  , real in cookie
        '''
        return self._userinfo

    def login_with_refresh_token(self , refresh_token):
        access_token_info = self.trade_access_token_with_refresh_token(refresh_token)
        self.access_token = access_token_info["access_token"]
        self._userinfo = access_token_info["info"]
        self.refresh_token = refresh_token
        return self

    def trade_access_token_with_refresh_token(self,refresh_token):
        mid = refresh_token.split(".")[1]
        mid_raw = json.loads(base64.b64decode(mid+'==') )# padding
        assert mid_raw["iss"] == "refresh"
        return self._get_unauth("/users/refresh", extra_headers = {"Authorization": refresh_token})

    def search_count(self,q,full=False):
        '''
        only get how many records we can fetch.
        '''
        return self.search(q,full = full)["page"]["total"]

    def __search_limit(self):
        # limit from https://fofa.so/static_pages/vip
        if self._userinfo["rank_level"] > 0:
            PAGE_SIZE = 20
            MAX_COUNT = 10_000
        else:
            # if you use 20 , then you can only visit 2 page , 2*20 results . else you can visit 5 pages , 5 * 10 results
            PAGE_SIZE = 10 
            MAX_COUNT = 50
        return PAGE_SIZE , MAX_COUNT        

    '''
    In Fofa Web
    the first query is not XHR and condition is not quoted like test and asn!=1123
    but the next query is XHR and condition is quoted  "test" and asn!="1123"
    Tested: q in response will be modified automatically

    Returns results, info
        results max count of items of your level (list or iterable).
        info dict keys:
                    max_total: max count globally at any level (number)
                    q: normalized query (string)
                    full: full result or not (bool)
                    mode: normal/extend
                    is_ipq
                    took

    '''
    def search_all(self , q , full=False , iterable = False):
        PAGE_SIZE , MAX_COUNT = self.__search_limit()
        pg1 = self.search(q,ps = PAGE_SIZE ,full = full)
        max_total = pg1["page"]["total"]
        info = {"max_total":max_total, "q": pg1["q"], "full": pg1["full"], "mode": pg1["mode"], "is_ipq": pg1["is_ipq"], "took": pg1["took"]}
        
        # mode , is_ipq   ..... infos
        total =  MAX_COUNT if max_total > MAX_COUNT else max_total
        if iterable:
            def _iter():
                start = 2
                for i in pg1["assets"]:
                    yield i
                yield_count = len(pg1["assets"])
                while total - yield_count > 0:
                    page = self.search(q, pn = start , ps = PAGE_SIZE , full = full )
                    for i in  page["assets"]:
                        yield i
                    yield_count += len(page["assets"])
                    start += 1
                pass
            return _iter(), info
        else:
            assets_all = pg1["assets"]
            start = 2
            while total - len(assets_all) > 0:
                page = self.search(q, pn = start , ps = PAGE_SIZE , full = full )
                assets_all += page["assets"]
                start += 1

            return assets_all , info

    '''
    Request:
    q: query content
    qbase64: base64 of q
    full: show result older than 1 yr if True
    ps: page size 10/20 two choice
    pn: page number
    '''
    '''
    Response:
data{
    took: "spended time in ms"
    q:
    qbase64
    mode: normal / extended 
    is_ipq: false // is unique ip?
    "page":{ "num":"pagenum" ,"size":"pagesize", "total":"total"  }
    assets: [
{
        "mtime": "2021-05-25 15:00:40",
        type:"subdomain" // two kind 类型分布(网站 , 协议) subdomain ,service
            "app_servers": [
            {
                "name": "apache",
                "code": "YXBwc2VydmVyPSJhcGFjaGUi"
            }
        ],
        "asn_no": 1234,
        "asn_org": "xxxx",
        'banner': "HTTP/1.1 200 OK\r\nSContent-Type: text/html; charset=UTF-8\r\nContent-Length: 125",
        "base_protocol": "tcp",
        "cert": "Version:  v3\nSerial Number: xxxx\nSignature Algorithm: "
}        "certs_is_valid": true,
        "certs_issuer_cn": "DigiCert SHA2 Secure Server CA",
        "certs_issuer_org": "DigiCert Inc",
        "certs_not_after": "1111-11-11 11:11:11",
        "certs_not_before": "1212-12-12 12:12:12",
        "certs_subject_cn": "xxx.xxx.xx",
        "certs_subject_org": "xxx.xxx.xx",
        "certs_valid_type": "", //?? maybe text
        "city": "Boydton",
        "city_code": "",
        "country": "美国",
        "country_code2": "US",
        "country_qcode": "Y291bnRyeT0iVVMi",
        "domain": "", // rPTR
         "favicon": "https://xxxx/favicon.ico",
        "favicon_hash": -1234,
        "header": "HTTP/1.1 200 OK\r\nConnection: close\r\n",
        "host": "https://xxxx",
        "icp": "", //beian hao?
        "id": "https://xxxx",
        "ip": "xxxx",
        "is_fraud": false,
        "is_honeypot": false,
        "isp": "", //?
        "link": "https://xxxx",
        
        "os": [], //?
        "port": 443,
        "protocol": "https",
        "region": "xxx",
        "server": "Apache",
        "struct_info": [],
        "title": "xxx",
        @20210601 new added?
        "dom_hash":
        "dom_sim_hash"

    ]

}

    '''
    def search(self,q , pn =1 , ps = 10 , full=False ):
        params = { "q":q , "qbase64":base64.b64encode(q.encode("utf-8")) , "ps":ps , "pn":pn , "full": "true" if full else "false"}
        data = self._get("/search", params)
        return data

    '''
    Request
    mode: normal/extended see: https://fofa.so/static_pages/api_help mode section
    '''
    
    '''
    since sign= is return via url_key in page from server 
    so you need visit page to get that url_key

    qbase64=x&mode=normal&full=false&ts=x&app_id=9e9fb94330d97833acfbc041ee1a76793f1bc691&sign=E6

    qbase64 will be modified (yes!)?  mode is dependes on the input "q" ,
    '''
    def stats(self, q , full = False):
        with self.__create_session() as s:
            resp = s.get("https://fofa.so/result" , params = { "qbase64": base64.b64encode(q.encode("utf-8")) ,"full": "true" if full else "false"})
            params = re.findall(r'''url_key.*?:.*?"(.*?)"''',resp.text)[0].encode().decode("unicode_escape")
            return self._get("/search/stats",params)


    def rules_all(self,keyword):
        result_all = []
        
        page_one = self.rules(keyword)
        total = page_one["page"]["total"]
        result_all += page_one["rules"]
        start = 2
        while total - len(result_all) > 0:
            page = self.rules(keyword,pn = start)
            result_all += page["rules"]
            start += 1

        return result_all


    '''
    Rule is a related item recommendation , (can replace rules/categories api in https://fofa.so/library?cid=0&keyword)
    Request
    keyword:
    ps: page size
    pn: page number
    '''
    '''
    Repsonse
    Note: in page 1 always only 3 items for display
    Note: ps param not work
    data:{
        "rules":[
            {  "name": xxx ,
                "code":"base64 query args"}
            ],
        "page":{ "num":"pagenum" ,"size":"pagesize", "total":"total"  }

    }

    '''
    def rules(self,keyword, pn = 1, ps = 10 ):
        return self._get("/search/rules",params = { "keyword":keyword, "ps":ps , "pn":pn })

    # This api endpoint is not ready? always 403
    def hosts_content(self, host):
        return self._get("/search/hosts/content" , params = {"host":host})

    # 1. in <div class="el-scrollbar__view"> 2. in window.__NUXT__ -> text
    def hosts_content_old(self,host):
        with self.__create_session() as s:
            resp = s.get("https://fofa.so/result/website?host={}".format(host))
            res = re.findall(r'''data:\[{text:\"(.*)\",list''' , resp.text)
            if len(res) > 0:
                return res[0].encode().decode("unicode_escape")
            return None

    # same as https://fofa.so/hosts/<host> only show port rule with asterisk
    def hostinfo(self,host):
        return self._get("/host/{}".format(host))

    #show all port info , more useful than `hostinfo`
    '''
    Response
    {'key': '<unique hash>', // maybe unique hash
        'list': {'443': {'asn': xxx, ...}
        'remain_count': 0, // what is this?
        'title': '<host>'}
    '''
    def hostsinfo(self,host):
        return self._get("/hosts/{}".format(host))

    '''the same as set-cookie userinfo and result of getrefreshtoken'''
    def me(self):
        # TODO: should we update userinfo?
        # maybe since API_KEY only from here
        return self._get("/m/")

    def _is_token_valid(self,token):
        mid = token.split(".")[1]
        mid_raw = json.loads(base64.b64decode(mid+'==') )# padding 

        t = time.time()
        return t < mid_raw["exp"]

    def _get_unauth(self, path, params = None , extra_headers = None):
        return self.__get_impl(path, params, extra_headers)
        pass

    def _get(self, path, params = None , extra_headers = None):
        if not self._is_token_valid(self.access_token):
            if self._is_token_valid(self.refresh_token):
                res = self.trade_access_token_with_refresh_token(self.refresh_token)
                self.access_token = res["access_token"]
                self._userinfo = res["info"]
            elif self.username is not None and self.password is not None:
                self.login(self.username, self.password , self._display_captcha)
            else:
                raise TokenInvalid("refresh_token expired")
        headers = { "Authorization": self.access_token}
        if extra_headers:
            headers.update(extra_headers)
        return self.__get_impl(path, params,headers)


    def __get_impl(self, path, params = None , headers = None):
        resp = self.session.get(self.API_ENDPOINT+path , params = params , headers = headers)
        # todo retry on fail!
        if resp.status_code !=200 :
            resp.raise_for_status()

        resp_json = resp.json()
        if resp_json["code"]!= 0:
            # code -20 : token expired
            raise FofaError(resp_json["code"],resp_json["message"])
        return resp_json["data"]
