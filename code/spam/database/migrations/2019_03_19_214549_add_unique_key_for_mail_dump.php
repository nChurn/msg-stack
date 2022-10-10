<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddUniqueKeyForMailDump extends Migration
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
            $table->unique(['mail_account_id', 'msg_num', 'mail_date']);
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
            // drop foreign key relation before drop unique
            $table->dropForeign('mail_dump_mail_account_id_foreign');
            $table->dropUnique('mail_dump_mail_account_id_msg_num_mail_date_unique');
            // return foreign after droping unique
            $table->foreign('mail_account_id')->references('id')->on('mail_accounts');
        });
    }
}
