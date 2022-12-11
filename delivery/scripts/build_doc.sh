#!/usr/bin/env bash

# Find current script's directory and go there
BASEDIR=$(dirname "$0")
cd ${BASEDIR}

# Catch XAIoGraphs version
VERSION=$(cat ../../VERSION)
echo "Building HTML documentation for XAIoGraphs ${VERSION}"

# Move into the documentation directory
cd ../../docs

# Define some useful variables
SOURCEDIR=./source
BUILDDIR=./build
CODEDIR=../xaiographs

# Clean former documentation
rm -rf ${BUILDDIR}/*

# Prepare workspace
mkdir -p ${BUILDDIR}/log

# Build documentation
sphinx-apidoc -o ${SOURCEDIR} ${CODEDIR}
sphinx-build -b html -c ${SOURCEDIR} ${SOURCEDIR} ${BUILDDIR}/html | tee ${BUILDDIR}/log/output.txt

# Pack documentation into tar file
tar -zcvf ${BUILDDIR}/xaiographs_doc-${VERSION}.tar.gz ${BUILDDIR}/html
