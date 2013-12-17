var extId = chrome.runtime.id;
var ctx = chrome.extension.getBackgroundPage();
var idx = 0;
var selectionPopup = null;

function log(msg) {
	ctx.console.info(msg);
}

function toggleElement(el) {
	if($(el).css('display') == "block") {
		$(el).css('display','none');
		return false;
	} else {
		$(el).css('display','block');
		return true;
	}
}

function initSelections(els) {
	$.each(els, function(idx, item) {
		$("#IS_selection_holder").append(
			$(document.createElement('li'))
				.append(item.innerHtml)
		);
	});
}

function setLabel() {	
	var applyLabel = $(".IS_template_" + selectionPopup.attr('rel'));
	applyLabel.attr('id',"IS_start_" + $(selectionPopup.find('input')[0]).val());
	toggleElement(selectionPopup);
}

function parseSelectedPortion() {
	var selection = window.getSelection();
	var range = selection.getRangeAt(0);
	var html = selection.anchorNode.parentElement;
	
	var s = html.innerHTML.substring(0, range.startOffset);
	var e = html.innerHTML.substring(range.endOffset, html.length);
	var t = selection.toString();
	
	$(html).html(s + '<span class="IS_label IS_template_' + idx + '">' + t + "</span>" + e);
	
	var label = $(".IS_template_" + idx);
	
	toggleElement(selectionPopup);
	$(selectionPopup.find('input')[0]).val('');
	selectionPopup.attr('rel', idx);
	selectionPopup.css({
		'top' : label.position().top - (selectionPopup.height() + 10),
		'left' : label.position().left
	});
	
	idx++;
}

port = chrome.runtime.connect(extId, {name: "uiPanel"});
port.onMessage.addListener(function(message) {
	log("forground received");
	log(message);
	
	if(message.sender == extId) {
		if(message.data == "portionSelected") {
			parseSelectedPortion();
		}
		
		if(message.data == "elementsSelected") {
			initSelections(message.elements);
		}
	}
});

$(document).ready(function() {
	selectionPopup = $("#IS_selection_popup");
	$("#IS_label_setter").on('click', setLabel);
	initSelections(ctx.els);
});