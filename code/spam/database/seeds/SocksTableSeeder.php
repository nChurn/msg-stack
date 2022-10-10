<?php

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class SocksTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $ips = ['192.95.57.203', '185.180.198.207', '145.249.104.111'];
        $types = ['grabber', 'spam'];
        foreach ($ips as $ip) {
            foreach ($types as $type) {
                # code...
                DB::table('socks')->insert([
                    'host' => $ip,
                    'port' => 1550,
                    'login' => 'mechatron',
                    'password' => 'MpvHdrApWq7YRgrFnBpduJQvrMcxsDE2',
                    'type' => $type,
                    'enabled' => 1,
                    'alive' => 1,
                    'smtp_allow' => 1,
                    'created_at' => Carbon::now()->format('Y-m-d H:i:s'),
                    'updated_at' => Carbon::now()->format('Y-m-d H:i:s')
                ]);
            }
        }
    }
}
