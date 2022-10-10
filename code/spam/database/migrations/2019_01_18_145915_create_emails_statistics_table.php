<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateEmailsStatisticsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        // spam campaign statistics
        Schema::create('campaign_addressbook', function (Blueprint $table) {
            $table->increments('id');
            // reference to spam campaign
            $table->unsignedInteger('campaign_id');
            $table->foreign('campaign_id')->references('id')->on('campaign')->onDelete('cascade');

            $table->unsignedInteger('mail_account_addressbook_id')->nullable();
            $table->foreign('mail_account_addressbook_id')->references('id')->on('mail_account_addressbook')->onDelete('set null');

            $table->unsignedInteger('mail_account_id')->nullable()->comment('just for ease of use');
            $table->foreign('mail_account_id')->references('id')->on('mail_accounts')->onDelete('set null');

            // 
            $table->string('address')->default('')->comment('might be from addressbok or from external spambase');

            // avoid insertion of multiple same addresses
            $table->unique(['id', 'address']);
            // error, must be, will be fixted in later migrations
            // $table->unique(['campaign_id', 'address']);

            $table->integer('record_status')->default(0)->comment('0-not sent, 1- sending, 2- sent ok, 3-sent error');
            $table->text('record_status_txt')->default('')->comment('error log for each mail in attempt');

            $table->longText('error_log')->default('');
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
        Schema::dropIfExists('emails_statistic');
        Schema::dropIfExists('campaign_addressbook');
    }
}
