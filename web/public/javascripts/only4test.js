/**
 * Created by yuyu on 2019/1/3.
 */
let value = 'p of vldb 2018'

arr = value.toString().split(' ')

let tmp = '';

for (let i = 0; i < arr.length; i++){
    tmp += arr[i] + ' ';
    if (i == 1){
        tmp += '\n';
    }
}

console.log(tmp)