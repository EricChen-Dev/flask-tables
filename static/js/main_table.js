var tablesVue = {
    data() {
        return {
            table_data: [], // 表格数据存放位置
            major_case_data: [], //科室所有病例存放位置
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

            table_key: '', //临时变量

            loading: true,

            show_major_cases: false
        };
    },
    methods: {
        editRow(row) {
            this.editingForm = Object.assign({}, row);
            this.dialogFormVisible = true;
        },
        goToReport(row) {
            const urlParams = new URLSearchParams(window.location.search);
            const operation_id = urlParams.get('operation_id')
            if (operation_id === undefined || operation_id === null)
                window.location.href = "/report?sbm=" + row.SBM;
            else 
                window.location.href = `/report/${operation_id}?sbm=${row.SBM}`
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
            // 提交更改信息

            // 载入动画和更改前端表格数据
            let load = this.loading_animation;

            //更改现有表格中的数据
            var index = this.table_data.findIndex((value) => value.SBM === this.editingForm.SBM);
            this.table_data[index] = Object.assign({}, this.editingForm);
            let index_in_temp = this.tempList.findIndex((value) => value.SBM === this.editingForm.SBM);
            this.tempList[index_in_temp] = Object.assign({}, this.editingForm);


            // 提交表格至后端
            console.log(this.editingForm);

            axios.post('/main/edit', this.editingForm).then(response => {
                this.$message.success("编辑成功，服务器传回消息：" + response.data.msg);
                this.dialogFormVisible = false;
                load.close;
            }).catch(error => {
                this.$message.error("错误，服务器传回消息：" + error.response.data.msg)
            });

            this.table_key = Math.random(); //强制刷新表格

        },
        selectPatient(patient) {
            //启动搜索动画
            let load = this.loading_animation;
            this.currentPageChangeInner(this.searchResultData, this.searchResultCurrentPage)
            //搜索动画关闭
            load.close;
        },
        changeTo(queryString) {
            if (queryString === '') {
                this.searchResultData = this.table_data;
                this.totalRecordsCount = this.table_data.length
                this.currentPageChangeInner(this.table_data, this.currentPage)
            }
        },
        querySearchAsync(queryString, callback) {
            let load = this.loading_animation;
            console.log("query: " + queryString);
            if (queryString === '') {
                this.searchResultData = this.table_data;
                this.totalRecordsCount = this.table_data.length
                this.currentPageChangeInner(this.table_data, this.currentPage)
            } else {
                //发送查询请求
                axios.get('/main/get_patients?query=' + queryString).then(response => {
                    callback(this.onQuerySuccess(response.data));
                });
            }
            load.close;
        },
        onQuerySuccess(data) {
            this.searchResultData = Object.assign([], data.data);
            this.searchResultCount = this.searchResultData.length;
            return this.searchResultData;
        },
        loading_animation() {
            // loading动画instance
            return this.$loading({
                lock: true,
                text: 'Loading',
                spinner: 'el-icon-loading',
                background: 'rgba(255,255,255, 0.6)'
            });
        },
        changeMajorCases(showMajor){
          //    是否显示本科室病例
            if(showMajor){

            }

        }

    },
    mounted() {
        this.loading = true;
        // mounted最开始运行，将数据解析为json为js可用，并运行第一次currentPageChangeInner()
        console.log(metaTableListData)
        this.table_data = metaTableListData;
        this.totalRecordsCount = this.table_data.length;
        this.currentPageChangeInner(this.table_data, this.currentPage); //获取第一页20行数据
    }
};

var tables = Vue.extend(tablesVue);

//这里是vue加载点html的id位置
new tables().$mount('#table')