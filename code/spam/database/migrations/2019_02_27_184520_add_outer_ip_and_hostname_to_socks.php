<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddOuterIpAndHostnameToSocks extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('socks', function (Blueprint $table) {
            //
            $table->string('hostname')->default('')->after('smtp_allow');
            $table->string('outer_ip')->default('')->after('smtp_allow');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('socks', function (Blueprint $table) {
            //
            $table->dropColumn(['outer_ip', 'hostname']);

        });
    }
}
