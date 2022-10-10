<!-- Radoi button  -->
<div class="form-group">
	<div class="col-12">
		<label>When mail account fails to send mails from it's addressbook:</label>
	</div>
	<div class="col-12">
		<div class="abc-radio abc-radio-info form-check form-check-inline">
	        @if(is_null($campaign) || !is_null($campaign) && $campaign->fail_behaviour == 0 )
	    	<input id="avlie_state_fail" value="0" name="fail_behaviour" type="radio" checked="checked">
	    	@else
	    	<input id="avlie_state_fail" value="0" name="fail_behaviour" type="radio">
	    	@endif
	    	<label for="avlie_state_fail">Mark rest addressbook as fail</label>
	    </div>
	    <div class="abc-radio abc-radio-info form-check form-check-inline">
	        @if(!is_null($campaign) && $campaign->fail_behaviour == 1 )
	    	<input id="fail_state_null" value="1" name="fail_behaviour" type="radio" checked="checked">
	    	@else
	    	<input id="fail_state_null" value="1" name="fail_behaviour" type="radio">
	    	@endif
	    	<label for="fail_state_null">Let other accounts try to use this addressbook</label>
	    </div>
	    
	</div>
</div>