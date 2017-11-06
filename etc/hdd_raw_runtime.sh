#! /bin/sh -x

target=~/tmp/hdd_all_`date +%m%d`

mkdir -p $target

for tsuite in "perf_hdd_raw_runtime"
do
    python ~/gitwork/ktest/src/kd/tfwk --test-suite $tsuite
    cp ~/tmp/ktest/.__latest__/notify.html ${target}/${tsuite}.html
done


