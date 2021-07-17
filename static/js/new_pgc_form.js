var formVue = {
    data() {
        return {
            form: {},   //表单数据存放
            isCollapse: false,  //导航栏默认展开状态
            options: {},    //表单选项
            rules: {}, //表单验证规则
            active: "",
            focused: "",
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
            return this.form[id];
        },
        submit() {
            //    提交表单
            // 表单验证
            this.$refs["form"].validate((valid, invalidObj) => {
                if (valid) {
                    alert('submit!');
                } else {
                    scrollToID(Object.keys(invalidObj)[0])
                    console.log(Object.keys(invalidObj)[0])
                    return false;
                }
            });
        },
        inputs(value){
            console.log(value)
        }
    },
    beforeMount() {
        // 初始化表单规则，别删那个temp
        var temp = {};
        for (let key in zdm) {
            for (let item of zdm[key]) {
                // 这里可以预填表格
                temp[item[1]] = undefined;
                // 根据第五列是否为必填
                if (item[4] === "是") {
                    // 如果是'是'，则在rules新建规则字典，key为id，如CS-1-1-1
                    this.rules[item[1]] = [{
                        required: true,
                        message: item[2] + "是必填项", trigger: 'change'
                    }];
                }
            }

        }
        this.form = Object.assign({}, temp);
        // 初始化选择选项
        for (let item of xz) {
            //遍历xz，将选项加入到对应options的键值对中
            if (this.options[item[1]]) {  // 如果已存在键值
                this.options[item[1]].push({value: item[2], label: item[3]});
            } else {
                // 未存在此键值，则新建键值和数组
                this.options[item[1]] = [];
                this.options[item[1]].push({value: item[2], label: item[3]});
            }
        }

    },
    mounted(){
    }
};

var form = Vue.extend(formVue);

//这里是vue加载到html的id位置
new form().$mount('#new_pgc_form')
