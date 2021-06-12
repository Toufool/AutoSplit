#!/usr/bin/env bash

BASEDIR=$(dirname "$0")
pyinstaller -w -F --icon=src/icon.ico "BASEDIR/../src/AutoSplit.py"
