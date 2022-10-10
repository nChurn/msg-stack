<?php

return [

    /*
    |--------------------------------------------------------------------------
    | System settings
    |--------------------------------------------------------------------------
    */

    "campaign" => [
        "max_active_campaigns" => 5,
        "workers_per_campaign" => 5,
        "connection_per_proxy" => 1,
        "cmp_check_interval" => 5,
        "reply_days" => 30,
        // mark records as new(0)/skipped(4)/blacklisted(5), when no conversation found
        "reply_empty_status" =>0,
        // 0 - only addressbook, 1 - only bases, 2 - use both adressbook + spambases
        "use_spambases" =>0,
        // UTC 24hrs format
        "start_from" =>10,
        "end_to" =>16,
    ],
    "acc_checker" => [
        "min_hours" =>  2,
        "number_process" =>  20,
        "process_per_proxy" => 5,
        "threads_per_protocol" => 10,
        "proc_timeout_first" => 10*60,
        "proc_timeout_regular" => 5*60,
    ],
    "socks_checker" => [
        "number_process" => 10
    ],
    "mail_grabber" => [
        "number_process" => 20,
        "process_per_proxy" => 5,
        "partial" => 50,
        "max_mail_days_old" => 90
    ],
    "shells" => [
        "check_thread_amount" => 20,
        "check_thread_proxy" => "socks5://terrazaurid:p7C2SbVTsJdnbte7uKvKgU9ZzMQrD38L@5.2.72.77:11537",
        "upload_thread_amount" => 20,
        "upload_thread_proxy" => "socks5://terrazaurid:p7C2SbVTsJdnbte7uKvKgU9ZzMQrD38L@5.2.72.77:11537",
        "vcm_check_url" => "http://avcheck.net/vhm/api/v1/check/",
        "vcm_check_api" => "4ba22ba9d6676a71faa4b874bb0818e2ef02c31c",
    ],
];
