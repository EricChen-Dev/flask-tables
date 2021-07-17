var tablesVue = {
    data() {
        return {
            table_data: [], // 表格数据存放位置
            search: '', //正在搜索的字段
            searchResultData: [],   //搜索结果

            currentPage: 1, //现在分页位置，默认为第1页
            pageSize: 20, //默认显示20条

            tempList: [],   //当前分页数据
            searchResultCurrentPage: 1, //搜索结果的当前页
            totalRecordsCount: 0, //总条数
            searchResultCount: 0, //搜索结果总条数

            dialogFormVisible: false, // 编辑对话框是否可见
            editingForm: {}, //正在编辑的数据
            formLabelWidth: '150px', //表单标签宽度

            table_key: '' //临时变量
        };
    },
    methods: {
        editRow(row) {
            this.editingForm = Object.assign({}, row);
            this.dialogFormVisible = true;
        },
        handleSizeChange(newPageSize) {
            //每页条数切换
            this.pageSize = newPageSize
            if (this.search !== '') {
                this.handleSearchResultCurrentChange(this.searchResultCurrentPage);
            } else {
                this.handleCurrentChange(this.currentPage)
            }
        },
        handleCurrentChange(newCurrentPage) {
            //页码切换
            this.currentPage = newCurrentPage;
            this.currentPageChangeInner(this.table_data, this.currentPage)
        },

        handleSearchResultCurrentChange(newCurrentPage) {
            //搜索结果页码切换
            this.searchResultCurrentPage = newCurrentPage;
            this.currentPageChangeInner(this.tempList, this.searchResultCurrentPage)
        },
        currentPageChangeInner(list, currentPage) {
            let from = (currentPage - 1) * this.pageSize;
            let to = currentPage * this.pageSize;
            this.tempList = [];
            for (; from < to; from++) {
                if (list[from]) {
                    this.tempList.push(list[from])
                }
            }
        },
        submit() {
            // 载入动画和更改前端表格数据
            let load = this.loading();
            var index = this.table_data.findIndex((value) => value.id === this.editingForm.id);
            this.table_data[index] = Object.assign({}, this.editingForm);
            let index_in_temp = this.tempList.findIndex((value) => value.id === this.editingForm.id);
            this.tempList[index_in_temp] = Object.assign({}, this.editingForm);
            let vueInstance = document.getElementById("table").__vue__;


            // 提交表格至后端
            $.ajax({
                url: '/main/edit?id=' + this.editingForm.id,
                data: JSON.stringify(this.editingForm),
                type: 'POST',
                contentType: "application/json",
                success: function (request) {
                    // Vue.prototype.$message.success("编辑成功");
                    Vue.prototype.$message.success("编辑成功，服务器传回消息：" + request.msg);

                    //关闭对话框
                    vueInstance.dialogFormVisible = false;

                },
                error: function (request) {
                    // Vue.prototype.$message.error("悲催，错误发生！！");
                    Vue.prototype.$message.error("错误，服务器传回消息：" + request.msg);
                },
                complete: function () {
                    load.close(); //关闭loading动画
                }
            });
            this.table_key = Math.random(); //强制刷新表格

        },
        searchChanged(search) {
            //当搜索值变动时

            //启动搜索动画
            let load = this.loading();

            if (search !== '') {
                this.searchResultData = this.table_data.filter(data => !search || data.patient_name.toLowerCase().includes(search.toLowerCase()) || data.patient_id.toLowerCase().includes(search.toLowerCase()) || data.id.toLowerCase().includes(search.toLowerCase()));
                this.searchResultCount = this.searchResultData.length;
                this.currentPageChangeInner(this.searchResultData, this.searchResultCurrentPage)
            } else {
                this.searchResultData = this.table_data;
                this.totalRecordsCount = this.table_data.length
                this.currentPageChangeInner(this.table_data, this.currentPage)
            }

            //搜索动画关闭
            load.close();
        },
        loading() {
            // loading动画instance
            return this.$loading({
                lock: true,
                text: 'Loading',
                spinner: 'el-icon-loading',
                background: 'rgba(255,255,255, 0.6)'
            });
        },
    },
    mounted() {
        // mounted最开始运行，将数据解析为json为js可用，并运行第一次currentPageChangeInner()
        this.table_data = JSON.parse(metaTableListData);
        this.totalRecordsCount = this.table_data.length;
        this.currentPageChangeInner(this.table_data, this.currentPage); //获取第一页20行数据
    }
};

var tables = Vue.extend(tablesVue);

//这里是vue加载点html的id位置
new tables().$mount('#table')