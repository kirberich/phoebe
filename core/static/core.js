$(function(){
	$(".js-api-toggle").change(function(e){
		var $this = $(this);
		var checked = $this.is(":checked");
		var api_key = $("#api-key").val();

		var data = {
			'api_key': api_key,
			'state': checked
		};

		if($this.data("extra") !== undefined) {
			var extra_parts = $this.data("extra").split("&");
			for(var i=0; i<extra_parts.length; i++) {
				var split_part = extra_parts[i].split(":");
				data[split_part[0]] = split_part[1];
			}
		}

		$.post($this.data("url"), data);
	});
});