<!doctype html>
<html>
<head>
    @include('includes.header')
    <link href="{{ asset('css/app.css') }}" rel="stylesheet" type="text/css" />
</head>
<body>

@include('includes.navbar')
@include('includes.sidebar')
<div class="main-content">
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <div class="col-12 alert-container">
                    
                </div>
            </div>
        </div>
        @yield('content')
    </div>
</div>
    
    <!-- Footer -->
    <footer class="page-footer font-small blue">
        @include('includes.footer')
    </footer>
    
    <div id="loader-bg" class="d-none"></div>
    <div id="loader" class="d-none"></div>

    <div class="d-none alert-templates">
        <div class="success">
            <div class="alert alert-success alert-dismissible hide"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong>Success!</strong> <span class="alert-text">{text}</span></div>
        </div>
        <div class="error">
            <div class="alert alert-danger alert-dismissible hide"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong>Error!</strong> <span class="alert-text">{text}</span></div>
        </div>
        <div class="cool-checkbox">
            <div class="form-check abc-checkbox abc-checkbox-info form-check-inline">
                <input class="form-check-input" id="{checkbox_id}" type="checkbox" data-checked value="{checkbox_value}" name="{checkbox_name}">
                <label class="form-check-label" for="{checkbox_id}">
                    {checkbox_text}
                </label>
            </div>
        </div>
    </div>


    <script src="{{ asset('js/manifest.js') }}" type="text/javascript"></script>
    <script src="{{ asset('js/vendor.js') }}" type="text/javascript"></script>
    <script src="{{ asset('js/app.js') }}" type="text/javascript"></script>
    <!-- page specific scripts -->
    @yield('pagespecificscripts')
    {{-- <script src="{{ asset('js/tinymce.min.js') }}" type="text/javascript"></script> --}}
</body>
</html>