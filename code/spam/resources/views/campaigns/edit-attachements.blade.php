<legend>Edit attachements:</legend>
<p>Select attachement to remove it on submit</p>
<table class="table table-bordered table-sm table-striped attachements-table" data-url="{{action('api\CampaignsController@getAttachements', $campaign->id)}}">
    <thead>
        <tr>
            <th>Id</th>
            <th>Name</th>
            <th>Size</th>
            <th>Used</th>
            <th>
                <div class="cool-checkbox">
                    <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                        <input class="form-check-input" id="selectAllAttachements" type="checkbox" name="selected_atts_toggler" value="none">
                        <label class="form-check-label" for="selectAllAttachements">All</label>
                    </div>
                </div>
            </th>
        </tr>
    </thead>
    <tbody>
        @if($campaign->attachements_count > 0)
            @foreach ($campaign->attachements as $att)
            <tr>
                <td>{{$att->id}}</td>
                <td width="100%">{{$att->name}}</td>
                <td>{{$att->size}}</td>
                <td>{{$att->used}}</td>
                <td>
                    <div class="cool-checkbox">
                        <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                            <input class="form-check-input" id="check_acc_{{$att->id}}" type="checkbox" name="selected_atts[]" value="{{$att->id}}">
                            <label class="form-check-label" for="check_acc_{{$att->id}}">&nbsp;</label>
                        </div>
                    </div>
                </td>
            </tr>
            @endforeach
        @else
            <tr><td colspan="10" align="center">No attachements in campaign</td></tr>
        @endif
    </tbody>
</table>
