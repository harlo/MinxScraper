var domId = null;
var manifest = {
	elements: [],
	config: {},
};
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
		manifest.url = tabs[0].url;
		chrome.tabs.sendMessage(domId, "initDomUtil");
	});
}

function loadScraperPanel() {	
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
	var post = { manifest : manifest }
	console.info(JSON.stringify(post));
	console.info(JSON.stringify(post).length);
	
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "http://localhost:" + API_PORT, true);
	xhr.setRequestHeader("Content-type", "application/json");
	xhr.setRequestHeader("X-MINX-KEY", extId);
	
	xhr.onreadystatechange = function() {
		if(xhr.readyState == 4) {
			console.info(JSON.parse(xhr.responseText));
		}
	};
	xhr.send(JSON.stringify(post));
}

function initUiPanelData() {
	return null;
}

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
	if(message.sender == "domUtils") {
		if(message.data == "setElements") {
			initLabeler();
			manifest.elements = message.elements;
			loadScraperPanel();
		}
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
			if(message.data == "schemaPrepared") {
				console.info(manifest.elements);
				chrome.windows.remove(panelId);
				packageManifest();
			}
			
			if(message.data == "connectionEstablished") {
				port.postMessage({
					sender: extId,
					data: "connectionEstablished",
					initData: initUiPanelData()
				});
			}
		}
	});	
});

chrome.browserAction.onClicked.addListener(function(tab) {
	chrome.tabs.executeScript(tab.id, {file: "/js/dom_utils.js"});	
	initOptions();
	console.info(API_PORT);
});

chrome.windows.onRemoved.addListener(function(windowId) {
	initOptions();
});
