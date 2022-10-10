<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ShellHistory extends Model
{
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'shell_history';

    /**
     * Indicates if the model should be timestamped.
     *
     * @var bool
     */
    // public $timestamps = true;

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    // protected $fillable = ['name', 'size', 'data'];

    // protected $hidden = ['data'];

    public function file()
    {
        // return $this->hasOne('App\Models\ModelName', 'foreign_key', 'local_key');
        // return $this->hasOne('App\Models\ShellFiles', 'id', 'shell_files_id');
        return $this->belongsTo( 'App\Models\ShellFiles', 'shell_files_id', 'id');
    }

    public function shell()
    {
        // return $this->hasOne('App\Models\ModelName', 'foreign_key', 'local_key');
        // return $this->hasOne('App\Models\Shells', 'id', 'shell_id');
        return $this->belongsTo( 'App\Models\ShellFiles', 'shell_files_id', 'id' );
    }
}
