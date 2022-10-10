<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddErrorDatetimeForMailAccounts extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('mail_accounts', function (Blueprint $table) {
            //
            $table->dateTime('error_at')->nullable()->default(null)->after('error_log');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('mail_accounts', function (Blueprint $table) {
            //
            $table->dropColumn('error_at');
        });
    }
}
