#!/usr/bin/env bash


baseDirForScriptSelf=$(cd "$(dirname "$0")"; pwd)

bash ${baseDirForScriptSelf}/run_ds9_or_ximtool.sh

if [ -d alipy_out ];then
    if [ "$1" == "s" ];then
        read -p "clear the alipy_out:Y or N ?" input1
        #input="y"
        if [ "$input1" == "y" -o "$input1" == "Y" ];then
            echo clear all  the alipy_out 
            rm -R alipy_out
            rm updatelst
        fi
    fi
fi

python ${baseDirForScriptSelf}/demo1.py 
if [ "$1" == "s" ];then
    check='yes'
else
    check='no'
fi

echo cd alipy_out
cd alipy_out

python ${baseDirForScriptSelf}/list_check.py ${check}
python ${baseDirForScriptSelf}/aperphot.py
python $baseDirForScriptSelf/apermag.py ${check}
while [ $? == "1" ]
do  
    
    echo errfile reboot
    python ${baseDirForScriptSelf}/list_check.py ${check}
    python $baseDirForScriptSelf/apermag.py ${check}
done




# usage(){
#     echo -e "Usage: $0 [OPTIONS]"
#     echo -e " -H --help  display help info ."
#     exit 1
# }

# while [ $# -gt 0 ]; do
#     case $1 in
#         -h|--help)
#             usage
#             shift 1
#             ;;
#     esac
# done
