<?php

namespace App\Http\Controllers\api;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Models\SystemSettings;
use Carbon\Carbon;
use Illuminate\Support\Facades\Redis;
use App\Traits\DefaultSettings;

class SystemSettingsController extends Controller
{
    use DefaultSettings;

    protected $request;
    protected $settings;

    public function __construct(Request $request) {
        $this->request = $request;

        $settings = Redis::hgetall('settings');
        array_walk($settings, function(&$a, $b) {
            $a = json_decode($a, true);
        });

        // check for missing keys
        $def_settings = config('system_settings');


        if( empty($settings) ){
            // try database
            $settings = SystemSettings::first();
            // if not exists, get defaults
            if( is_null($settings) ){
                $data = json_encode($def_settings);
                $settings = new SystemSettings();
                $settings->settings = $data;
                $settings->save();

            }else{
                $data = json_decode($settings->settings, true);
                // $data = $this->array_merge_recursive_distinct($data, $def_settings);
                $data = $this->array_merge_recursive_distinct($def_settings, $data);
                $settings->update(['settings' => json_encode($data)]);
            }

            // create redis record:
            foreach ($data as $key => $value) {
                Redis::hset('settings', $key, json_encode($value));
            }

            // always save assoc array array
            $settings = $data;
        }

        $this->settings = $settings;
    }

    /**
     * Store a newly created resource in storage.
     *
     * @return Response
     */
    public function storeSettings($skey)
    {
        $all_keys = $this->request->post();
        // generate proper values
        $update_data = [];
        foreach ($all_keys as $key => $value) {
            $update_data[$key] = $value;
        }

        $update_data['updated_at'] = time();

        // save data to redis
        Redis::hset('settings', $skey, json_encode($update_data));

        // generate data for database
        // $all_settings = json_decode($this->settings->settings, true);
        $all_settings = $this->settings;
        $all_settings[$skey] = $update_data;

        // $update_data['settings'] = json_encode($all_settings);
        $db_update = [
            'updated_at' => Carbon::now(),
            'settings' => json_encode($all_settings)
        ];

        SystemSettings::first()->update($db_update);

        return response()->json(['success' => true, 'message' => implode(" ", explode('_',ucfirst($skey)))  . ' settings updated.']);
    }
}
