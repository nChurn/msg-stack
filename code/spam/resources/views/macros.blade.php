@extends('default')
@section('title', 'Macros editor')
@section('content')
	<ul class="nav nav-tabs" id="myTab" role="tablist">
        <li class="nav-item">
            <a class="nav-link active" id="manage-tab" data-toggle="tab" href="#manage" role="tab" aria-controls="manage" aria-selected="true">Manage</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" id="add_new-tab" data-toggle="tab" href="#add_new" role="tab" aria-controls="add_new" aria-selected="false">Add new</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" id="macro_help-tab" data-toggle="tab" href="#macro_help" role="tab" aria-controls="macro_help" aria-selected="false">Help</a>
        </li>
    </ul>
    <div id="app">
	    <div class="tab-content mt-2" id="myTabContent">
	        <div class="tab-pane fade" id="add_new" role="tabpanel" aria-labelledby="add_new-tab">
	        	<macros-create-component
                    api_url="{{route('api.macros.store')}}"
	        	></macros-create-component>
	        </div>
	        <div class="tab-pane fade show active" id="manage" role="tabpanel" aria-labelledby="manage-tab">
	            <macros-list-component
                    api_url="{{route('api.macros.index')}}"
                    remove_url="{{route('api.macros.remove')}}"
	            ></macros-list-component>
	        </div>
	        <div class="tab-pane fade" id="macro_help" role="tabpanel" aria-labelledby="macro_help-tab">
                @include('includes.supported-macroses')
            </div>
	    </div>
    </div>
@stop
