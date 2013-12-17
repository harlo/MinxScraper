var domId = null;
var els = null;
var panelId = null;
var port = null;
var extId = chrome.runtime.id;

var contextMenus = {
	'domutil': {
		id: 'IS_select_elements',
		callback: function() {
			loadDomUtil();
		}
	},
	'labeler' : {
		id: 'IS_label_portion',
		callback: function() {
			port.postMessage({sender: extId, data: "portionSelected"});
		}
	}
};

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
			'width' : 600,
		},
		function(window) {
			panelId = window.id;
		}
	);
}

function initOptions() {
	removeMenuOptions(contextMenus.domutil.id);
	
	chrome.contextMenus.create({
		'title' : "Create MinxScraper from this element...",
		'id' : contextMenus.domutil.id,
		'contexts' : ["selection"],
		'onclick' : contextMenus.domutil.callback
	});
}

function initLabeler() {
	removeMenuOptions(contextMenus.labeler.id);
	
	chrome.contextMenus.create({
		'title' : "Label this portion as...",
		'id' : contextMenus.labeler.id,
		'contexts' : ["selection"],
		'onclick' : contextMenus.labeler.callback
	});
}

function removeMenuOption(id) {
	chrome.contextMenus.remove(id);
}

function removeMenuOptions(id) {
	for(cm in contextMenus) {
		var contextMenu = contextMenus[cm];
		
		if(id != undefined && contextMenu.id == id) {
			continue;
		}
		
		removeMenuOption(contextMenu.id);
	}
}

function packageManifest() {
	// TODO!
}

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
	if(message.sender == "domUtils") {
		initLabeler();
		loadScraperPanel(message.data);
	}
	
	console.info("background received");
	console.info(message);
	console.info(sender);		
});

chrome.runtime.onConnect.addListener(function(p) {
	port = p;
	
	port.onMessage.addListener(function(message) {
		console.info("background received");
		console.info(message);
		
		if(message.sender == "uiPanel") {
			if(message.data == "portionsPrepared") {
				console.info(els);
				chrome.windows.remove(panelId);
				packageManifest();
			}
		}
	});	
});

chrome.browserAction.onClicked.addListener(function(tab) {
	chrome.tabs.executeScript(tab.id, {file: "/js/dom_utils.js"});	
	initOptions();
});

chrome.windows.onRemoved.addListener(function(windowId) {
	initOptions();
});
