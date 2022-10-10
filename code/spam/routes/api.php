<?php

use Illuminate\Http\Request;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

// This noe cant be cached, also - completely useless in my project
// Route::middleware('auth:api')->get('/user', function (Request $request) {
//     return $request->user();
// });

Route::group([/*'prefix' => 'api',*/ 'middleware' => ['auth.basic:web,login']], function () {
	// Route::resource handles common CRUD shit
	// Verb 		URI 					Action 	Route Name
	// GET 			/socks 					index 	socks.index
	// GET 			/socks/create 			create 	socks.create
	// POST 		/socks 					store 	socks.store
	// GET 			/socks/{photo} 			show 	socks.show
	// GET 			/socks/{photo}/edit 	edit 	socks.edit
	// PUT/PATCH 	/socks/{photo} 			update 	socks.update
	// DELETE 		/socks/{photo} 			destroy socks.destroy

	Route::resources([
		'socks' => 'api\SocksController',
		'cmr' => 'api\CheckMailReceiverController',
    	// 'mail_accs' => 'api\EmailAccountsController',
    	// 'test_accs' => 'api\EmailAccountsController',
    	'campaigns' => 'api\CampaignsController',
    	'send_rules' => 'api\SendRulesController',
	]);

	// Route::resources(['{acc_type}', 'api\EmailAccountsController'])->where('acc_type', '(mail_accs|test_accs)');
	Route::get('{acc_type}', array('as' => 'api.acc.type.get', 'uses' => 'api\EmailAccountsController@index'))->where('acc_type', '(mail_accs|test_accs)');
	Route::post('{acc_type}', array('as' => 'api.acc.type.post', 'uses' => 'api\EmailAccountsController@store'))->where('acc_type', '(mail_accs|test_accs)');

	// custom methods handlers
	Route::post('socks/mass_update', 'api\SocksController@massUpdate');
	Route::get('socks_stats', 'api\SocksController@getSocksStats');

	Route::post('mail_accs/mass_update', 'api\EmailAccountsController@massUpdate');
	Route::post('mail_accs/name/{id}', 'api\EmailAccountsController@name');
	Route::post('mail_accs/from_mail/{id}', 'api\EmailAccountsController@from_mail');
	Route::post('addressbook_field/{id}', 'api\EmailAccountsController@updateHolderField');
	Route::post('{acc_type}/mass_update', array( 'as' => 'api.acc.mass_update', 'uses' => 'api\EmailAccountsController@massUpdate'))->where('acc_type', '(mail_accs|test_accs)');
	Route::post('/add_addresses/{id}', 'api\EmailAccountsController@addAddresses');
	Route::get('/mail_dump/details/{id}', 'api\EmailAccountsController@mailDumpDetails');

	Route::post('send_rules/mass_update', 'api\SendRulesController@massUpdate');

	Route::post('campaign/update/{id}/', 'api\CampaignsController@update');
	Route::post('campaign/{id}/status/{status}', 'api\CampaignsController@status');
	Route::get('/attachements/{id}', 'api\CampaignsController@getAttachements');
	Route::get('campaign/{id}/details/records', 'api\CampaignsController@detailsAddressBook');
	Route::post('campaign/{id}/details/update', 'api\CampaignsController@addressBookMassUpdate');

	Route::name('api.spam_base.')->prefix('spam_base')->group(function(){
		Route::get('list', 'api\SpamBaseController@index')->name('list');
		Route::get('get/{id}', 'api\SpamBaseController@get')->name('get');
		// Route::post('new', 'api\SpamBaseController@index')->name('new');
		Route::post('store/{id}', 'api\SpamBaseController@store')->name('store');
		Route::get('delete/{id}', 'api\SpamBaseController@delete')->name('delete');
		Route::post('mass_update', 'api\SpamBaseController@massUpdate')->name('mass_update');
		Route::get('export/{id}', 'api\SpamBaseController@export')->name('export');
	});

	Route::name('api.system_settings.')->prefix('system_settings')->group(function(){
		Route::post('{skey}', 'api\SystemSettingsController@storeSettings')->name('store');
	});

	Route::name('api.attachments.')->prefix('attachments')->group(function(){
		Route::get('/', 'api\AttachmentsController@index')->name('index');
		Route::get('groups', 'api\AttachmentsController@groups')->name('groups');
		Route::post('new', 'api\AttachmentsController@create')->name('create');
		Route::post('delete', 'api\AttachmentsController@delete')->name('delete');
		Route::post('update/{id}', 'api\AttachmentsController@update')->name('update');
	});

	Route::name('api.macros.')->prefix('macros')->group(function(){
		Route::get('/', 'api\MacrosController@index')->name('index');
		Route::post('/new', 'api\MacrosController@store')->name('store');
		Route::post('/remove', 'api\MacrosController@remove')->name('remove');

	});
});
