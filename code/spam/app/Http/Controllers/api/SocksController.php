<?php

namespace App\Http\Controllers\api;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Models\Socks;
use Illuminate\Support\Facades\Redis;
use Carbon\Carbon;

class SocksController extends Controller
{
    protected $request;

    public function __construct(Request $request) {
        $this->request = $request;
    }

    public function index()
    {
        $params = $this->request->only(['order_col', 'order_dir']);

        // if(!empty($params['order_col']) && $params['order_col'] !== 'undefined')
        //     $data = Socks::orderBy($params['order_col'], $params['order_dir'])->get();
        // else
        //     $data = Socks::all();

        // Yes it's harder than build in
        // build all necessearly data types in here
        $socks_data = Redis::hgetall('socks:data');
        $socks_checked = Redis::zrange('socks:checked', 0, 999999999999, 'WITHSCORES');
        $socks_alive = Redis::smembers('socks:alive');
        // $socks_dead = Redis::smembers('socks:dead');

        $socks_grabber = Redis::smembers('socks:grabber');
        $socks_spam = Redis::smembers('socks:spam');
        $socks_checker = Redis::smembers('socks:checker');

        $socks_enabled = Redis::smembers('socks:enabled');
        $socks_smtp = Redis::smembers('socks:smtp');
        // $socks_blacklist = Redis::smembers('socks:blacklist');
        $socks_outerip = Redis::hgetall('socks:outerip');
        $socks_hostname = Redis::hgetall('socks:hostname');
        $socks_banned = Redis::hgetall('socks:banned');


        // TODO: do i need to optimize it via making requests for every item instead of gathering alll data at the beginning?
        // do i need to make sort at all?
        $ret_data = array_map(function($item, $key) use ($socks_checked, $socks_alive, $socks_enabled, $socks_smtp, $socks_grabber, $socks_spam, $socks_checker, $socks_hostname, $socks_outerip, $socks_banned) {
            $ret = json_decode($item, true);
            $ret['id'] = $key;
            // SISMEMBER to lower memory usage?
            $ret['enabled'] = in_array($key, $socks_enabled);
            $ret['alive'] = in_array($key, $socks_alive);
            $ret['smtp_allow'] = in_array($key, $socks_smtp);

            // $ret['type'] = in_array($key, $socks_grabber) ? 'grabber' : 'spam';

            if( in_array($key, $socks_grabber) )
                $ret['type'] = 'grabber';
            elseif( in_array($key, $socks_spam) )
                $ret['type'] = 'spam';
            elseif( in_array($key, $socks_checker) )
                $ret['type'] = 'checker';
            else
                $ret['type'] = 'unknown';

            // HGET to lower memory usage?
            $ret['checked_at'] = $socks_checked[$key] == 'never' ? null : Carbon::createFromTimestamp($socks_checked[$key])->toDateTimeString();
            $ret['hostname'] = array_key_exists($key, $socks_hostname) ? $socks_hostname[$key] : '';
            $ret['outer_ip'] = array_key_exists($key, $socks_outerip) ? $socks_outerip[$key] : '';
            $ret['banlist'] = array_key_exists($key, $socks_banned) ? $socks_banned[$key] : '';

            return $ret;
        }, $socks_data, array_keys($socks_data));
        //

        if(!empty($params['order_col']) && $params['order_col'] !== 'undefined')
            $ret_data = $this->sortBySubValue($ret_data, $params['order_col'], $params['order_dir'] == 'asc');

        // $ret_data = array_filter($ret_data, function($item) {
        //     return $item['id'] != 's:3342821438';
        // });
        // foreach ($ret_data as $item) {
        //     \Log::debug("SocksController: item:" . $item['id'] . ' size ' . strlen( json_encode($item) ) );
        // }

        return response()->json([
            'success' => true,
            'message' => 'Complete socks list.',
            // 'data' => $data
            'data' => $ret_data
        ]);

    }


