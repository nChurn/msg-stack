<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateSocksTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('socks', function (Blueprint $table) {
            $table->increments('id');
            $table->string('host');
            $table->integer('port');
            $table->string('login')->default('');
            $table->string('password')->default('');
            $table->string('type')->default('spam'); //spam will be used to send spam, check - is for getting mails
            $table->boolean('enabled', true)->default(false);
            $table->boolean('alive', false)->default(false);
            $table->boolean('smtp_allow', false)->default(false);
            $table->bigInteger('latency',0)->default(0);
            $table->bigInteger('speed',0)->default(0);
            $table->timestamp('checked_at')->nullable()->default(null);
            $table->integer('status')->default(0); // 0 - not processed 1 - processing, 2 - processed, 3 - error processed
            $table->text('banlist')->default('');
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
        Schema::dropIfExists('socks');
    }
}
