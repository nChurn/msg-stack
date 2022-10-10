<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class ChangeUniqueForScanRules extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('scan_rules', function (Blueprint $table) {
            // change unique for datatable
            $table->dropUnique('scan_rules_rule_exclude_unique');
            $table->unique(['rule', 'exclude', 'group']);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('scan_rules', function (Blueprint $table) {
            // restore previous set
            $table->dropUnique('scan_rules_rule_exclude_group_unique');
            $table->unique(['rule', 'exclude']);
        });
    }
}
