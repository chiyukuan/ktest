#!/bin/sh

target=~/tmp/tkcd_dock_test/`date +%m%d`

mkdir -p $target

declare -a positive_ts=(
                        "tkcd_P__1x1_bind"
                        "tkcd_P__1x1_wr_one_tile"
                        "tkcd_P__1x1_rw_one_tile"
                        "tkcd_P__1x1_wr_more_tiles"
                        "tkcd_P__1x1_rw_more_tiles"
                        )

declare -a bind_error_ts=(
                    "tkcd_P__1x1_dock_bind_error"
                    "tkcd_P__1x1_dock_bind_error_2"
                    "tkcd_P__1x1_dock_bind_error_3"
                        )

declare -a io_no_ep_ts=(
                    "tkcd_P__1x1_write_no_ep0"
                    "tkcd_P__1x1_write_no_ep1"
                    "tkcd_P__1x1_write_no_ep2"
                    "tkcd_P__1x1_write_no_ep0_ep2"
                    "tkcd_P__1x1_write_no_ep1_ep2"
                        )

declare -a io_error_ts=(
                    "tkcd_P__1x1_write_ep0_error"
                    "tkcd_P__1x1_write_ep1_error"
                    "tkcd_P__1x1_write_ep0_ep1_error"
                        )
declare -a io_timeout_ts=(
                    "tkcd_P__1x1_write_ep1_tout"
                    "tkcd_P__1x1_write_ep1_tout__ep1_tg_tout"
                    "tkcd_P__1x1_write_ep1_tout__ep2_tg_tout"
                    "tkcd_P__1x1_write_ep1_tout__ep1_ep2_tg_tout"
                        )


declare -a io_dirty_tile_ts=(
                    "tkcd_P__1x1_tileset_1_dirty__forward_read"
                        )

declare -a misc_ts=(
                    "tkcd_P__1x1_write_ep1_all_error"
                    "tkcd_P__1x1_write_ep1_error__no_ep2"
                   )

declare -a tsuites=(
                    ${positive_ts[@]}
                    ${bind_error_ts[@]}
                    ${io_no_ep_ts[@]}
                    ${io_error_ts[@]}
                    ${io_timeout_ts[@]}
                    ${io_dirty_tile_ts[@]}
                    ${misc_ts[@]}
                    )

for tsuite in "${tsuites[@]}" ; do

    python ~/gitwork/ktest/src/kd/tfwk --test-suite $tsuite
    sleep 5
    cp ~/tmp/ktest/.__latest__/notify.html ${target}/${tsuite}.html
    cp ~/tmp/ktest/.__latest__/result.log  ${target}/${tsuite}.result

    echo "============================ $tsuite ============================" >> ${target}/result.log
    cat ${target}/${tsuite}.result >> ${target}/result.log
done


