<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Shells extends Model
{
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'shells';

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
    protected $fillable = ['url', 'password', 'fail_checks', 'vcm_fails'];
}
