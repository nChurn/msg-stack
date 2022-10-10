<?php

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class SystemSettingsTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $settings = [
            "campaign" => [
                "max_active_campaigns" => 5,
                "workers_per_campaign" => 5,
                "connection_per_proxy" => 1,
                "cmp_check_interval" => 5,
                // "max_messages" => 10000,
                // "per_time" => 300
            ],
            "socks_checker" => [
                "number_process" => 10,
            ],
            "mail_grabber" => [
                "number_process" => 20,
                "process_per_proxy" => 5,
                "partial" => 50,
                "max_mail_days_old" => 90
            ]
        ];

        //
        DB::table('system_settings')->delete();
        DB::table('system_settings')->insert([
            'settings' => json_encode($settings),
            'created_at' => Carbon::now()->format('Y-m-d H:i:s'),
            'updated_at' => Carbon::now()->format('Y-m-d H:i:s')
        ]);
    }
}
