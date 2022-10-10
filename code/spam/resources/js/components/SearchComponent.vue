<template>
    <div class="form-group">
        <label for="search_input">{{label_text}}</label>
        <div class="input-group input-group-sm">
            <input class="form-control py-2" v-model="search" v-bind:id="search_input_id" name="search" type="search" v-on:keyup="keyUpHandler">
            <span class="input-group-append">
                <button class="btn btn-secondary" type="button" v-on:click="submitSearch">
                    <i class="fa fa-search"></i>
                </button>
            </span>
        </div>
    </div>
</template>

<script>
    export default {
        props: {
            'label_text':{
                type: String,
            },
            'search_input_id': {
                type: String,
            },
            'append_search_event': {
                type: String,
                default: 'append-search'
            },
        },
        data:function (){
            return {
                search: ''
            }
        },
        mounted() {
            // console.log('Search Component mounted.')
        },
        methods: {
            keyUpHandler(evt){
                if(evt.keyCode == 13)
                    this.submitSearch(evt);
                else{
                    this.$root.$emit('keyup-search', evt, this.search);
                    EventBus.$emit('keyup-search', evt, this.search);
                }
            },

            submitSearch: function(evt){
                // this.$root.$emit('append-search', evt, this.search);
                // EventBus.$emit('append-search', evt, this.search);
                this.$root.$emit(this.append_search_event, evt, this.search);
                EventBus.$emit(this.append_search_event, evt, this.search);
            },

            // updateHandler: function(evt){

            // }
        }
    }
</script>
