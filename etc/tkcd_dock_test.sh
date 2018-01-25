#!/bin/sh

target=~/tmp/tkcd_dock_test/`date +%m%d`

mkdir -p $target

# @note tkcd_P__1x1_restart need to verify the no sync is required
declare -a positive_ts=(
                        "tkcd_P__1x1_bind"
                        "tkcd_P__1x1_wr_one_tile"
                        "tkcd_P__1x1_rw_one_tile"
                        "tkcd_P__1x1_wr_more_tiles"
                        "tkcd_P__1x1_rw_more_tiles"
                        "tkcd_P__1x1_restart"
                        )

# @todo need a way to re-write the tile-group, tile-group out-of-sync
declare -a bind_error_ts=(
                    "tkcd_P__1x1_dock_bind__host2_host3_bind_error"
                    "tkcd_P__1x1_dock_bind__host2_host3_host4_bind_error"
                    "tkcd_P__1x1_dock_bind__host1_bind_error"
                    "tkcd_P__1x1_dock_bind__ep1_tg_error"
                    "tkcd_P__1x1_dock_bind__ep2_tg_error"
                    "tkcd_P__1x1_dock_bind__ep1_ep2_tg_error"
                    "tkcd_P__1x1_dock_bind__ep0_ep1_ep2_tg_error"
                        )
# testbench: 5 tkcd
### @NOTE need a way to clean up the bind resource at node-bind timeout cases
declare -a bind_timeout_ts=(
                    "tkcd_P__1x1_dock_bind__host2_host3_bind_tout"
                    "tkcd_P__1x1_dock_bind__host2_host3_host4_bind_tout"
                    "tkcd_P__1x1_dock_bind__ep0_tg_tout"
                    "tkcd_P__1x1_dock_bind__ep1_tg_tout"
                    "tkcd_P__1x1_dock_bind__ep2_tg_tout"
                    "tkcd_P__1x1_dock_bind__ep1_ep2_tg_tout"
                    "tkcd_P__1x1_dock_bind__ep0_ep1_ep2_tg_tout"
                        )

declare -a no_ts=(
                    "bind write, remove disk ==> rebuild"
#                    "bind write, stop ep1, cleanup ep1 db, restart ep1 ==> rebuild"
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

declare -a rd_dirty_tile_ts=(
                    "tkcd_P__1x1_tileset_1_dirty__forward_read"
                    "tkcd_P__1x1_tileset_1_dirty__forward_read__ep1_tout"
                        )

# @todo need a way to persist tileGrp and tile meta data at beging of rebuild
declare -a rebuild_ts=(
                    "tkcd_P__1x1_rebuild__on_start"
                    "tkcd_P__1x1_rebuild__on_disk_deletion"
                    "tkcd_P__1x1_rebuild__on_ep0_replacement"
                    "tkcd_P__1x1_rebuild__on_ep1_replacement"
                    "tkcd_P__1x1_rebuild__on_ep2_replacement"
                    )

declare -a misc_ts=(
                    "tkcd_P__1x1_write_ep1_all_error"
                    "tkcd_P__1x1_write_ep1_error__no_ep2"
                   )

declare -a tsuites=(
                    ${positive_ts[@]}
                    ${bind_error_ts[@]}
                    ${bind_timeout_ts[@]}
                    ${io_no_ep_ts[@]}
                    ${io_error_ts[@]}
                    ${io_timeout_ts[@]}
                    ${rd_dirty_tile_ts[@]}
                    ${rebuild_ts[@]}
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


