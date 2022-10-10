<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateScanRulesTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('scan_rules', function (Blueprint $table) {
            $table->increments('id');
            $table->string('rule');
            // if true - rule check that letter DOES NOT HAVE match
            $table->boolean('exclude');
            $table->boolean('enabled');
            // make this pair unique, ot avoid double addings
            $table->unique(['rule', 'exclude']);
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('scan_rules');
    }
}
