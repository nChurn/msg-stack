<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class MaildumpAddFromAndToFields extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('mail_dump', function (Blueprint $table) {
            //
            $table->text('to')->default('')->after('mail_account_id');
            $table->text('from')->default('')->after('mail_account_id');
            // $table->unique(['mail_account_id', 'msg_num']);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('mail_dump', function (Blueprint $table) {
            $table->dropColumn(['to', 'from']);
        });
    }
}
