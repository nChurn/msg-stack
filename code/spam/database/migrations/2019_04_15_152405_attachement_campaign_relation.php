<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AttachementCampaignRelation extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        //
        Schema::create('attachement_campaign', function (Blueprint $table) {
            $table->increments('id');
            $table->unsignedInteger('attachement_id');
            $table->unsignedInteger('campaign_id');

            $table->foreign('attachement_id')->references('id')->on('attachements')->onDelete('cascade');
            $table->foreign('campaign_id')->references('id')->on('campaign')->onDelete('cascade');

        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('attachement_campaign');
        //
    }
}
