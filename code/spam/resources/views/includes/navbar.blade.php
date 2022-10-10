<nav class="navbar navbar-expand-sm bg-dark navbar-dark" role="navigation">
    <!-- <a class="navbar-brand" href="{{ action("SocksController@index") }}">Socks</a> -->
  <ul class="nav navbar-nav">
    <li class="nav-item">
      <a class="nav-link" href="{{ action("SocksController@index") }}">Socks</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="{{ action("CheckMailReceiverController@index") }}">Receiver</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="{{ action("EmailAccountsController@index", 'mail_accs') }}">Accounts</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="{{ action("EmailAccountsController@index", 'test_accs') }}">Test Accounts</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="{{ route('spam_base.all') }}">Bases</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="{{ action("CampaignsController@index") }}">Campaigns</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="{{ route("attachments") }}">Attachments</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="{{ action("SendRulesController@index") }}">Send Rules</a>
    </li>

    <li class="nav-item">
      <a class="nav-link" href="{{ route('macros') }}">Macros tpls</a>
    </li>

    <li class="nav-item">
      <a class="nav-link" href="{{ route('settings.index') }}">Settings</a>
    </li>
    <!-- <li class="nav-item">
      <a class="nav-link" href="javascript:void(0)">Link 3</a>
    </li> -->
  </ul>

  <ul class="nav navbar-nav pull-right navbar-nav ml-auto">
    {{-- smtp related indicators --}}
    <li class="nav-item dropdown">
        <a class="nav-link" title="SMTP" class="nav-link dropdown-toggle" data-toggle="dropdown" href="#">SMTP</a>
        <div class="dropdown-menu">
            <a class="dropdown-item" href="{{ route('smtp_stop') }}">STOP</a>
            <a class="dropdown-item" href="{{ route('smtp_start') }}">START</a>
        </div>
    </li>
    <li class="nav-item d-none smtps smtp-sending">
      <a href="#" class="nav-link" title="Sending in prohress">
        <i class="fa fa-send"></i>
        <span class="counter counter-threads"></span>
        <span class="counter counter-success"></span>
        <span class="counter counter-failed"></span>
        <span class="counter counter-total"></span>
        <span class="counter counter-remain"></span>
      </a>
    </li>
    <li class="nav-item d-none smtps smtp-idle"><a href="#" class="nav-link" title="Sending is idle"><i class="fa fa-stop-circle"></i></a></li>
    <li class="nav-item d-none smtps smtp-preparing"><a href="#" class="nav-link" title="Sending is beign prepared"><i class="fa fa-cubes"></i></a></li>


    {{-- shells related indicators --}}
    <li class="nav-item"><a href="{{ action("ShellsController@index") }}" class="nav-link" title="Shells">Shells</a></li>
    <li class="nav-item d-none shells shells-clearing"><a href="#" class="nav-link" title="All files are being removed from shells"><i class="fa fa-trash"></i></a></li>
    <li class="nav-item d-none shells shells-removing"><a href="#" class="nav-link" title="Some files are being removed from shells"><i class="fa fa-recycle"></i></a></li>
    <li class="nav-item d-none shells shells-stopped"><a href="#" class="nav-link" title="Shellls files upload is done/stopped"><i class="fa fa-exclamation-circle"></i></a></li>
    <li class="nav-item d-none shells shells-started"><a href="#" class="nav-link" title="Files are uploading to shells"><i class="fa fa-cloud-upload"></i></a></li>
    <li class="nav-item d-none shells shells-stopping"><a href="#" class="nav-link" title="Shell uploads are stopping..."><i class="fa fa-exclamation-triangle"></i></a></li>

    {{-- socks related info --}}
    <li class="nav-item socks"><a href="{{ action("SocksController@index") }}" class="nav-link socks-smtp" title="Socks">Socks</a></li>
    <li class="nav-item socks"><a href="{{ action("SocksController@index") }}" class="nav-link socks-smtp" title="Socks"><i class="fa fa-check"></i><span class="counter"></span></a></li>
    <li class="nav-item socks"><a href="{{ action("SocksController@index") }}" class="nav-link socks-dead" title="Dead"><i class="fa fa-close"></i><span class="counter"></span></a></li>
    <li class="nav-item socks"><a href="{{ action("SocksController@index") }}" class="nav-link socks-banned" title="Banned"><i class="fa fa-ban"></i><span class="counter"></span></a></li>
    <li class="nav-item socks"><a href="{{ action("SocksController@index") }}" class="nav-link socks-unchecked" title="Unchecked"><i class="fa fa-question-circle"></i><span class="counter"></span></a></li>
  </ul>
</nav>
