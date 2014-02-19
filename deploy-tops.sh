#!/bin/bash

cd $TOPS_HOME
gradle clean
$TOPS_HOME/tops-member/tops-member-server/deploy-test.sh --not-clean

$TOPS_HOME/tops-front/tops-front-operator-biz/deploy-test.sh --not-clean --no-monitor
$TOPS_HOME/tops-front/tops-front-operator-flight/deploy-test.sh --not-clean --no-monitor
$TOPS_HOME/tops-front/tops-front-operator-hotel/deploy-test.sh --not-clean --no-monitor
$TOPS_HOME/tops-front/tops-front-operator-member/deploy-test.sh --not-clean --no-monitor
$TOPS_HOME/tops-front/tops-front-operator-pricing/deploy-test.sh --not-clean --no-monitor
$TOPS_HOME/tops-front/tops-front-purchaser/deploy-test.sh --not-clean --no-monitor
$TOPS_HOME/tops-front/tops-front-provider/deploy-test.sh --not-clean --no-monitor
$TOPS_HOME/tops-front/tops-front-messaging/deploy-test.sh --not-clean --no-monitor