    //
    /**
     * Show the form for creating a new resource.
     *
     * @return Response
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     *
     * @return Response
     */
    public function store()
    {
        // array of socks to insert
        $data = [];
        // get ip list
        $ip_list = $this->request->input('ip_list');

        // get data from request file_list
        if(!empty($this->request->file_list)){
            \Log::debug( "SocksController: processing file records:");
            foreach ($this->request->file_list as $file) {
                $filepath = $file->path();
                $ips_raw = file_get_contents($filepath);
                // $items = explode("\n", $addrs_raw);
                $ip_list .= $ips_raw;
            }
        }
        // extract all occurencies
        $data = [];

        // extract all occurencies
        preg_match_all('/((.+\:.+)?\@)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,5}/', $ip_list, $matches);

        // \Log::debug("api\SocksController::store: matches:[". json_encode($matches) ."]");


        // check if we got anything in there
        if( !is_array( $matches[0] ) || count($matches[0]) == 0 ){
            return response()->json(['success' => false, 'message' => 'No socks found in list']);
        }

        // matches[0] contains whole string
        // matches[1] contains groups
        foreach ($matches[0] as $index=>$match) {
            // echo "index:[{$index}] match:[{$match}]\n";
            if( $matches[1][$index] ){
                $credentials = $matches[1][$index];
                // extract credentials from whole string for futher ease of use
                $match = str_replace($credentials, "", $match);
                // remove @ from the end
                $credentials = substr($credentials,0,-1);
                // echo "we got credentials:[$credentials]\n";
                // echo "match now:[{$match}]\n";
                // host:port format
                $ip_array = explode(":", $match);
                // user:password format
                $credentials = explode(":", $credentials);
            }else{
                $credentials = ['', ''];
                $ip_array = explode(":",$match);
            }

            $data[] = [
                "host" => $ip_array[0],
                "port" => $ip_array[1],
                "login" => $credentials[0],
                "password" => $credentials[1],
                "type" => $this->request->input('type'),
                "enabled" => 1,
                // manually set timestamps in bulk insertion
                "created_at" => date('Y-m-d H:i:s'),
                "updated_at" => date('Y-m-d H:i:s')
            ];
        }

        if( count($data) > 0 )
            Socks::insert($data); // Eloquent approach

        // $counter = Redis::hlen('socks:data');

        // how to avoid dupes?
        Redis::pipeline(function ($pipe) use ($data) {
            foreach ($data as $item) {
                $skey = "s:" . crc32("{$item['host']}:{$item['port']}:{$item['type']}");
                $sdata = ['host' => $item['host'], 'port' => $item['port'], 'login' => $item['login'], 'password' => $item['password']];
                // insert data into hash-map
                $pipe->hset('socks:data', $skey, json_encode($sdata));
                // insert key into few sets
                $pipe->zadd('socks:checked', 0, "$skey");
                // insert data into socks:types
                $pipe->sadd("socks:{$item['type']}", "$skey");
                // insert data into alive
                $pipe->sadd("socks:dead", "$skey");
                // insert data into enabled
                $pipe->sadd("socks:enabled", "$skey");
            }
        });

        // sleep(10);

        return response()->json(['success' => true, 'message' => 'Socks are inserted. Socks check process will start shortly.']);
    }

    public function massUpdate()
    {
        $action = $this->request->input('option');
        $ids = $this->request->input('ids');
        $ids_str = implode(" ", $ids);

        // $socksTable = (new Socks())->getTable();
        if( $action == 'enable' ){
            Redis::srem("socks:disabled", $ids);
            Redis::sadd("socks:enabled", $ids);
            // Socks::whereIn('id', $ids)->update(array('enabled' => 1));
            // DB::table($userTable)->whereIn('id', $ids)->update(array('enabled' => 1));
            // remove keys from disabled
        }elseif ($action == 'disable') {
            Redis::srem("socks:enabled", $ids);
            Redis::sadd("socks:disabled", $ids);
            // Socks::whereIn('id', $ids)->update(array('enabled' => 0));
            // DB::table($userTable)->whereIn('id', $ids)->update(array('enabled' => 0));
        }elseif ($action == 'allow-smtp') {
            Redis::sadd("socks:smtp", $ids);
            // Socks::whereIn('id', $ids)->update(array('smtp_allow' => 1));
            // DB::table($userTable)->whereIn('id', $ids)->update(array('smtp_allow' => 1));
        }elseif ($action == 'disallow-smtp') {
            // Socks::whereIn('id', $ids)->update(array('smtp_allow' => 0));
            // DB::table($userTable)->whereIn('id', $ids)->update(array('smtp_allow' => 0));
            // Redis::srem("socks:smtp", $ids_str);
            Redis::srem("socks:smtp", $ids);
        }elseif ($action == 'type-spam') {
            // Socks::whereIn('id', $ids)->update(array('type' => 'spam'));
            // DB::table($userTable)->whereIn('id', $ids)->update(array('type' => 'spam'));
            // TODO: recalc key to avoid dupes
            Redis::sadd("socks:spam", $ids);
            Redis::srem("socks:grabber", $ids);
            Redis::srem("socks:checker", $ids);
        }elseif ($action == 'type-grabber') {
            // TODO: recalc key to avoid dupes
            Redis::sadd("socks:grabber", $ids);
            Redis::srem("socks:spam", $ids);
            Redis::srem("socks:checker", $ids);
        }elseif ($action == 'type-checker') {
            // TODO: recalc key to avoid dupes
            Redis::sadd("socks:checker", $ids);
            Redis::srem("socks:spam", $ids);
            Redis::srem("socks:grabber", $ids);
        }elseif ($action == 'delete-all-dead') {
            // Socks::where('alive', 0)->whereNotNull('checked_at')->delete();

            // just doing regular delete but ids are got from proper set
            $ids = Redis::smembers('socks:dead');
            $ids_str = implode(" ", $ids );
            // \Log::error("SocksController: delete-all-dead: {$id_str}");
            if(strlen($ids_str) > 2)
                $action = "delete";
        }elseif ($action == 'delete-all-banlisted') {
            // Socks::where('banlist', '!=', '')->delete();
            $ids = array_keys( Redis::hgetall('socks:banned') );
            $ids_str = implode(" ", $ids);
            if(strlen($ids_str) > 2)
                $action = "delete";
        }

        if ($action == 'delete') {
            // Socks::whereIn('id', $ids)->delete();
            // DB::table($userTable)->whereIn('id', $ids)->delete();
            Redis::srem('socks:alive', $ids);
            Redis::srem('socks:dead', $ids);
            Redis::srem("socks:enabled", $ids);
            Redis::srem("socks:disabled", $ids);
            Redis::srem("socks:grabber", $ids);
            Redis::srem("socks:spam", $ids);
            Redis::srem("socks:checker", $ids);
            Redis::srem("socks:smtp", $ids);
            Redis::zrem("socks:checked", $ids);
            // remove from hashes
            Redis::hdel("socks:data", $ids);
            Redis::hdel("socks:outerip", $ids);
            Redis::hdel("socks:hostname", $ids);
            Redis::hdel("socks:banned", $ids);
        }

        return response()->json(['success' => true, 'message' => 'Changes applied.']);

    }

