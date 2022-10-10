<!-- Checkbox -->
<div class="form-group">
  <div class="col-md-12">
    <div class="form-check abc-checkbox abc-checkbox-info abc-checkbox-inline form-check-inline">
        @if(!is_null($campaign) && $campaign->has_attaches == 0 )
        <input class="form-check-input" id="has_attaches" type="checkbox" name="has_attaches" value="1" data-checked="0">
        @else
        <input class="form-check-input" id="has_attaches" type="checkbox" name="has_attaches" value="1"  checked="checked" data-checked="1">
        @endif
        <label class="form-check-label" for="has_attaches">Use attachements</label>
    </div>
  </div>
</div>
