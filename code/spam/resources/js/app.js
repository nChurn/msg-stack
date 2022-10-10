/**
 * First we will load all of this project's JavaScript dependencies which
 * includes Vue and other libraries. It is a great starting point when
 * building robust, powerful web applications using Vue and Laravel.
 */

// require('./axios');
require('./bootstrap');
require('./index');
require('./paginator');
require('./socks');
require('./mail_accs');
require('./mail_acc.addressbook');
require('./mail_acc.mail_dump');
require('./campaign.all');
require('./campaign.new');
require('./campaign.details');
// require('./campaign.edit');
require('./cmr');
require('./send_rules');
require('./system_settings');

// require('../../node_modules/trumbowyg/dist/trumbowyg.min.js')

// require('./tinymce.min.js');
// require('./themes/modern/theme.min.js');

// Add vue support
window.Vue = require('vue');
window.EventBus = new Vue();

VueAxios = require('vue-axios');
Vue.use(VueAxios, axios);

CxltToastr = require('cxlt-vue2-toastr').default;
Vue.use(CxltToastr);

// Popover = require('vue-js-popover').default;
// Vue.use(Popover, { tooltip: true });

VTooltip = require('v-tooltip').default
Vue.use(VTooltip);

var Paginate = require('vuejs-paginate')
Vue.component('paginate', Paginate)


// Dropdown = require('bootstrap-vue/es/components/dropdown');
// Vue.use(Dropdown);
// BootstrapVue = require('bootstrap-vue');
// Vue.use(BootstrapVue);

// /**
//  * The following block of code may be used to automatically register your
//  * Vue components. It will recursively scan this directory for the Vue
//  * components and automatically register them with their "basename".
//  *
//  * Eg. ./components/ExampleComponent.vue -> <example-component></example-component>
//  */

// // const files = require.context('./', true, /\.vue$/i)
// // files.keys().map(key => Vue.component(key.split('/').pop().split('.')[0], files(key).default))

// Vue.component('paginate', require('vuejs-paginate'));
var Paginate = require('vuejs-paginate')
Vue.component('paginate', Paginate)

Vue.component('example-component', require('./components/ExampleComponent.vue').default);
Vue.component('search-component', require('./components/SearchComponent.vue').default);
Vue.component('text-field-component', require('./components/TextFieldComponent.vue').default);
Vue.component('mail-acc-list-component', require('./components/EmailAccountsComponent.vue').default);
Vue.component('attachment-list-component', require('./components/AttachmentsComponent.vue').default);
Vue.component('attachment-upload-component', require('./components/AttachmentsUploadComponent.vue').default);
Vue.component('spam-base-list-component', require('./components/SpamBaseListComponent.vue').default);
Vue.component('spam-base-details-component', require('./components/SpamBaseDetailsComponent.vue').default);
Vue.component('campaign-record-details-component', require('./components/CampaignRecordDetailsComponent.vue').default);
Vue.component('macros-create-component', require('./components/MacrosCreateComponent.vue').default);
Vue.component('macros-list-component', require('./components/MacrosListComponent.vue').default);

// // /*
// //  *  Next, we will create a fresh Vue application instance and attach it to
// //  *  the page. Then, you may begin adding components to this application
// //  * or customize the JavaScript scaffolding to fit your unique needs.
// //  */
// // Define a new component called button-counter

// // new Vue({ el: '#app' })

const app = new Vue({
    el: '#app',
});

// EventBus.$on('append-search', (evt, search) => {
// 	// console.log('Got event from buss:', evt, search);
//   // console.log(`Oh, that's nice. It's gotten ${clickCount} clicks! :)`)
// });
