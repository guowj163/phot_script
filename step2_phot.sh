#!/usr/bin/env bash

#ref.fits,pos

baseDirForScriptSelf=$(cd "$(dirname "$0")"; pwd)

bash ${baseDirForScriptSelf}/run_ds9_or_ximtool.sh
sleep 10
curthpath=`pwd`

for dirname in `ls obj* -d`; do
#for dirname in `cat objdir`; do
  echo \<\<\<\<\<${dirname}\>\>\>\>\>
  cd  ${dirname}
  #rm updatelst
  if [ -f ref.fits ]; then
    if ! [ -f aper.txt ];then 
      cp ${baseDirForScriptSelf}/aper.txt .
    fi

    bash ${baseDirForScriptSelf}/seperate_reduce.sh $1
  fi
  cd ${curthpath}
done




dir_light=lightcurve_`date "+%Y%m%d"`
if ! [ -d ${dir_light} ]; then
  echo mkdir ${dir_light}
  mkdir ${dir_light}
fi

lightpath=`pwd`/$dir_light


for dirname in `ls obj* -d`; do
  echo \<\<\<\<\<${dirname}\>\>\>\>\>
  cd  ${dirname}
  if [ -d alipy_out ]; then
    cd alipy_out
    cp  *_obj.png ${lightpath}
    cp  *_cmp.png ${lightpath}
    cp  *_lightcurve.day ${lightpath}
  fi
  cd ${curthpath}
done


