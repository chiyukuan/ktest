#!/bin/sh

target=~/tmp/plug_and_play_test/`date +%m%d`

mkdir -p $target

declare -a tsuites=(
                        "perf__620_local_1__remote_0__xfs"
                        "perf__620_local_2__remote_0__xfs"
                        "perf__620_local_4__remote_0__xfs"
                        "perf__620_local_0__remote_1__xfs"
                        "perf__620_local_0__remote_2__xfs"
                        "perf__620_local_1__remote_1__xfs"
                        "perf__620_local_2__remote_2__xfs"
                        "perf__620_local_4__remote_2__xfs"
                    )

for tsuite in "${tsuites[@]}" ; do

    #python ~/gitwork/ktest/src/kd/tfwk --test-suite $tsuite --dry-run
    #continue
    python ~/gitwork/ktest/src/kd/tfwk --test-suite $tsuite
    sleep 5
    cp ~/tmp/ktest/.__latest__/notify.html ${target}/${tsuite}.html
    cp ~/tmp/ktest/.__latest__/result.log  ${target}/${tsuite}.result

    echo "============================ $tsuite ============================" >> ${target}/result.log
    cat ${target}/${tsuite}.result >> ${target}/result.log
done


