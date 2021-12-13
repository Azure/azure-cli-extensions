#!/bin/bash
node_exporter_url="http://localhost:9100/metrics"
node_exporter_metrics_location="/tmp/node_exporter_logs.txt"

echo "---------------------------------------OS details-------------------------------------------"
cat /etc/os-release
echo "----------------------------------------CPU details------------------------------------------"
cat /proc/cpuinfo
echo "----------------------------------------Memory details---------------------------------------"
cat /proc/meminfo
echo "------------------------------------------Latest system performance--------------------------"
top -b -n 1
echo "----------------------------------------calling node exporter endpoint---------------------------"
curl -o ${node_exporter_metrics_location} -w "Connect: %{time_connect} TTFB: %{time_starttransfer} Total time: %{time_total} \n" ${node_exporter_url}
