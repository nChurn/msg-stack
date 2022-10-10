<!-- Checkbox -->
<div class="form-group">
    <div class="col-6">
        <div class="form-check abc-checkbox abc-checkbox-info abc-checkbox-inline form-check-inline">
            @if(!is_null($campaign) && $campaign->is_html == 1 )
                <input class="form-check-input" id="is_html" type="checkbox" name="is_html" value="1" data-checked="1" />
            @else
                <input class="form-check-input" id="is_html" type="checkbox" name="is_html" value="1" data-checked="0" />
            @endif
            <label class="form-check-label" for="is_html">Body as HTML</label>
        </div>
    </div>
    <div class="col-2 preview-html" id="previeButton" >
        <button
            class="btn btn-info btn-sm"
            data-macro-from-name="{{$macros_data['from_name']}}"
            data-macro-to-name="{{$macros_data['to_name']}}"
            data-macro-from-email="{{$macros_data['from_email']}}"
            data-macro-to-email="{{$macros_data['to_email']}}"

            data-macro-tpls="{{json_encode($macros_templates)}}"
            {{-- @foreach ($macros_templates as $tpl) --}}
                {{-- data-macro-templates --}}
            {{-- @endforeach --}}
            >Preview</button>
    </div>
</div>
