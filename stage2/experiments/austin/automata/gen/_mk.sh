#!/bin/bash
# assemble hdr + body + ftr  -> $1
cat gen/_hdr.lean gen/_body.lean gen/_ftr.lean > "$1"
