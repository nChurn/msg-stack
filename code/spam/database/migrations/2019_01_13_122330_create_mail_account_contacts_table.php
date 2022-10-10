<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateMailAccountContactsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('mail_account_addressbook', function (Blueprint $table) {
            $table->increments('id');
            $table->string('address')->default('');
            $table->string('name')->default('');
            // make address unique field to avoid multiple occurencies
            $table->unique('address');
            // reference to email account
            $table->unsignedInteger('email_account_id');
            $table->foreign('email_account_id')->references('id')->on('mail_accounts')->onDelete('cascade');
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
        Schema::dropIfExists('mail_account_addressbook');
        Schema::dropIfExists('mail_account_contacts');
    }
}
