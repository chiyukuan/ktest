#! /bin/sh -x

target=~/tmp/0630_hdd

mkdir -p $target

for tsuite in "small"
do
    python ~/gitwork/ktest/src/kd/tfwk --test-suite $tsuite
    cp ~/tmp/ktest/.__latest__/notify.html ${target}/${tsuite}.html
done


