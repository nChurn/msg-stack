<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Socks extends Model
{
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'socks';

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
    protected $fillable = ['name', 'host', 'port', 'login', 'password', 'type', 'enabled', 'smtp_allow', 'checked_at', 'latency', 'speed'];
}
