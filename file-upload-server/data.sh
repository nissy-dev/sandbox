#!/usr/bin/env bash
# -u: Fail on when existing unset variables
# -e -o pipefail: Fail on when happening command errors
set -ueo pipefail

mkdir 1g && cd 1g && mkfile 1g 1g.txt && cd .. && tar -czf 1g.tar.gz 1g && rm -rf 1g
mkdir 2g && cd 2g && mkfile 2g 2g.txt && cd .. && tar -czf 2g.tar.gz 2g && rm -rf 2g
mkdir 5g && cd 5g && mkfile 5g 5g.txt && cd .. && tar -czf 5g.tar.gz 5g && rm -rf 5g
mkdir 10g && cd 10g && mkfile 10g 10g.txt && cd .. && tar -czf 10g.tar.gz 10g && rm -rf 10g
mkdir 20g && cd 20g && mkfile 20g 20g.txt && cd .. && tar -czf 20g.tar.gz 20g && rm -rf 20g
mkdir 50g && cd 50g && mkfile 50g 50g.txt && cd .. && tar -czf 50g.tar.gz 50g && rm -rf 50g
