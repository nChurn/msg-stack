<template>
    <div class="spam-base-details-container">
        <div class="row mb-3">
            <div class="col-3">
                <div class="form-group">
                    <label for="spam_base_name">Spam base name</label>
                    <input id="spam_base_name" name="text_input" class="form-control py-2" type="text_input" v-model="spamBase.name">
                </div>
            </div>
        </div>

        <div class="row mb-3" v-if="spamBase.id>0">
            <div class="col-12">
                <label>Update details:</label>
            </div>
            <div class="col-4">
                <div class="abc-checkbox abc-checkbox-info form-check form-check-inline">
                    <input id="remove_account_records" name="remove_account_records" checked="checked" type="checkbox" v-model="spamBase.remove_account_records">
                    <label for="remove_account_records">Delete old email account records</label>
                </div>
                <div class="abc-checkbox abc-checkbox-info form-check form-check-inline">
                    <input id="recreate" name="recreate" checked="checked" type="checkbox" v-model="spamBase.recreate">
                    <label for="recreate">Clear all data before update</label>
                </div>
            </div>
        </div>

        <div class="row mb-3">
            <div class="col-12">
                <label for="selected_group">Select exclude filters:</label>
            </div>
            <div class="col-3" :class="{'d-none': isFetching}">
                <div v-for="item in filter_group" class="abc-checkbox abc-checkbox-info form-check form-check-inline">
                    <input :value="item.group" v-model="spamBase.filters" name="check_list_group[]" type="checkbox" :id="'check_list_group_'+item.group">
                    <label :for="'check_list_group_'+item.group">{{item.group}}</label>
                </div>
            </div>
            <div class="col-3" :class="{'d-none': !isFetching}">
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"></div>
                </div>
            </div>
        </div>


        <div class="row mb-3">
            <div class="col-12">
                <label>Select source:</label>
            </div>
            <div class="col-4">
                <div class="abc-checkbox abc-checkbox-info form-check form-check-inline">
                    <input id="upload_from_file" name="upload_from_file" checked="checked" type="checkbox" v-model="uploadFromFile">
                    <label for="upload_from_file">Upload from file</label>
                </div>
                <div class="abc-checkbox abc-checkbox-info form-check form-check-inline">
                    <input id="insert_raw_data" name="insert_raw_data" checked="checked" type="checkbox" v-model="insertRawData">
                    <label for="insert_raw_data">Insert raw data</label>
                </div>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-3" :class="{'d-none': !uploadFromFile && !insertRawData}">
                <label for="parse_rules">Parse rules:</label>
                <input type="text" class="form-control py-2" id="parse_rules" name="parse_rules" v-model="spamBase.parse_rules" />
            </div>
        </div>
        <div class="row mb-3" :class="{'d-none': !uploadFromFile}">
            <div class="col-12">
                <label for="attachements">Select raw data from file</label>
                <input type="file" class="form-control-file" name="attachements[]" id="attachements" multiple="">
            </div>
        </div>
        <div class="row mb-3" :class="{'d-none': !insertRawData}">
            <div class="col-12">
                <div class="form-group">
                    <label for="spam_base_raw">Insert raw emails data</label>
                    <textarea name="" id="spam_base_raw" cols="30" rows="10" class="md-textarea form-control" v-model="spamBase.rawEmails"></textarea>
                </div>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-12">
                <div class="form-group">
                    <input id="enable_automatics" name="enable_automatics" checked="checked" type="checkbox" v-model="spamBase.enable_automatics">
                    <label for="enable_automatics">Enable automatics</label>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <div class="form-group">
                    <button class="btn btn-info" type="button" v-on:click="save($event)">Submit</button>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
