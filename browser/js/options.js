var ctx = chrome.extension.getBackgroundPage();

function getConfig() {
	var xhr = new XMLHttpRequest();
	xhr.open("GET", "http://localhost:" + ctx.API_PORT + "/config", true);
	
	xhr.onreadystatechange = function() {
		if(xhr.readyState == 4) {
			var r = JSON.parse(xhr.responseText);
			if(r.result == 200) {
				var html = $("#IS_scrapers_holder").html();
				$("#IS_scrapers_holder").html(
					Mustache.to_html(html, {scrapers : r.data.scrapers}));
				
				initUI();
				console.info(r.data.scrapers[0].config);
			}
		}
	};
	
	xhr.send();
}

function initUI() {
	for(var e=0, el;el=document.getElementsByClassName('IS_toggleElement')[e]; e++) {
		el.addEventListener('click', toggleElement);
	}
	
	for(var e=0, el;el=document.getElementsByClassName('IS_save_schema')[e]; e++) {
		el.addEventListener('click', saveSchema);
	}
}

function saveSchema() {
	id = $(this).attr('rel');
	
	var schema = {
		id : id,
		config : {
			IS_config_headers : "",
			IS_config_period : $("#IS_config_period_" + id).val(),
			IS_config_period_mult : $("#IS_config_period_mult_" + id).val()
		},
		headers: [],
		method: $("#IS_method_" + id).val().toUpperCase()
	};
	
	$.each($("#IS_headers_" + id).find('input'), function(idx, item) {
		var header = {
			name : $(item).attr('name'),
			value : $(item).val()
		};
		schema.headers.push(header);
		schema.config.IS_config_headers += (header.name + ": " + header.value + ";");
	});
	
	schema.is_active = $("#IS_is_active_" + id).attr('rel');	
	console.info(schema);
		
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "http://localhost:" + ctx.API_PORT + "/config", true);
	xhr.setRequestHeader("Content-type", "application/json");
	
	xhr.onreadystatechange = function() {
		if(xhr.readyState == 4) {
			console.info(JSON.parse(xhr.responseText));
		}
	};
	
	xhr.send(JSON.stringify(schema));
	
}

function toggleElement() {
	el = $(this).attr('rel');

	if($(el).css('display') == 'block') {
		$(el).css('display', 'none');
		return false;
	} else {
		$(el).css('display', 'block');
		return true;
	}
}

document.addEventListener('DOMContentLoaded', getConfig);