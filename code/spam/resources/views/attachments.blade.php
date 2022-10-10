@extends('default')
@section('title', 'Attachments')
@section('content')
    <div id="app">
		<ul class="nav nav-tabs mb-3" id="myTab" role="tablist">
	        <li class="nav-item">
	            <a class="nav-link" id="add_new-tab" data-toggle="tab" href="#add_new" role="tab" aria-controls="add_new" aria-selected="false">Add new</a>
	        </li>
	        <li class="nav-item">
	            <a class="nav-link active" id="manage-tab" data-toggle="tab" href="#manage" role="tab" aria-controls="manage" aria-selected="true">Manage</a>
	        </li>
	    </ul>
	    <div class="tab-content" id="myTabContent">
			<div class="tab-pane fade" id="add_new" role="tabpanel" aria-labelledby="add_new-tab">
				<attachment-upload-component
					api_url = "{{route('api.attachments.index')}}"
					groups_url = "{{route('api.attachments.groups')}}"
	            	create_url = "{{route('api.attachments.create')}}"
				></attachment-upload-component>
			</div>
			<div class="tab-pane fade show active" id="manage" role="tabpanel" aria-labelledby="manage-tab">
	            <attachment-list-component
	            	api_url = "{{route('api.attachments.index')}}"
	            	create_url = "{{route('api.attachments.create')}}"
	            	update_url = "{{route('api.attachments.update', 'att_id')}}"
	            	delete_url = "{{route('api.attachments.delete')}}"
	            ></attachment-list-component>
	        </div>
	    </div>
	</div>
@stop
