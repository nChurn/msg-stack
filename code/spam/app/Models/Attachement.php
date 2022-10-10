<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Redis;

class Attachement extends Model
{
    //
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'attachements';

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
    protected $fillable = ['name', 'size', 'path', 'data'];

    protected $hidden = ['data'];

    protected $appends = ['used_redis'];

    // public function email()
    // {
    //     return $this->belongsTo('App\Models\Email');
    // }

    public function campaign()
    {
        return $this->belongsTo('App\Models\Campaign');
    }

    public function getUsedRedisAttribute()
    {
        // $id = $this->attributes['id'];
        $id = $this->id;
        return (int)Redis::get("attachement:{$id}:used");
    }
}
