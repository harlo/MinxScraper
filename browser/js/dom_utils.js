var extId = chrome.runtime.id;

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
	if(sender.id == extId) {
		if(message.data == "initDomUtil") {
			getSelectedNodes();
		}		
	}
});

function getPathToBody(el, nodeAsBody) {
	var pathToBody = [];
	var bodyRoot = null;
	if(nodeAsBody == undefined || nodeAsBody == null) {
		nodeAsBody = "body";
	}
	
	bodyRoot = document.getElementsByTagName(nodeAsBody)[0];	
	var parent = el.parentNode;
	var sibling = el;
	
	do {
		var siblingPath = 0;
		for(var e=0, el; el=parent.childNodes[e]; e++) {
			if(el == sibling) {
				pathToBody.push(siblingPath);
				break;
			}
		
			siblingPath++;
		}
	
		sibling = parent;
		parent = parent.parentNode;
		
	} while(parent != bodyRoot);
	
	for(var e=0, el; el=bodyRoot.childNodes[e]; e++) {
		if(el == sibling) {
			pathToBody.push(e);
		}
	}
	
	return pathToBody;
}

function getSelectedNodes() {
	var els = [];
	
	var selection = window.getSelection();
	var range = selection.getRangeAt(0);
	var rangeEls = range.commonAncestorContainer.getElementsByTagName("*");
	
	for(var e=0, el; el=rangeEls[e]; e++) {	
		if(
			selection.containsNode(el, true) && 
			el.parentNode == range.commonAncestorContainer
		) {
			var elClone = document.createElement('div');
			elClone.appendChild(el.cloneNode(true));
			
			els.push({
				innerHtml: elClone.innerHTML,
				pathToBody: getPathToBody(el)
			});
		}
	}
	
	chrome.runtime.sendMessage(null, {
		sender: "domUtils",
		data: "setElements",
		elements: els,
		rootElement: "body"
	});
}