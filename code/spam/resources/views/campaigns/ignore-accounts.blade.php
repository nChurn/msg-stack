<!-- Checkbox -->
<div class="form-group">
  <div class="col-md-12">
    <div class="form-check abc-checkbox abc-checkbox-info abc-checkbox-inline form-check-inline">
        @if(!is_null($campaign) && $campaign->ignore_accounts == 1 )
        <input class="form-check-input" id="ignore_accounts" type="checkbox" name="ignore_accounts" value="1" checked="checked" data-checked="1">
        @else
        <input class="form-check-input" id="ignore_accounts" type="checkbox" name="ignore_accounts" value="1" data-checked="0">
        @endif
        <label class="form-check-label" for="ignore_accounts">Skip accounts contact list</label>
    </div>
  </div>
</div>
