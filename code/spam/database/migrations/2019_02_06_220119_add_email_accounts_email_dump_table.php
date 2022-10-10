<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddEmailAccountsEmailDumpTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        //
        Schema::create('mail_dump', function (Blueprint $table) {
            $table->increments('id');
            // reference to mail account
            $table->unsignedInteger('mail_account_id');
            $table->foreign('mail_account_id')->references('id')->on('mail_accounts');
            // 
            $table->string('subject')->default('');
            $table->mediumText('body')->default('');
            $table->integer('msg_num')->default(0);
            // 
            $table->boolean('need_body')->default(false);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        //
        Schema::dropIfExists('mail_dump');
    }
}
