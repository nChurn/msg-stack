<div class="form-group filter-groups">
    <label for="">Use filter groups (email addresses will be ignored if matches any filter in selected group)</label>

    @if(empty($radio) || $radio == false)
    <div class="form-check abc-checkbox abc-checkbox-info form-check">
        <input class="form-check-input check-all" id="selectAllGroups" type="checkbox">
        <label class="form-check-label" for="selectAllGroups">All</label>
    </div>
    @endif
    
    <div class="row">
    @foreach( $filters as $filter )
    <div class="col-4">
    @if(empty($radio) || $radio == false)
        <div class="form-check abc-checkbox abc-checkbox-info form-check">
            @if(!empty($selected) && $selected->contains($filter->group))
            <input class="form-check-input check-group" name="selected_filters[]" id="select_{{$filter->group}}" type="checkbox" value="{{$filter->group}}" checked="checked" data-checked="1">
            @else
            <input class="form-check-input check-group" name="selected_filters[]" id="select_{{$filter->group}}" type="checkbox" value="{{$filter->group}}" data-checked="0">
            @endif
            <label class="form-check-label" for="select_{{$filter->group}}">{{$filter->group}}</label>
        </div>
        @elseif(!empty($radio) && $radio == true)
        <div class="form-check abc-radio abc-radio-info form-check">
            @if(!empty($selected) && $selected->contains($filter->group))
            <input class="form-check-input check-group" name="selected_filters[]" id="select_{{$filter->group}}" type="radio" value="{{$filter->group}}" checked="checked" data-checked="1">
            @else
            <input class="form-check-input check-group" name="selected_filters[]" id="select_{{$filter->group}}" type="radio" value="{{$filter->group}}" data-checked="0">
            @endif
            <label class="form-check-label" for="select_{{$filter->group}}">{{$filter->group}}</label>
        </div>
    @endif
    </div>
    @endforeach
    </div>

</div>