var ctx = chrome.extension.getBackgroundPage();

function sendAction() {
	var action = $(this).attr('rel');
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "http://localhost:" + ctx.API_PORT + "/engine/" + action, true);
	xhr.onreadystatechange = function() {
		if(xhr.readyState == 4) {
			console.info(JSON.parse(xhr.responseText));
		}
	};
	
	xhr.send();
}

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
				
				html = $("#IS_sync_holder").html();
				$("#IS_sync_holder").html(
					Mustache.to_html(html, {sync : r.data.sync}));
				
				
				initUI();
				console.info(r.data.scrapers[0].config);
			}	
		}
	};
	
	xhr.send();
}

function activateOption() {
	var url, data;
	var parent = $(this).parent();
	var activate = parent.attr('rel') == undefined ? false : (parent.attr('rel') === "true");
		
	if(parent.hasClass('IS_activate_sync')) {
		url = "http://localhost:" + ctx.API_PORT + "/engine/sync";
		data = {
			database : parent.attr('id').replace('IS_status_toggle_',""),
			is_active : !activate
		}
	} else if(parent.hasClass('IS_activate_schema')) {
		url = "http://localhost:" + ctx.API_PORT + "/config";
		data = {
			id : parent.attr('id').replace('IS_is_active_',""),
			is_active : !activate
		};
	}
	
	if(url != undefined && data != undefined) {
		var xhr = new XMLHttpRequest();
		xhr.open("POST", url, true);
		xhr.onreadystatechange = function() {
			var r = JSON.parse(xhr.responseText);
			if(r.result == 200) {
				parent.attr('rel', !activate);
				updateActivated(parent);
			}
		};
	
		xhr.send(JSON.stringify(data));
	}
	
	
}

function updateActivated(el) {
	var child = $(el).children('.IS_status_toggle_off')[0];
	
		
	if($(el).attr('rel') != undefined) {
		if($(el).attr('rel') == "true") {
			child = $(el).children('.IS_status_toggle_on')[0];
		}
	}
	
	$.each($(el).children('a'), function(idx, item) {
		if(item != child) {
			$(item).removeClass('IS_status_active');
		} else {
			$(item).addClass('IS_status_active');	
		}
	});
}

function initUI() {
	for(var e=0, el;el=document.getElementsByClassName('IS_toggleElement')[e]; e++) {
		el.addEventListener('click', toggleElement);
	}
	
	for(var e=0, el;el=document.getElementsByClassName('IS_save_schema')[e]; e++) {
		el.addEventListener('click', saveSchema);
	}
	
	for(var e=0, el;el=document.getElementsByClassName('IS_save_sync')[e]; e++) {
		el.addEventListener('click', saveSync);
	}
	
	for(var e=0, el;el=document.getElementsByClassName('IS_master_ctrl')[e]; e++) {
		el.addEventListener('click', sendAction);
	}
	
	for(var e=0, el;el=document.getElementsByClassName('IS_remove_opt')[e]; e++) {
		el.addEventListener('click', removeEl);
	}
	
	for(var e=0, el;el=document.getElementsByClassName('IS_delete_schema')[e]; e++) {
		el.addEventListener('click', deleteSchema);
	}
	
	for(var e=0, el;el=document.getElementsByClassName('IS_status_toggle_on')[e]; e++) {
		el.addEventListener('click', activateOption);
	}
	
	for(var e=0, el;el=document.getElementsByClassName('IS_status_toggle_off')[e]; e++) {
		el.addEventListener('click', activateOption);
	}
	
	for(var e=0, el;el=$('.IS_status_toggle')[e]; e++) {
		updateActivated(el);
		
	}
}

function removeEl() {
	$("#" + $(this).attr('rel')).remove();
}

function saveSync() {
	database = $(this).attr('rel');
	
	var sync = {
		database : database
	};
	
	$.each($("#IS_sync_vars_" + database), function(idx, item) {
		$.each($($(item).children('li')).children('p'), function(idx_, item_) {
			var key = item_.innerText.replace(" ","");
			var val = $($(item_).find('input')[0]).val();
			
			sync[key] = val;
		});
	});
	
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "http://localhost:" + ctx.API_PORT + "/engine/sync", true);
	xhr.send(JSON.stringify(sync));

}

function deleteSchema() {
	id = $(this).attr('rel');
	console.info("deleting " + id);
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