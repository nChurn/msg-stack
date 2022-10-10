<div>
    <legend>Insert addresses from outside:</legend>
    <div class="form-group">
        <label for="">Emails parser rules</label>
        <input class="form-control form-control-sm" name="parse_rules" id="parse_rules" type="text" value="[email],[name],[company],[rest]">
        <span class="help-block text-sm">
        	<small><a href="#" data-toggle="collapse" data-target="#parse_rules_info">help</a></small>
        </span>
    </div>
    <div class="form-group collapse" id="parse_rules_info">
        <label for="">
            Common format: [module]delimiter[module], e.g: [name],[email]
            <br>Currenctly supported following modules:
            <ul>
                <li>[mail] - email</li>
                <li>[name] - holder's name and surname</li>
                <li>[company] - company</li>
                <li>[rest] - all the rest</li>
            </ul>
        </label>
    </div>
    <!-- upload file -->
    <div class="form-group">
        <label for="file_list">Add from txt file</label>
        <input class="form-control-file" name="file_list[]" id="file_list" type="file">
    </div>
    <div class="form-group">
	    <!-- Textarea -->
        <label for="">Add from clipboard</label>
	    <textarea class="form-control" id="outer_addresses" name="outer_addresses" rows="6"></textarea>
	</div>

</div>
