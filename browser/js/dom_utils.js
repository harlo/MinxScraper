var extId = chrome.runtime.id;

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
	if(sender.id == extId) {
		if(message.data == "initDomUtil") {
			getSelectedNodes();
		}
		
		if(message.data == "getPathToXMLRoot") {
			getPathToXMLRoot(message.elements);
		}	
	}
	
	console.info("tab received");
	console.info(message);
	console.info(sender);
});

function log(msg) {
	console.info(msg);
}

function getDomElementFromPath(pathToClone) {
	var path = pathToClone.slice(0).reverse();
	var parent = document.getElementsByTagName("body")[0];
	var domEl = null;
	
	for(var p=0; p<path.length; p++) {
		domEl = parent.childNodes[path[p]];
		parent = domEl;
	}
	
	return domEl;
}

function getPathToXMLRoot(els) {
	log("FIXING XML");
	
	var rssTag = "webkit-html-tag";
	pathToXMLRoot = [];
		
	// the first and last elements are tag nodes, usually.
	// the middle sibling contains the info we want
	for(var e=0, el; el = els[e]; e++) {
		if(el.innerHtml) {
			var holder = document.createElement('div');
			holder.innerHTML = el.innerHtml;
			
			if(holder.getElementsByClassName("IS_label").length == 0) {
				continue;
			}
			
			for(var i=0, el_; el_ = holder.getElementsByClassName("IS_label")[i]; i++) {
				log("ANALYZING NEW ELEMENT");
				
				var xmlPath = {
					tags : [],
					domIndex : e
				};
				
				var breakAway = getDomElementFromPath(el.pathToBody);
				
				// find the tag it belongs to, and its child position
				var parent = el_.parentNode;
				//log(el_);
				//log("FIRST PARENT:");
				//log(parent);
				
				xmlPath.XMLContent = parent.innerText;
				// is parent node class.text?
				if(parent.className == "text") {
					// is parent's sibling "webkit-html-tag"?
					for(var j=0, el__; el__ = parent.parentNode.childNodes[j]; j++) {
						if(el__.className == rssTag && xmlPath.tag == null) {
							log("first tag found!");
							xmlPath.tags.push(el__.innerText
								.replace("<","")
								.replace("/","")
								.replace(">",""));
							break;
						}
					}
				} else {
					log("parent name is NOT text.  what to do?");
				}
				
				if(xmlPath.tags.length == 0) {
					log("first tag still not found!");
					// if not, is parent node in node calss collapsible-content?
					if(parent.parentNode.className == "collapsible-content") {
						//log("PARENT:");
						//log(parent);
						
						for(var j=0, el__; el__ = parent.parentNode.parentNode.childNodes[j]; j++) {
							//log("EL__:");
							//log(el__);
							inspect = el__;
							
							if(el__.className == "line" && xmlPath.tag == null) {
								var tags = el__.getElementsByClassName(rssTag);
								if(tags.length > 0) {
									log("first tag found!");
									xmlPath.tags.push(tags[0].innerText
										.replace("<","")
										.replace("/","")
										.replace(">",""));
									break;
								}
								
							}
							
							
						}
						
						if(xmlPath.tags.length == 0) {
							//log("PREVIOUS SIBLING:");
							//log(breakAway.previousSibling);
							log("first tag STILL not found!");
							var s = breakAway.previousSibling
								.getElementsByClassName(rssTag);
							
							if(s.length > 0) {
								xmlPath.tags.push(s[0].innerText
									.replace("<","")
									.replace("/","")
									.replace(">",""));
							}
						}
					}
				}
								
				if(xmlPath.tags.length > 0) {
					// walk the tag up the document tree all the way to rss
					
					var currentTag = null;
					var rssTagFound = false;
					
					do {
						//log("BREAK AWAY:");
						//log(breakAway);
						
						var expanded = null;
						
						if(breakAway.parentNode.className=="expanded") {
							// should be the next expanded up
							expanded = breakAway.parentNode.parentNode.parentNode;
						} else if(breakAway.parentNode.className=="collapsible-content") {
							expanded = breakAway.parentNode;
						}
						
						if(expanded != null && expanded.previousSibling != null) {
							//log("EXPANDED:");
							//log(expanded);
							
							//log("PREVIOUS SIBLING:");
							//log(expanded.previousSibling);
							var s = expanded.previousSibling
								.getElementsByClassName(rssTag);
							
							if(s.length > 0) {
								currentTag = s[0].innerText
									.replace("<","")
									.replace("/","")
									.replace(">","");

								//log("CURRENT TAG:");
								//log(currentTag);
								
								var isRssTag = currentTag.match(/^rss/g);
								log(isRssTag);
								
								if(isRssTag != null && isRssTag.length > 0) {
									rssTagFound = true;
								}
								
								xmlPath.tags.push(rssTagFound ? "rss" : currentTag);
								breakAway = expanded;								
							} else {
								log("ALSO BROKEN");
								break;
							}				
						} else {
							log("BROKEN");
							break;
						}
					
					} while(!rssTagFound);
					
					log(xmlPath);
					// contentAsXML = whatever is at path
					pathToXMLRoot.push(xmlPath);
				}
			}
		}
	}
	
	
	chrome.runtime.sendMessage(null, {
		sender: "domUtils",
		data: "schemaPreparedWithXML",
		pathToXMLRoot: pathToXMLRoot
	});
}

function getPathToBody(el, nodeAsBody) {	
	var pathToBody = [];
	var bodyRoot = nodeAsBody;
	
	if(nodeAsBody == undefined || nodeAsBody == null) {
		bodyRoot = document.getElementsByTagName("body")[0];
	}
	
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
			
			var m = {
				innerHtml: elClone.innerHTML,
				pathToBody: getPathToBody(el)
			};			
			els.push(m);
		}
	}
	
	chrome.runtime.sendMessage(null, {
		sender: "domUtils",
		data: "setElements",
		elements: els,
		rootElement: "body"
	});
}