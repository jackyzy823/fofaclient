from setuptools import setup , find_packages
import pathlib


here = pathlib.Path(__file__).parent.resolve()


long_description = ( here / 'README.md' ).read_text(encoding= 'utf-8')

setup(
	name='fofaclient',
	version='0.1.2',
	description="An unoffical fofa client",
	long_description=long_description,
	long_description_content_type = "text/markdown",
	## TODOs
	#url="https://github.com/"
	#author
	#author_email
	#keywords
	classifiers=[
		'Development Status :: 3 - Alpha',
		# .....

	],
	python_requires=">=3,<4",
	install_requires=[
		"requests[socks,security]~=2.25",
        'pycryptodome',
		"Pillow~=8.2",
		'tflite_runtime~=2.5;python_version<"3.10"',
		'tensorflow~=2.5;python_version>="3.10"',
		'importlib-resources>=1.0;python_version<"3.9"'
	],
	extras_require={
		"full": ["tensorflow~=2.5"]
	},
	packages = find_packages(),
	package_data = {
		"fofaclient": ["model/rucaptcha.tflite"],
	},
)
