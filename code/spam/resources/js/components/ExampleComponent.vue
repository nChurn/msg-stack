<template>
    <div class="container">
        <div class="row justify-content-center" >
            <div class="col-md-8">
                <div class="card card-default">
                    <div class="card-header" v-on:click="counter++">Example Component {{counter}}</div>

                    <div class="card-body">
                        I'm an example component.
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

    export default {
        data:function (){
            return {
                counter: 100
            }
        },
        mounted() {
            console.log('Component mounted.');
            console.log('window.EventBus', window.EventBus);
            window.EventBus.$on('append-search', this.onAppendSearchHandler);

        },
        methods:{
            onAppendSearchHandler: (evt, search) => {
                console.log('ExampleComponent got event from buss:', evt, search);
            }
        }
    }

</script>
