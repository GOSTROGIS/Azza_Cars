#!/bin/bash
# usage: fetch.sh NAME URL
UA="AzzaCars/0.1 (https://github.com/GOSTROGIS/Azza_Cars)"
out="catalog/sources/sales_us/raw/$1"
code=$(curl -sS -L -A "$UA" --max-time 60 -o "$out" -w "%{http_code}" "$2")
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
sha=$(sha256sum "$out" | cut -d' ' -f1)
size=$(stat -c %s "$out")
echo -e "$1\t$code\t$size\t$ts\t$sha\t$2" | tee -a catalog/sources/sales_us/fetch_log.tsv
