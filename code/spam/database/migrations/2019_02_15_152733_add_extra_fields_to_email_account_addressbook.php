<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddExtraFieldsToEmailAccountAddressbook extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('mail_account_addressbook', function (Blueprint $table) {
            //reverse order
            $table->string('rest')->default('')->after('name');
            $table->string('company')->default('')->after('name');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('mail_account_addressbook', function (Blueprint $table) {
            //
            $table->dropColumn(['company', 'rest']);
        });
    }
}
