var extId = chrome.runtime.id;
var ctx = chrome.extension.getBackgroundPage();

function log(msg) {
	ctx.console.info(msg);
}

$(document).ready(function() {
	$.each(ctx.els, function(idx, item) {
		$("#IS_selection_holder").append(
			$(document.createElement('li'))
				.append(item.innerHtml)
		);
	});	
});