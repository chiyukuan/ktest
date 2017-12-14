#!/bin/sh

target=~/tmp/tkcd_dock_test/`date +%m%d`

mkdir -p $target

declare -a tsuites=("tkcd_P__1x1_dock_bind_error"
                    "tkcd_P__1x1_dock_bind_error_2"
                    "tkcd_P__1x1_dock_bind_error_3"
                    "tkcd_P__1x1_tileset_1_dirty__forward_read"
                    "tkcd_P__1x1_write_ep0_error"
                    "tkcd_P__1x1_write_ep1_error"
                    "tkcd_P__1x1_write_ep0_ep1_error"
                    "tkcd_P__1x1_write_no_ep2"
                    "tkcd_P__1x1_write_ep1_error__no_ep2"
                    "tkcd_P__1x1_write_ep1_all_error" )

for tsuite in "${tsuites[@]}" ; do

    echo  "============================ $tsuite ============================"
    python ~/gitwork/ktest/src/kd/tfwk --test-suite $tsuite
    sleep 5
    cp ~/tmp/ktest/.__latest__/notify.html ${target}/${tsuite}.html
    cp ~/tmp/ktest/.__latest__/result.log  ${target}/${tsuite}.result
done


