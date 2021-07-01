# fofaclient
## Supported Fofa Version
	
	Start from 4.7.112

## Feature

	- Bypass rucaptcha via ML
	- Support refresh_token
	- Auto aggregate results
	- fetch results via generator

## Install
```bash
pip install --extra-index-url https://google-coral.github.io/py-repo/ git+https://github.com/jackyzy823/fofaclient

```
if pip failed with 404 not found , please upgrade pip

## Requirements
	1. Common
		- Requests
	2. Using Model
		- Pillow
		- tflite_runtime or tensorflow

			tflite_runtime via pip3 install --index-url https://google-coral.github.io/py-repo/ tflite_runtime
			NOTE: python 3.9 is not supported
	3. Training Model
		- Pillow
		- tensorflow

		- gcc or other compilers (to compile rucaptcha)


## How To

- Training Model
	1. generate image via a modified version of https://github.com/huacnlee/rucaptcha/blob/main/ext/rucaptcha/rucaptcha.c

	we use the config    black_white length = 5 strikethrough = true  outline = false  which is used by fofa
	2. Training

		study from: https://github.com/JackonYang/captcha-tensorflow/blob/master/captcha-solver-tf2-4digits-AlexNet-98.8.ipynb

### Usage
```python
import fofaclient
client = fofaclient.FofaClient(proxies =None).login("email","password")
# or
# client = fofaclient.FofaClient(proxies =None).login_with_refresh_token("eJ........")
res , info = client.search_all("testquery",iterable = True)
max_count = info["max_count"]
max_count = client.search_count("testquery", full=True)
stat = client.stats("testquery")
me = client.me()
rules = client.rules_all("testrule")
```



### TODO
1. add sleep argments for `_all` function to avoid possible 502
2. can recover when break in middle
3. type * id maybe unique key

### API Research from `https://fofa.so/_nuxt/b18bc5a.js`

```js
        r('request', {
          getUserInfo: function () {
            return s.$get('/m/')
          },
          getSearchInput: function (e) {
            return s.$get('/search/tip', {
              params: e
            })
          },
          signOut: function () {
            return s.$get('/m/logout')
          },
          getLoginInfo: function (e) {
            return s.$get('/users/login', { //params unknown
              params: e
            })
          },
          getLoginOut: function (e) {
            return s.$get('https://i.nosec.org/logout', {
              params: e
            })
          },
          getCeshiLoginInfo: function (e) {
            return s.$get('/login', {
              params: e
            })
          },
          refreshApiKey: function () {
            return s.$get('/m/acc-key/refresh') 
          },
          getPersonalCenter: function () {
            return s.$get('/m/profile')
          },
          getMyRules: function (e) {
            return s.$get('/m/rules', {
              params: e
            })
          },
          getCategories: function () {
            return s.$get('/m/categories')
          },
          addRules: function (e) {
            return s.$post('/m/rules', e)
          },
          getRulesInfo: function (e) {
            return s.$get('/m/rules/'.concat(e))
          },
          getSitesCompanies: function (e) {
            return s.$get('/m/rule/sites/companies', {
              params: e
            })
          },
          editRules: function (e, t) {
            return s.$put('/m/rules/'.concat(e), t)
          },
          deleteRules: function (e, t) {
            return s.$delete('/m/rules/'.concat(e, '/cid/').concat(t))
          },
          getApplicationWebsite: function (e) {
            return s.$get('/m/rule/sites', {
              params: e
            })
          },
          getCompanies: function (e) {
            return s.$get('/m/rule/companies', {
              params: e
            })
          },
          getMyPocs: function (e) {
            return s.$get('/m/pocs', {
              params: e
            })
          },
          rulesStat: function () {
            return s.$get('/rules/stat')
          },
          rulesCategories: function (e) {
            return s.$get('/rules/categories', {
              params: e
            })
          },
          categoriesMore: function (e, t) {
            return s.$get('/rules/categories/'.concat(e), {
              params: t
            })
          },
          help: function () {
            return s.$get('/help')
          },
          helpSearch: function (e) {
            return s.$get('/help/search/' + e)
          },
          getTransaction: function (e, t) {
            return s.$get('/m/finance/logs/'.concat(e), {
              params: t
            })
          },
          addWithdrawal: function (e) {
            return s.$post('/m/finance/withdraw', e)
          },
          getAccCategory: function (e) {
            return s.$get('/m/finance/acc/'.concat(e))
          },
          rechargeF: function (e, t) {
            return s.$post('/m/orders/'.concat(e), t)
          },
          getOrderNo: function (e, t) {
            return s.$get('/m/orders/pay/'.concat(e), {
              params: t
            })
          },
          addBankCard: function (e) {
            return s.$post('/m/finance/bankcard', e)
          },
          deleteBank: function (e) {
            return s.$delete('/m/finance/acc/bank/'.concat(e))
          },
          submitAssets: function (e) {
            return s.$post('/m/assets', e)
          },
          getDownloads: function (e) {
            return s.$get('/m/downloads', {
              params: e
            })
          },
          getSearchRules: function () {
            return s.$get('/m/search/rules')
          },
          getAreas: function (e) {
            return s.$get('/m/areas/'.concat(e))
          },
          submitReport: function (e) {
            return s.$post('/m/reports', e)
          },
          getReportInfo: function (e) {
            return s.$get('/m/reports/'.concat(e))
          },
          getResultSearch: function (e) {
            return s.$get('/search', { //done 
              params: e
            })
          },
          getRelevantSearch: function (e) {
            return s.$get('/search/rules', { //done
              params: e
            })
          },
          searchDownload: function (e) {
            return s.$post('/m/search/download', e)
          },
          getHostsContent: function (e) {
            return s.$get('/search/hosts/content', { // 401?
              params: e
            })
          },
          getSearchStat: function (e) {
            return s.$get('/search/stats', { // need sign from webpage
              params: e
            })
          },
          getSearchIconSimilar: function (e) {
            return s.$get('/m/search/icons', {
              params: e
            })
          },
          getDomainMore: function (e) {
            return s.$get('/search/icons/more', {
              params: e
            })
          },
          getHostsInfo: function (e) {
            return s.$get('/hosts/'.concat(e)) 
          },
          getHostInfo: function (e) {
            return s.$get('/host/'.concat(e))
          },
          getCaptcha: function () {
            return s.$get('/captcha') // new kind of captcha , do not know how to use
          },
          questionFeedback: function (e) {
            return s.$post('/feedback', e)
          },
          joinEnterpriseMembers: function (e) {
            return s.$post('/m/contact_us', e)
          },
          downloadClient: function (e) {
            return s.$get('/client/download', {
              params: e
            })
          },
          getRefreshToken: function (e) {
            return s.get('/users/refresh', {  //done
              params: e
            })
          }
        }),

```


### Undocumented Query Syntax
js_name=""
js_md5=""

= means contains
== means absoultely equal

More on `https://fofa.so/help_articles/list?id=8`