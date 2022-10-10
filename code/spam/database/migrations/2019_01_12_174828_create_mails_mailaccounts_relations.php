<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateMailsMailaccountsRelations extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        // Schema::create('mails_mailaccounts_relations', function (Blueprint $table) {
        //     $table->integer('email_id')->unsigned();
        //     $table->foreign('email_id')->references('id')->on('emails');
        //     $table->integer('mail_account_id')->unsigned();
        //     $table->foreign('mail_account_id')->references('id')->on('mail_accounts');
        //     // $table->increments('id');
        //     // $table->timestamps();
        // });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('mails_mailaccounts_relations');
    }
}
