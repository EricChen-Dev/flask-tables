var tablesVue = {
    data() {
        return {
            table_data: [],
            search: '',
            operation_index_filters: [] //手术序号筛选选项
        };
    },
    methods: {
        editRow(row) {
            //编辑按钮响应位置
            console.log(row);
        },
        filter_operation_index(value, row) {
            //筛选方法
            return row.operation_index == value;
        }
    },
    mounted() {
        // mounted最开始运行，将数据解析为json为js可用
        this.table_data = JSON.parse(metaTableListData);
        this.operation_index_filters = [];
        // 将筛选项加载
        for (let row of this.table_data){
            console.log(row)
            if (!this.operation_index_filters.some(item => item.value === row.operation_index)){ //检查是否已经存在这个序号
                this.operation_index_filters.push({text: row.operation_index, value: row.operation_index});
            }
        }

    }
};

var tables = Vue.extend(tablesVue);

//这里是vue加载到html的id位置
new tables().$mount('#table')