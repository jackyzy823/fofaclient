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
res , max_count = client.search_all("testquery",iterable = True)
max_count = client.search_count("testquery", full=True)
stat = client.stats("testquery")
me = client.me()
rules = client.rules_all("testrule")
```



### TODO
1. add sleep argments for `_all` function to avoid possible 502
2. can recover when break in middle
3. type * id maybe unique key