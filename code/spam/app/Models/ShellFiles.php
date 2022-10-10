<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ShellFiles extends Model
{
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'shell_files';

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
    protected $fillable = ['name', 'size', 'data', 'export_name'];

    protected $hidden = ['data'];
}
