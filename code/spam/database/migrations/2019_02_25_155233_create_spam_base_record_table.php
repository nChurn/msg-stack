<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateSpamBaseRecordTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('spam_base_record', function (Blueprint $table) {
            $table->increments('id');
            $table->string('address')->default('');
            $table->string('name')->default('');

            // reference to email account
            $table->unsignedInteger('email_account_id')->nullable();
            $table->foreign('email_account_id')->references('id')->on('mail_accounts')->onDelete('set null');
            // reference to email account
            $table->unsignedInteger('spam_base_id');
            $table->foreign('spam_base_id')->references('id')->on('spam_base')->onDelete('cascade');

            // make record unique per spam base
            $table->unique(['address', 'spam_base_id']);

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
        Schema::dropIfExists('spam_base_record');
    }
}
