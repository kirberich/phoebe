$(function(){
	$(".js-presence").change(function(e){
		var $this = $(this);
		var checked = $this.is(":checked");
		var api_key = $("#api-key").val()

		$.post(
			$this.data("url"), 
			{
				'device_id': $this.data("device"), 
				'is_present': checked, 
				'api_key': api_key
			}
		)
	});
});