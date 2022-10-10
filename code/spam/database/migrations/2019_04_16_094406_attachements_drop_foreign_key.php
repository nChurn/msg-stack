<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AttachementsDropForeignKey extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('attachements', function (Blueprint $table) {
            //
            $table->dropForeign('attachements_campaign_id_foreign');
            // once dropped, fill proper relations 
            $raw_sql = "INSERT INTO `attachement_campaign` (attachement_id, campaign_id) SELECT id as 'attachement_id', campaign_id FROM `attachements` WHERE campaign_id != 0;";
            DB::statement($raw_sql);

        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('attachements', function (Blueprint $table) {
            //
            $table->foreign('campaign_id')->references('id')->on('campaign')->onDelete('cascade');
        });
    }
}
