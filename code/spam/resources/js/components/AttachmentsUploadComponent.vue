<template>
    <div class="attachment-upload-container">
        <div class="row mb-3">
            <div class="col-12">
                <label for="selected_group">Select group:</label>
            </div>
            <div class="col-12">
                <div class="progress" :class="{'d-none': !isFetching}">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"></div>
                </div>
                <div :class="{'d-none': isFetching}" v-for="item in list_groups" class="abc-radio abc-radio-info form-check form-check-inline">
                    <input :value="item.group" v-model="selected_group" name="check_list_group" type="radio" :id="'redio_list_group_'+item.group">
                    <label :for="'redio_list_group_'+item.group">{{item.group}}</label>
                </div>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-12">
                <label for="selected_group">.. or write new group:</label>
            </div>
            <div class="col-2">
                <input class="form-control form-control-sm" v-model="selected_group" name="selected_group" type="text">
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <div class="abc-checkbox abc-checkbox-info form-check form-check-inline">
                    <input id="group_clear" value="1" name="group_clear" checked="" type="checkbox" v-model="group_clear">
                    <label for="group_clear">Remove old records in selected group</label>
                </div>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-12">
                <label for="attachements">Attachements</label>
                <input type="file" class="form-control-file" name="attachements[]" id="attachements" multiple="">
            </div>
        </div>

        <div class="row">
          <div class="col-4">
            <button id="upload" name="upload" class="btn btn-info" v-on:click="uploadAttaches($event)">Upload</button>
          </div>
        </div>
    </div>
</template>
<script>
export default {
    props: {
        'api_url': String,
        'create_url': String,
        'groups_url': String,
    },
    data: function() {
        return {
            selected_group: "",
            list_groups: [],
            group_clear: false,

            isFetching: false,
            isUploading: false,
        }
    },
    created() {
        console.log('created');
        // this.fetch();
    },
    mounted() {
        this.fetch();
    },
    methods: {
        fetch(evt) {
            console.log('fetching...', this.groups_url);
            var self = this;
            this.isFetching = true;

            this.$http.get(this.groups_url)
                .then((response) => {
                    var data = response.data.data;
                    this.list_groups = data.groups;
                }).catch((error) => {
                    this.showRequestError(error);
                })
                .then(() => {
                    this.isFetching = false;
                });
        },
        showRequestError(error) {
            var message = error.response.statusText;
            if (error.response.data && typeof error.response.data == 'object') {
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
                title: 'Error',
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

        uploadAttaches(evt){
            var formData = new FormData();
            // console.log('uploadAttaches fired?');

            // process other vars
            formData.append("selected_group", this.selected_group);
            formData.append("group_clear", this.group_clear);


            // process files
            var $files = $('#attachements');
            var el = $files.get(0);
            var ins = el.files.length;

            // console.log('$files', $files, 'el', el, 'ins', ins);

            if(ins<1){
                this.showRequestError({'response':{'statusText':'Please select at least one file'}});
            }

            for (var x = 0; x < ins; x++) {
                formData.append($files.attr('name'), el.files[x]);
            }

            var data = formData;
            var url = this.create_url;

            this.$toast.info({
                title: 'Uplading new attachments',
                message: "Please wait",
                position: 'top right',
                timeOut: 20000,
                progressBar: true,
                hideDuration: 0,
            });

            // var form_headers = {'Content-Type': 'multipart/form-data', ''};

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

    }
}

</script>
