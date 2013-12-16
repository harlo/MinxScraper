var domId = null;
var panelId = null;
var els = null;

function loadDomUtil() {
	chrome.tabs.query({currentWindow: true, active: true}, function(tabs) {
		domId = tabs[0].id;
		chrome.tabs.sendMessage(domId, "initDomUtil");
	});
}

function loadScraperPanel(sel) {
	els = sel;
	
	chrome.windows.create(
		{
			'url' : '/layout/minx_browser.html',
			'type' : 'panel',
			'width' : 600
		},
		function(window) {
			panelId = window.id;
		}
	);
}

function loadScraperNavigation(e) {
	console.info(e);
}

function initOptions() {
	chrome.contextMenus.create({
		'title' : "Create MinxScraper from this element...",
		'id' : 'IS_select_elements',
		'contexts' : ["selection"],
		'onclick' : function() {
			loadDomUtil();
		}
	});
}

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
	if(message.sender == "domUtils") {
		loadScraperPanel(message.data);
	}
	
	console.info(message);
	console.info(sender);		
});

chrome.browserAction.onClicked.addListener(function(tab) {
	chrome.tabs.executeScript(tab.id, {file: "/js/dom_utils.js"});	
	initOptions();
});
