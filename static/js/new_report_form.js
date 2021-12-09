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
            // console.log(this.zdmJson[main])
            return this.zdmJson[main].data.find(item => item.id === id)
        },
        matchShowCondition(main, zdm_id) {
            let zdm = this.getZdmData(main, zdm_id)

            if (zdm.related_id === null || zdm.related_id === '') {
                return true
            } else if (zdm.related_id_condition === this.form[zdm.related_id]) {
                return true
            } else if (zdm.related_id_condition.includes("/")) {
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
        saveAsDraft() {
            //    保存为草稿不作验证
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
                finishedDate: '',
                status: '草稿',
                data: data
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
        reformatDate(date){
            //格式 yyyy/MM/dd HH:MM:SS
            return date.getFullYear() +"/"+ (date.getMonth()+1) +"/"+ date.getDate() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
        }
    },
    beforeMount() {
        // 初始化表单规则，别删那个temp
        let temp = {};
        for (let key in zdm) {
            for (let item of zdm[key]['data']) {
                // 这里可以预填表格
                if (item['type'] === '字符串') {
                    temp[item['id']] = '';
                } else if (item['type'] === '数组') {
                    temp[item['id']] = [];
                } else if (item['sql_type'] === 'datetime') {
                    temp[item['id']] = '';
                } else {
                    temp[item['id']] = '';
                }
                // 根据第五列是否为必填
                if (item['nullable'] !== "是") {
                    // 如果是'是'，则在rules新建规则字典，key为id，如CS-1-1-1
                    this.rules[item['id']] = [{
                        required: true,
                        message: item['name'] + "是必填项", trigger: 'change'
                    }];
                }
            }

        }
        this.form = Object.assign({}, temp);
        // 初始化选择选项
        this.options = {};
        for (let item of xz) {
            //遍历xz，将选项加入到对应options的键值对中
            if (this.options[item['dbz_id']]) {  // 如果已存在键值
                this.options[item['dbz_id']].push({value: item['option'], label: item['label']});
            } else {
                // 未存在此键值，则新建键值和数组
                this.options[item['dbz_id']] = [];
                this.options[item['dbz_id']].push({value: item['option'], label: item['label']});
            }
        }

        // 预填表格 - hard code
        this.form["SBM"] = patient["SBM"];
        this.form["CM-0-1-1-1"] = patient["ZKYS"] //质控医师
        this.form["CM-0-1-1-2"] = patient["ZKHS"] //质控护士
        this.form["CM-0-1-1-3"] = patient["ZZYS"] //主治医师
        this.form["CM-0-1-1-4"] = patient["ZRHS"] //责任护士
        this.form["CM-0-1-1-5"] = major //上报科室
        this.form["caseId"] = patient["BAH"] //患者病案号
        this.form["IDCard"] = this.replaceZfz(patient["SFZH"]) //患者身份证号
        this.form["CM-0-2-1-1"] = patient["CSNYR"] //出生年月日
        this.form["CM-0-2-1-6"] = patient["XSDCSTZ"] //新生儿出生体重（克）
        this.form["CM-0-2-4-1"] = patient["RYSJ"] //入院日期时间
        this.form["CM-0-2-4-2"] = patient["CYSJ"] //出院日期时间
        // this.form["CM-0-3-1"] = patient["ZKYS"] //费用支付方式
        // this.form["CM-0-1-1-1"] = patient["ZKYS"] //质控医师

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
