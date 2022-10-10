<?php

use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     *
     * @return void
     */
    public function run()
    {
        $this->call(UsersTableSeeder::class);
        $this->call(SocksTableSeeder::class);
        $this->call(SendRulesTableSeeder::class);
        $this->call(CheckMailReceiversTableSeeder::class);
        $this->call(SystemSettingsTableSeeder::class);
    }
}
