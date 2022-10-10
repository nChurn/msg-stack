<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class ChangeAddressUniqueStatementToCampaignAddressbook extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('campaign_addressbook', function (Blueprint $table) {
            //
            // $table->dropUnique('campaign_addressbook_id_address_unique');
            $raw_sql1 = "ALTER TABLE `campaign_addressbook` DROP INDEX `campaign_addressbook_id_address_unique`;";
            // DB::statement($raw_sql1);

            // TODO: this one may be tricky, befor doing it
            // - backip all records from campaign_addressbook with insert-ignore statement
            // - remove them from table and do migration
            // - restore data from backup

            // // clear database from bumb fuck data
            // $raw_sql2 = "DELETE `a` FROM `campaign_addressbook` AS `a`, `campaign_addressbook` AS `b` WHERE ";
            // // Ensures one version remains
            // $raw_sql2 .= "`a`.`id` < `b`.`id` ";
            // // Any duplicates you want to check for
            // $raw_sql2 .= "AND (`a`.`address` = `b`.`address`) AND (`a`.`campaign_id` = `b`.`campaign_id`);";
            // DB::statement($raw_sql2);

            $raw_sql3 = "ALTER TABLE campaign_addressbook ADD UNIQUE INDEX campaign_addressbook_campaign_id_address_unique (campaign_id, address);";
            DB::statement($raw_sql3);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('campaign_addressbook', function (Blueprint $table) {
            //
            $table->unique(['id', 'address']);
            $table->dropUnique('campaign_addressbook_campaign_id_address_unique');
        });
    }
}
