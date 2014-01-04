var extId = chrome.runtime.id;
var ctx = chrome.extension.getBackgroundPage();
var idx = 0;
var selectionPopup = null;
var iteratorPopup = null;

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
		log(item);
		$("#IS_selection_holder").append(
			$(document.createElement('li'))
				.append(item.innerHtml)
		);
	});
}

function initConfig() {
	toggleElement($("#IS_step_portions"));
	toggleElement($("#IS_step_config"));
	
	port.postMessage({
		sender: "uiPanel",
		data: "initConfiger"
	});
	
	$("#IS_config_iterate_url").val(ctx.manifest.url);
	$("#IS_config_header").val(parseHeadersAsText(ctx.manifest.headers));
}

function setLabel() {	
	var applyLabel = $(".IS_template_" + selectionPopup.attr('rel'));
	applyLabel.attr('id',"IS_start_" + $(selectionPopup.find('input')[0]).val());
	toggleElement(selectionPopup);
}

function setIterator() {
	var operator = null;
	var value = null;
	var replacement = iteratorPopup.attr('rel');
	
	if(replacement == undefined || replacement == null) {
		return;
	}
	
	$.each(iteratorPopup.find('input,select'), function(i, item) {		
		switch($(item).prop('tagName').toLowerCase()) {
		case "input":
			if($(item).val() != 0 && $(item).val() != '') {
				value = $(item).val();
			}
			break;
		case "select":
			operator = $($(item).children('option:selected')[0]).val();
			break;
		}
	});
	
	if(value != null && operator != null) {
		$("#IS_config_iterate_url").val(
			$("#IS_config_iterate_url").val().replace(
				replacement, 
				("[%" + operator + "]" + value + "[/%" + operator + "]")));
	}
	
	log(value);
	log(operator);
	log(replacement);
	
	toggleElement(iteratorPopup);
}

function parseHeadersAsText(h) {
	var hString = "";
	$.each(h, function(i, item) {
		hString += (item.name + ": " + item.value + "\n");
	});
	return hString;
}

function insertHtmlAfterSelection(html) {
    var sel, range, expandedSelRange, node;
	sel = window.getSelection();
	if (sel.getRangeAt && sel.rangeCount) {
		range = window.getSelection().getRangeAt(0);
		
		expandedSelRange = range.cloneRange();
		range.collapse(false);

		// Range.createContextualFragment() would be useful here but is
		// non-standard and not supported in all browsers (IE9, for one)
		var el = document.createElement("div");
		el.innerHTML = html;
		var frag = document.createDocumentFragment(), node, lastNode;
		while ( (node = el.firstChild) ) {
			lastNode = frag.appendChild(node);
		}
		range.insertNode(frag);

		// Preserve the selection
		if (lastNode) {
			expandedSelRange.setEndAfter(lastNode);
			sel.removeAllRanges();
			sel.addRange(expandedSelRange);			
		}
	}
}

function iterateSelectedPortion() {
	var selection = window.getSelection();	
	var html = selection.anchorNode.firstElementChild;
	var t = selection.toString();
	
	if(html.id != "IS_config_iterate_url") {
		return;
	}
	
	iteratorPopup.attr('rel', t);	
	toggleElement(iteratorPopup);
}

function fuzzSelectedPortion() {
	var selection = window.getSelection();	
	var range = selection.getRangeAt(0);
	var html = selection.anchorNode.parentElement;
	var t = selection.toString();
	
	var replacement = '<span class="IS_fuzzed">' + t + '</span>';
	insertHtmlAfterSelection(replacement);
	
	var s = html.innerHTML.substring(0, (html.innerHTML.indexOf(replacement) - t.length));	
	var r = html.innerHTML.substring(s.length, (s.length + t.length));
	var e = html.innerHTML.substring((s.length + r.length), html.length);

	$(html).html(s + e);
}

function parseSelectedPortion() {
	var selection = window.getSelection();	
	var range = selection.getRangeAt(0);
	var html = selection.anchorNode.parentElement;
	var t = selection.toString();
	
	var replacement = '<span class="IS_label IS_template_' + idx + '">' + t + '</span>';
	insertHtmlAfterSelection(replacement);
	
	var s = html.innerHTML.substring(0, (html.innerHTML.indexOf(replacement) - t.length));	
	var r = html.innerHTML.substring(s.length, (s.length + t.length));
	var e = html.innerHTML.substring((s.length + r.length), html.length);

	$(html).html(s + e);
	
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

function finishPortions() {
	$.ajax({
		url: "/layout/selection_view.html",
		dataType: "html",
		success: function(html) {			
			$.each($("#IS_selection_holder").children('li'), function(i, item) {				
				var template = $(html).clone();
				$(template).append($(item).html());
				
				var templateHolder = $(document.createElement('div'));
				$(templateHolder).append($(template));
				
				ctx.manifest.elements[i].innerHtml = $(templateHolder).html();				
			});
			
			log(ctx.manifest.elements);
			initConfig();
		}
	});
}

function finishSchema() {
	$.each($(".IS_config_form").find('input,select,textarea'), function(i, item) {
		log($(item));
		
		var value = null;
		var tag = $(item).attr('id');
		
		switch($(item).prop('tagName').toLowerCase()) {
		case "input":
			if($(item).val() != 0 && $(item).val() != '') {
				value = $(item).val();
			}
			break;
		case "select":
			value = $($(item).children('option:selected')[0]).val();
			break;
		case "textarea":
			if($(item).val().length > 1) {
				value = $(item).val();
			}
			break;
		}
		
		if(tag != null && value != null) {
			ctx.manifest.config[tag] = value;
		}
	});
	
	log(ctx.manifest.config);
	
	port.postMessage({
		sender: "uiPanel",
		data: "schemaPrepared"
	});
}

function loadAsset(el, val) {
	log($(el).prop('tagName'));
}

port = chrome.runtime.connect(extId, {name: "uiPanel"});
port.onMessage.addListener(function(message) {
	log("forground received");
	log(message);
	
	if(message.sender == extId) {
		if(message.data == "portionSelected") {
			parseSelectedPortion();
		}
		
		if(message.data == "fuzzSelected") {
			fuzzSelectedPortion();
		}
		
		if(message.data == "iterateOverURL") {
			iterateSelectedPortion();
		}
		
		if(message.data == "loadAsset") {
			loadAsset($("#" + message.asset.id), message.asset.value);
		}
		
		if(message.data == "connectionEstablished") {
			if(message.initData == null) {
				initSelections(ctx.manifest.elements);
			} else {
				// load all this data
			}
		}
	}
});

$(document).ready(function() {
	selectionPopup = $("#IS_selection_popup");
	iteratorPopup = $("#IS_iterator_popup");
	
	$("#IS_label_setter").on('click', setLabel);
	$("#IS_iterator_setter").on('click', setIterator);
	
	$("#IS_submit_portions").on('click', finishPortions);
	$("#IS_submit_config").on('click', finishSchema);
		
	port.postMessage({
		sender: "uiPanel",
		data: "connectionEstablished"
	});
});