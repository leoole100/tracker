#!/bin/bash
cd doc
pandoc -s main.tex -o ../README.md --shift-heading-level-by=1