# MinxScraper

******
Setup

After cloning, run

	git submodule update --init --recursive

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

	cd MinxScraper
	python api.py

Stop

	[ctrl+c]