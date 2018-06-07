#!/bin/bash

rm -f guindex_*.min.js

for file in guindex_*.js; do

    file_base="$(basename $file .js)"
    file_compressed="$file_base.min.js"

    echo "Compressing file $file -> $file_compressed"

    yui-compressor --preserve-semi $file -o $file_compressed
done