export default {
    props: {
        'api_url': String,
        'edit_url': String,
        'mail_acc_select_event_name': {
            type: String,
            default: 'some_event'
        },
        'outer_mail_acc_select_event_name':{
            type: String,
            default: 'some_event_2'
        }
    },
    data: function() {
        return {
            spamBase: {
                "id": -1,
                "name": "",
                "selected_ids": [],
                "rawEmails": "",
                "filters":[],
                "parse_rules": "[email],[name],[company],[rest]",
                "enable_automatics": false,
            },
            filter_group: [],
            uploadFromFile: true,
            insertRawData: false,
            isUploading: false,
            isFetching: false,
        }
    },

    created() {
        EventBus.$on(this.mail_acc_select_event_name, (evt, selected_ids) => {
            this.spamBase.selected_ids = selected_ids;
        });

        this.fetch();
    },

    methods: {
        fetch(evt) {
            if (evt) {
                evt.preventDefault();
                evt.stopPropagation();
            }
            this.isFetching = true;
            var request_url = this.api_url;
            var self = this;
            // console.log('do request:', request_url);
            this.$http.get(request_url)
                .then((response) => {
                    var data = response.data.data;
                    this.filter_group = data.filter_group;

                    // process data only if exists
                    if(data.base){
                        for(var key in this.spamBase){
                            if(data.base[key])
                                this.spamBase[key] = data.base[key];
                        }

                        if( data.base.selected_ids && data.base.selected_ids.length){
                            this.dispatchOuterMailAccountsSelectionEvent();
                        }
                    }



                }).catch((error) => {
                    console.log('error', error);
                    this.showRequestError(error);
                })
                .then(() => {
                    this.isFetching = false;
                });
        },

        validate(){
            console.log(this.spamBase.filters);
            var ret = {"success": true, "message": ""};

            if(this.spamBase.name.length < 1){
                ret.success = false;
                ret.message = "Pleas fill in base name";
                return ret;
            }

            return ret;
        },

        save(evt) {
            var vaildation = this.validate();

            if(!vaildation.success){
                // this.showRequestError({ 'response': { 'statusText': vaildation.message } });
                this.showRequestError(vaildation.message, 'Validation error');
                return;
            }

            var formData = new FormData();

            // append all spam base data
            for (var key in this.spamBase) {
                formData.append(key, this.spamBase[key]);
            }

            // process files
            var $files = $('#attachements');
            var el = $files.get(0);
            var ins = el.files.length;

            if (ins < 1 && this.spamBase.selected_ids.length == 0 && this.spamBase.rawEmails == "") {
                // this.showRequestError({ 'response': { 'statusText': 'Please upload raw accaouns from txt or put in to textarea or select mail account from list' } });
                this.showRequestError('Please select file to upload or fill in raw data or select mail account from list', 'Validation error');
                return;
            }

            for (var x = 0; x < ins; x++) {
                formData.append($files.attr('name'), el.files[x]);
            }

            this.$toast.info({
                title: 'Saving spam base',
                message: "Please wait",
                position: 'top right',
                timeOut: 20000,
                progressBar: true,
                hideDuration: 0,
            });

            // var form_headers = {'Content-Type': 'multipart/form-data', ''};

            var url = this.edit_url;
            this.isUploading = true;
            // this.$http.post(url, formData, {headers: form_headers})
            this.$http.post(url, formData)
                .then((response) => {
                    this.$toast.removeAll();
                    this.showRequestSuccess(response);
                }).catch((error) => {
                    this.$toast.removeAll();
                    this.showRequestError(error);
                })
                .then(() => {
                    // this.$toast.removeAll();
                    this.isUploading = false;
                    this.fetch();
                });

        },

        showRequestError(error, title="Error processing spam base request") {
            var message = error;
            if (typeof error !== 'string' && error.response && error.response.data && typeof error.response.data == 'object') {
                message = error.response.statusText;
                var err_data = error.response.data;
                if (err_data.message) {
                    message = err_data.message;
                }
                if (err_data.file) {
                    message += "\nFile:" + err_data.file;
                }
                if (err_data.line) {
                    message += "\nLine:" + err_data.line;
                }
            }

            this.$toast.error({
                title: title,
                message: message,
                position: 'top right',
                timeOut: 7000,
                progressBar: false,
                hideDuration: 500
            });
        },

        showRequestSuccess(response, title) {
            if (!title) title = "Success";

            this.$toast.success({
                title: title,
                message: response.data.message,
                position: 'top right',
                timeOut: 3500,
                progressBar: false,
                hideDuration: 500
            });
        },

        dispatchOuterMailAccountsSelectionEvent(){
            let ids = this.spamBase.selected_ids;
            let evt_name = this.outer_mail_acc_select_event_name;
            // console.log('evt_name', evt_name);
            var evt = new CustomEvent(evt_name, {
                detail: { "ids": ids }
            });
            // console.log('dispatchSelectionEvent', ids);
            window.dispatchEvent(evt);
            EventBus.$emit(evt_name, evt, ids);
            // console.log('dispatch event', evt_name, ids);
        }
    }
}

</script>
