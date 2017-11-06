#!/bin/bash

RDIR="/root/.ktest/running"
QDIR="/root/.ktest/queue"
DDIR="/root/.ktest/done"
PAUSE_ME="/root/.ktest/run.sh_PAUSE"

function nextScript()
{
    if [ -f $PAUSE_ME ];
    then
        if [ "$pPause" = "Yes" ]; then
            echo ""
            echo "--"
            echo "-- Pause the run.sh. Remove ${PAUSE_ME} to resume"
            echo "--"
            pPause="No"
        fi
        nScript=""
    else
        for entry in $QDIR/*
        do
            if [ $entry = "$QDIR/*" ]; then
                nScript=""
            else
                nScript=$(basename $entry)
            fi
            break
        done
    fi
}

function runTestSuite()
{
    mv $QDIR/$nScript $RDIR/$nScript
    tsuite=${nScript#*_test_suite_}
    PYTHONPATH=/root/gitwork/myTestFwk/src python /root/gitwork/ktest/src/kd/tfwk --test-suite $tsuite
    mv $RDIR/$nScript $DDIR/${nScript}__`date +%Y_%m%d__%H%M%S`
}

function runScript()
{
    mv $QDIR/$nScript $RDIR/$nScript
    sh -x $RDIR/$nScript
    mv $RDIR/$nScript $DDIR/${nScript}__`date +%Y_%m%d__%H%M%S`
}

mkdir -p $RDIR
mkdir -p $QDIR
mkdir -p $DDIR

pWaiting="Yes"
pPause="Yes"

while true; do
    nextScript

    if [ "$nScript" = "" ]; then
        if [ "$pWaiting" = "Yes" ]; then
            echo ""
            echo "--"
            echo "-- Waiting for new task"
            echo "--"
            pWaiting="No"
        fi
        sleep 300
    elif [[ "$nScript" = *"_test_suite_"* ]]; then
        runTestSuite
        pWaiting="Yes"
        pPause="Yes"
        sleep 600
    else
        runScript
        pWaiting="Yes"
        pPause="Yes"
        sleep 600
    fi
done

# function ktest_add_test_script() { mv $1 ~/.ktest/queue/`date +%Y_%m%d__%H%M%S`_$1 ; }
