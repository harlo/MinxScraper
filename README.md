# MinxScraper

******
Setup

After cloning, run

	git submodule update --init --recursive

Install the submodules tornado, requests, and m2x

	cd library/[package]
	sudo python setup.py install

Install dependencies (not included in packaging):

	sudo pip install beautifulsoup4

(or see http://www.crummy.com/software/BeautifulSoup/ if you have trouble)

******
Chrome Extension

Enable Developer mode in chrome://extensions.
Click the "Load unpacked extension" button, navigate to 
	
	/browser 

and click OK.

******
Config

Please edit the config files at:

	/conf.json.example
	/conf.py.example

And copy them as:

	/conf.json
	/conf.py

******
Start

First:

	cd MinxScraper
	python api.py

Then use the chrome extension.  See this video for help: http://www.youtube.com/watch?v=3zVlcJeAssk

Stop

	[ctrl+c]