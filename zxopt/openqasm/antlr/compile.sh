#!/bin/bash

VERSION=4.9.2
EXECUTABLE_NAME=antlr-$VERSION-complete.jar
GRAMMAR_FILE=OpenQASM.g4

curl -O https://www.antlr.org/download/$EXECUTABLE_NAME
echo Generating lexer and parser
java -jar $EXECUTABLE_NAME -Dlanguage=Python3 $GRAMMAR_FILE
rm $EXECUTABLE_NAME
echo Done