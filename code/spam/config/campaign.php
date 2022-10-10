<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Campaign status
    |--------------------------------------------------------------------------
    */

    'status' => [
        'CREATED' => 0, //get rid of
        'STARTED' => 1,
        'PAUSED' => 2,
        'HIBERNATED' => 3, //get rid of
        'COMPETED' => 4,
    ],
    'record_status' => [
        'await' => 0,
        'processing' => 1,
        'success' => 2,
        'fail' => 3,
        'skip' => 4,
        'blacklist' => 5
    ],
    'fail_behaviour' => [
        'mark_fail' => 0,
        'mark_null' => 1
    ]
];
