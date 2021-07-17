var tablesVue = {
    data() {
        return {
            table_data: '',
        };
    },
    methods: {},
    mounted() {
        this.table_data = JSON.parse(metaTableListData);
    }
};

var tables = Vue.extend(tablesVue);

//这里是vue加载到html的id位置
new tables().$mount('#table')