#!/bin/bash
VERSION=4.9.2
EXECUTABLE_NAME=antlr-$VERSION-complete.jar

curl -O https://www.antlr.org/download/$EXECUTABLE_NAME
echo Reading grammer
java -jar $EXECUTABLE_NAME -Dlanguage=Python3 openqasm.g4
rm $EXECUTABLE_NAME