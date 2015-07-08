#!/bin/bash
PR_DIR=../addressimo/paymentrequest
protoc -I=$PR_DIR --python_out=$PR_DIR $PR_DIR/paymentrequest.proto