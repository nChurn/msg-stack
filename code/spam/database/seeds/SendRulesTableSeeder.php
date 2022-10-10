<?php

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class SendRulesTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {

        $rules = [
            [
                'group' => 'general',
                'rules' => ['salesmanagement@cloud-gstat.bid','postmaster','spam','abuse','admin','blacklist','blachhole','complain','noreply','no-email','webmaster']
            ],
            [
                'group' => 'google',
                'rules' => ['@googlemail\.', '@gmail\.', '@googlegroups', 'youtube\.']
            ],
            [
                'group' => 'yahoo',
                'rules' => ['@yahoo\.', '@ymail\.', '@rocketmail', '(@|\.)att\.']
            ],            
            [
                'group' => 'aol',
                'rules' => ['@aol\.']
            ],
            [
                'group' => "microsoft",
                'rules' => ['@hotmail\.','@live\.','@office365\.','@microsoft\.','@msn\.','@outlook\.']
            ],
            [
                'group' => "the_rest_big",
                'rules' => ['@vzwpix\.com','@cableone\.','@gmx\.','verizon','@ustream\.','@sbcglobal\.','@comcast\.','\.rr\.com','@rr\.','@icloud\.','@mac\.','yandex','@bellsouth\.','@pnc\.com','yousendit','@earthlink\.','@me\.','@cox\.','@rogers\.','@btinternet\.','vodafone','charter','@juno\.','@web\.de','@vtext\.','@optonline\.','@frontier\.','@netscape\.','@fuse\.net','@yelp\.','att-mail\.','bpisports\.']
            ],
            [
                'group' => "Social",
                'rules' => ['facebook','pinterest','instagram','linkedin','twitter','@livestream\.','pornhub','\.craigslist\.','tripadvisor\.','@craigslist\.']
            ],
            [
                'group' => "Robots",
                'rules' => ['^accounts@','^postmaster@','donotreply','-reply','noreply','no-response','^news@','\.mcdlv\.','\.mcsv\.','\.rsgsv\.','\.rsys2\.','\.@Aflac-OnlineServices\.']
            ],
            [
                'group' => "Shops_etc",
                'rules' => ['amazon','walmart','bestbuy','paypal','newegg','ebay','@staples\.','booking']
            ],

            [
                'group' => "Still_in_progress",
                'rules' => ['notification','update@','updates@','godaddy','@fedex\.','\.fedex\.','@dhl\.','\.dhl\.','@ups\.','\.ups\.','@notify\.','\.notify\.','notify@','notify-','getresponse\.']
            ],
            [
                'group' => "Still_in_progress",
                'rules' => ['^support','^billpay','^service','^order','alerts@','@alerts\.','^helpdesk','^newsletter','@tickets\.','@ticketfly\.','^survey','^mailer','^mail-','^donotreply','\.local','^help','@dell\.','@hp\.','@msi\.','@asus\.','@apple\.','@pcbell\.','@ibm\.','@bankchampaign\.com','^bounce-']
            ],
            [
                'group' => "Big_banks_in_progress",
                'rules' => ['citibank','bankofamerica','\.citi\.com','@citi\.com','wellsfargo','\.chase\.com','irs\.gov','intuit\.com','@paychex\.com','americanexpress','53\.com']
            ],
            [
                'group' => "AV",
                'rules' => ['@eset\.','@avast\.','@avira\.','@norton\.','@fortinet\.','@trendmicro\.','@symantec\.','@mcafee\.','@panda\.','@drweb\.','@kaspersky\.','@avg\.','@comodo\.','@malwarebytes\.','@f-secure\.','@webroot\.','@sophos\.','@zonealarm\.']
            ],
            [
                "group" => "bad_zones",
                "rules" => ['\.za($|\s|;)','\.ru($|\s|;)','\.tr($|\s|;)','\.br($|\s|;)','\.jp($|\s|;)','\.in($|\s|;)','\.gr($|\s|;)','\.vn($|\s|;)','\.tw($|\s|;)','\.lt($|\s|;)','\.lv($|\s|;)','\.ee($|\s|;)','\.bg($|\s|;)','\.pl($|\s|;)','\.sk($|\s|;)','\.ua($|\s|;)','\.ke($|\s|;)','\.zw($|\s|;)','\.do($|\s|;)','\.cz($|\s|;)','\.kr($|\s|;)']
            ],
            [
                "group" => "euro_zones",
                "rules" => ['\.de($|\s|;)','\.fr($|\s|;)','\.be($|\s|;)','\.it($|\s|;)','\.uk($|\s|;)','\.es($|\s|;)','\.se($|\s|;)','\.nl($|\s|;)','\.at($|\s|;)']
            ]
        ];

        /*$general_rules = ['salesmanagement@cloud-gstat.bid','postmaster','spam','abuse','admin','blacklist','blachhole','complain','noreply','no-email','webmaster'];
        //
        foreach ($general_rules as $key => $value) {
            DB::table('scan_rules')->insert([
                'rule' => $value,
                'group' => $value,
                'exclude' => 1,
                'enabled' => 1,
                'created_at' => Carbon::now()->format('Y-m-d H:i:s'),
                'updated_at' => Carbon::now()->format('Y-m-d H:i:s')
            ]);
        }*/

        foreach ($rules as $rule_group) {
            $bunch = [];
            foreach ($rule_group['rules'] as $key => $value) {
                # code...
                $bunch[] = [
                    'rule' => $value,
                    'group' => strtolower($rule_group['group']),
                    'exclude' => 1,
                    'enabled' => 1,
                    'created_at' => Carbon::now()->format('Y-m-d H:i:s'),
                    'updated_at' => Carbon::now()->format('Y-m-d H:i:s')
                ];
            }

            DB::table('scan_rules')->insert($bunch);
        }
    }
}
