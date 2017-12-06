#!/bin/sh -x

target=~/tmp/tkcd_dock_all_`date +%m%d`

mkdir -p $target

for tsuite in "tkcd_P__1x1_dock_bind_error " \
              "tkcd_P__1x1_dock_bind_error_2 " \
              "tkcd_P__1x1_dock_bind_error_3 " \
              "tkcd_P__1x1_tileset_1_dirty__forward_read " \
; do
    python ~/gitwork/ktest/src/kd/tfwk --test-suite $tsuite
    cp ~/tmp/ktest/.__latest__/notify.html ${target}/${tsuite}.html
done


