<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ScanRules extends Model
{
    //
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'scan_rules';

    /**
     * Indicates if the model should be timestamped.
     *
     * @var bool
     */
    public $timestamps = true;

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [ 
        'rule', 'exclude', 'is_active', 'enabled'
    ];
}