    /**
     * Display the specified resource.
     *
     * @param  int  $id
     * @return Response
     */
    public function show($id)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @param  int  $id
     * @return Response
     */
    public function edit($id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     *
     * @param  int  $id
     * @return Response
     */
    public function update($id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  int  $id
     * @return Response
     */
    public function destroy($id)
    {
        //
    }

    /**
     * @param array $array
     * @param string $value
     * @param bool $asc - ASC (true) or DESC (false) sorting
     * @param bool $preserveKeys
     * @return array
     * */
    private function sortBySubValue($array, $value, $asc = true, $preserveKeys = false)
    {
        if (is_object(reset($array))) {
            $preserveKeys ? uasort($array, function ($a, $b) use ($value, $asc) {
                return $a->{$value} == $b->{$value} ? 0 : ($a->{$value} <=> $b->{$value}) * ($asc ? 1 : -1);
            }) : usort($array, function ($a, $b) use ($value, $asc) {
                return $a->{$value} == $b->{$value} ? 0 : ($a->{$value} <=> $b->{$value}) * ($asc ? 1 : -1);
            });
        } else {
            $preserveKeys ? uasort($array, function ($a, $b) use ($value, $asc) {
                return $a[$value] == $b[$value] ? 0 : ($a[$value] <=> $b[$value]) * ($asc ? 1 : -1);
            }) : usort($array, function ($a, $b) use ($value, $asc) {
                return $a[$value] == $b[$value] ? 0 : ($a[$value] <=> $b[$value]) * ($asc ? 1 : -1);
            });
        }
        return $array;
    }

    public function getSocksStats()
    {

        // return response("hui");
        // get all unchecked
        $socks_unchecked = array_keys(Redis::zrange('socks:checked', 0, 1, 'WITHSCORES'));

        // get all alive
        $socks_alive = Redis::smembers('socks:alive');
        // get all dead
        $socks_dead = Redis::smembers('socks:dead');
        // get all smtp
        $socks_smtp = Redis::smembers('socks:smtp');
        // get all banned
        $socks_banned = array_keys( Redis::hgetall('socks:banned') );

        // found dead smtp
        $ret_dead = array_intersect($socks_smtp, $socks_dead);
        // if no smtp - show all dead actually
        if( count($ret_dead) == 0 && count($socks_dead) > 0 ){
            $ret_dead = $socks_dead;
        }
        // found alive smtp
        $ret_smtp = array_intersect($socks_smtp, $socks_alive);
        // found banned smtp
        $ret_banned = array_intersect($socks_smtp, $socks_banned);
        // found unchecked smtp
        $ret_unchecked = array_intersect($socks_smtp, $socks_unchecked);

        // shell uploader
        $su_started = Redis::get('shell_upload:started');
        $su_stopped = Redis::get('shell_upload:stopped');
        $su_clear_all = Redis::get('shell_upload:clear_all');
        $su_removing = Redis::get('shell_upload:removing');

        // status 0 - stopped, 1 - mark as started, timestamp - started
        $smtp_status = (int)Redis::get('smtp_sender:started');

        // stop_all, idle, started
        // if( $smtp_status == 'stop_all' ){
        // }


        return response()->json(['success' => true, 'message' => [
            'smtp' => count($ret_smtp),
            'dead' => count($ret_dead),
            'banned' => count($ret_banned),
            'unchecked' => count($ret_banned),
            'shells' => [
                'started' => $su_started,
                'stopped' => $su_stopped,
                'clear_all' => $su_clear_all,
                'removing' => $su_removing,
            ],
            'smtp_send' => [
                'started' => $smtp_status,
            ]
        ]]);
    }
}
