#!/bin/bash
cd doc/paper
pandoc -s main.tex -o ../../README.md --shift-heading-level-by=1