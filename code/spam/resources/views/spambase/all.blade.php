@extends('default')
@section('title', 'Base list')
@section('content')
    <div class="row">
        <div class="col-12">
            <h2>
                Bases list
            </h2>
            <a href="{{action('SpamBaseController@new')}}">New base</a>
        </div>
    </div>
    
    <div id="app">
        <spam-base-list-component
        api_url="{{route('api.spam_base.list')}}"
        delete_url="{{route('api.spam_base.delete', 'base_id')}}"
        mass_update_url="{{route('api.spam_base.mass_update')}}"
        edit_url="{{route('spam_base.show', 'base_id')}}"
        export_url="{{route('api.spam_base.export', 'base_id')}}"
        >            
        </spam-base-list-component>
    </div>
@stop