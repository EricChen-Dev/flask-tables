var formVue = {
    data() {
        return {
            form: {},   //表单数据存放
            isCollapse: false,  //导航栏默认展开状态
            options: {},    //表单字段可选项
            rules: {}, //表单验证规则
            active: "",
            focused: "",
            zdmJson: {}
        };
    },
    methods: {
        handleOpen(key, keyPath) {
            console.log(key, keyPath);
        },
        handleClose(key, keyPath) {
            console.log(key, keyPath);
        },
        moveToAnchor(key, keyPath) {
            //路径最后的#改为点击到的index
            window.location.hash = key;
        },
        getData(id) {
            if (id === 'None')
                return ''
            else
                return this.form[id];
        },
        getZdmData(main, id) {
            return this.zdmJson[main].data.find(item => item['字段名称'] === id)
        },
        matchShowCondition(main, zdm_id) {
            let zdm = Object.assign({}, this.getZdmData(main, zdm_id))
            zdm.related_id = zdm['关联表']
            zdm.related_id_condition = zdm['关联条件']
            if (zdm.related_id === null && zdm.related_id_condition === null) {
                return true
            } else if (zdm.related_id !== null && zdm.related_id === zdm['字段名称']) {
                //等于自己的情况
                return true
            } else if (zdm.related_id !== null && zdm.related_id_condition === null) {
                //当相关项为空时
                return this.form[zdm.related_id] === undefined || this.form[zdm.related_id] === '' || this.form[zdm.related_id] === null || this.form[zdm.related_id] !== 'UTD';
            } else if (zdm.related_id_condition === this.form[zdm.related_id]) {
                return true
            }
            else if (this.form[zdm.related_id].includes(zdm.related_id_condition))
                return true
             else if (zdm.related_id_condition.includes("/")) {
                let conditions = zdm.related_id_condition.split("/")
                return !!conditions.includes(this.form[zdm.related_id]);
            }
            return false
        },
        replaceZfz(zfz) {
            return zfz.substr(0, 4) + '**********' + zfz.substr(14, 4)
        },
        submit() {
            // 提交表单
            // 表单验证
            this.$refs["form"].validate((valid, invalidObj) => {
                let data = Object.assign({}, this.form);
                data.IDCard = patient["SFZH"];

                let postData = {
                    sbm: patient.SBM,
                    dbz: dbz.id,
                    dbz_name: dbz.name,
                    cykb: patient.CYKB,
                    zzys: patient.ZZYS,
                    zzysks: zzys.major,
                    txys: txys,
                    finishedDate: this.reformatDate(new Date()),
                    status: '已完成',
                    data: data
                }
                if (valid) {
                    axios.post(window.location.pathname + window.location.search, postData)
                        .then(response => {
                            console.log(response)
                            if (response.data.outcome) {
                                window.location.href = response.data.next;
                            } else {
                                this.$message.error('未知错误');
                            }
                            this.loading = false;
                        })
                } else {
                    scrollToID(Object.keys(invalidObj)[0])
                    return false;
                }
            });
        },
        saveAsDraft(status) {
            //    保存为草稿不作验证
            let data = Object.assign({}, this.form);
            data.IDCard = patient["SFZH"];
            let postData = {
                sbm: patient.SBM,
                cykb: patient.CYKB,
                zzys: patient.ZZYS,
                zzysks: zzys.major,
                txys: txys,
                finishedDate: '',
                status: '草稿',
                data: data
            }
            if (status === 'ignore') {
                // 如果点击的废弃按钮
                postData.status = '废弃'
            }

            axios.post(window.location.pathname + window.location.search, postData)
                .then(response => {
                    console.log(response)
                    if (response.data.outcome) {
                        window.location.href = response.data.next;
                    } else {
                        this.$message.error('未知错误');
                    }
                    this.loading = false;
                })
        },
        reformatDate(date) {
            //格式 yyyy/MM/dd HH:MM:SS
            return date.getFullYear() + "/" + (date.getMonth() + 1) + "/" + date.getDate() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
        },
    },
    beforeMount() {
        // 初始化表单规则，别删那个temp
        let temp = {};
        for (let key in zdm) {
            for (let item of zdm[key]['data']) {
                // 这里可以预填表格
                if (item['数据类型'] === '数组') {
                    temp[item['字段名称']] = [];
                } else if (item['数据类型'] === '数值') {
                    temp[item['字段名称']] = 0;
                } else {
                    temp[item['字段名称']] = '';
                }
                // 根据第五列是否为必填
                if (item['上传时不能为空'] === "是") {
                    // 如果是'是'，则在rules新建规则字典，key为id，如CS-1-1-1
                    this.rules[item['字段名称']] = [{
                        required: true,
                        message: item['数据采集项目'] + "是必填项", trigger: 'change'
                    }];
                }
            }

        }
        this.form = Object.assign({}, temp);
        // 初始化选择选项
        this.options = {};
        for (let item of xz) {
            //遍历xz，将选项加入到对应options的键值对中
            if (this.options[item['关联表']]) {  // 如果已存在键值
                this.options[item['关联表']].push({value: item['选择项'], label: item['值内容']});
            } else {
                // 未存在此键值，则新建键值和数组
                this.options[item['关联表']] = [];
                this.options[item['关联表']].push({value: item['选择项'], label: item['值内容']});
            }
        }

        for (let item in zdm) {
            for (let row of zdm[item].data) {
                console.log(row)

                if (row['预填字段'] !== null) {
                }
            }
        }

        // for (var group in zdm) {
        //     for (let row of zdm[group].data) {
        //         if (row['预填字段'] !== null) {
        //             console.log(row)
        //
        //             if (row['数据类型'] === '数组') {
        //                 console.log(this.options[row['字段名称']])
        //                 this.form[row['字段名称']].append()
        //             } else {
        //                 this.form[row['字段名称']] = patient[0][row['预填字段']]
        //             }
        //
        //         }
        //     }
        // }


        this.zdmJson = zdm;

    },
    mounted() {
    }
};

// 这里更改了Vue的分隔符识别，{{ }}和jinja冲突
Vue.options.delimiters = ['{*', '*}'];
var form = Vue.extend(formVue);
//这里是vue加载到html的id位置
new form().$mount('#new_report_form')
