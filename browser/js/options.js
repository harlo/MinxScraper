var ctx = chrome.extension.getBackgroundPage();
var conf;

function getConfig() {
	var xhr = new XMLHttpRequest();
	xhr.open("GET", "http://localhost:" + ctx.API_PORT + "/config", true);
	
	xhr.onreadystatechange = function() {
		if(xhr.readyState == 4) {
			var r = JSON.parse(xhr.responseText);
			if(r.result == 200) {
				conf = r.data;
				console.info(conf);
			}
		}
	};
	
	xhr.send();
}

$(document).ready(function() {
	getConfig();
});