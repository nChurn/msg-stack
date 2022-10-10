<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\SystemSettings;
use Illuminate\Support\Facades\Redis;
use App\Traits\DefaultSettings;

class SystemSettingsController extends Controller
{
    use DefaultSettings;
    /**
     * Display a listing of the resource.
     *
     * @return Response
     */
    public function index()
    {

        // hashmap
        $settings = Redis::hgetall('settings');
        array_walk($settings, function(&$a, $b) {
            $a = json_decode($a, true);
        });

        // \Log::debug("Settings from redis:" . json_encode($settings));

        // check for missing keys
        $def_settings = config('system_settings');
        // \Log::debug("Settings from defaults:" . json_encode($def_settings));

        if( empty($settings) ){
            // try database
            $settings = SystemSettings::first();
            // if not exists, get defaults
            if( is_null($settings) )
                $settings = $def_settings;
            else
                $settings = json_decode($settings->settings, true);

            // $settings = $this->array_merge_recursive_distinct($settings, $def_settings);
            $settings = $this->array_merge_recursive_distinct($def_settings, $settings);
            // create redis record:
            foreach ($settings as $key => $value) {
                Redis::hset('settings', $key, json_encode($value));
            }
        }else{
            // \Log::debug("redis settings not empty, merge with defaults in case...");
            // $settings = $this->array_merge_recursive_distinct($settings, $def_settings);
            $settings = $this->array_merge_recursive_distinct($def_settings, $settings);

            \Log::error("def_settings:" . json_encode($def_settings));
            \Log::error("settings:" . json_encode($settings));
        }

        // \Log::warn("system_settings:" . json_encode($settings));

    	return view('system_settings', ['settings' => $settings]);
    }


}
