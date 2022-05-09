from setuptools import setup , find_packages
import pathlib


here = pathlib.Path(__file__).parent.resolve()


long_description = ( here / 'README.md' ).read_text(encoding= 'utf-8')

setup(
	name='fofaclient',
	version='0.1.1',
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
                # from google-coral's own repo: https://google-coral.github.io/py-repo/
		'tflite_runtime~=2.5;python_version<"3.10"',
		'tensorflow~=2.5;python_version>="3.10"',
		'importlib-resources>=1.0;python_version<"3.9"'
	],
	# no more work for pip 19+ https://pip.pypa.io/en/stable/news/#v19-0
	# https://stackoverflow.com/a/54793503
	dependency_links=[
		"https://google-coral.github.io/py-repo/"
	],
	extras_require={
		"full": ["tensorflow~=2.5"]
	},
	packages = find_packages(),
	package_data = {
		"fofaclient": ["model/rucaptcha.tflite"],
	},
)
