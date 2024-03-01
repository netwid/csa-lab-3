#!/bin/bash

template="README-template.md"
output="README.md"

awk '
    function include(file) {
        while ((getline line < file) > 0) {
            print line
        }
        close(file)
    }

    /include\(.*\)/ {
        match($0, /include\((.*)\)/, arr)
        include(arr[1])
        next
    }

    { print }
' "$template" > "$output"

echo "README.md has been generated."
