#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4 -*-
#
# LLVM Source Files sync from Makefile.am
#
# Copyright (C) 2010-2017 Gianluigi Tiesi <sherpya@netfarm.it>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
# ======================================================================

# script deps: python-lxml

import os
import lxml.etree
from lxml import objectify

llvm_base = 'clamav/libclamav/c++/'
vcprefix = '../../../' + llvm_base
vcproj = 'msvc/proj/vc8/libclamav_llvm.vcproj'
mingwmake = 'mingw/llvm.mak'
cmake = 'cmake/llvm-sources.cmake'
projects = [ 'libclamavcxx', 'libllvmsystem', 'libllvmcodegen', 'libllvmx86codegen', 'libllvmjit' ]
blacklist = [ 'llvm/config.status', 'PointerTracking.cpp' ]

def skip_line(line):
    line = line.strip()
    if line.find('=') == -1: return False
    if line.startswith('#'): return False
    return True

def skip_lib(lib):
    if lib.find('_la_SOURCES') == -1: return True
    if lib[:-11] not in projects: return True
    return False

def parse_makefile_am(path):
    mf = open(path).read()
    mf = mf.replace('\\\n', '')
    lines = mf.split('\n')
    sources = set()
    lines = filter(skip_line, lines)
    for line in lines:
        line = line.strip().replace('+=', '=')
        key, value = line.split('=', 1)
        key, value = key.strip(), value.strip()
        if skip_lib(key): continue
        values = value.split()
        for source in values:
            if source.endswith('.h'): continue
            sources.add(source)

    map(sources.remove, blacklist)

    # vc2005 makes wrong with object files when more sources share same basename
    # so it needs to be excluded or renamed somehow, I had luck 'PointerTracking.cpp'
    basenames = []
    for source in sources:
        source = source.split('/').pop()
        if source in basenames:
            raise Exception('Duplicate basename for %s' % source)
        basenames.append(source)

    return sorted(sources)

def relpath(path):
    rel = vcprefix + path
    return rel.replace('/', '\\')

def gen_vcproj(path, mksources):
    projfd = open(path)
    header = projfd.readline()
    proj = objectify.parse(projfd)
	projfd.close()
    root = proj.getroot()
    source_files = root.xpath('Files/Filter[@Name="Source Files"]')[0]
    files = source_files.xpath('File')
    sources = []
    for f in files:
        s = f.attrib['RelativePath'].replace('\\', '/').replace(vcprefix, '')
        sources.append(s)
    sources.sort()
    print 'Needed files: %d - in vcproj: %d' % (len(mksources), len(sources))
    if sources == mksources:
        print 'VC Project unchanged'
    else:
        source_files.clear()
        source_files.attrib['Name'] = "Source Files"
        for newfile in mksources:
            newfile = vcprefix + newfile
            newfile = newfile.replace('/', '\\')
            f = lxml.etree.fromstring('<File RelativePath="%s"></File>' % newfile)
            source_files.append(f)
        out = open(path + '.new', 'w')
        out.write(header)
        proj.write(out, pretty_print=True)
        out.close()
        os.unlink(path)
        os.rename(path + '.new', path)
        print 'VC Project was updated (%d sources now)' % len(mksources)

def gen_mingwmake(path, sources):
    print 'Writing mingw makefile'
    f = open(path, 'wb')
    f.write('# Automatic generated by llvm-sync.py\n')
    f.write('# DO NOT EDIT! llvm-sync.py will overwrite this file\n\n')
    f.write('libclamav_llvm_SOURCES=$(addprefix $(clamav)/libclamav/c++/,' + ' \\\n\t'.join(sources) + ')')
    f.write('\n')
    f.close()

def gen_cmake(path, sources):
    print 'Writing cmake makefile'
    f = open(path, 'wb')
    f.write('# Automatic generated by llvm-sync.py\n')
    f.write('# DO NOT EDIT! llvm-sync.py will overwrite this file\n\n')
    f.write('set(llvm_srcs\n    ')
    f.write('\n    '.join(sources))
    f.write(')\n')
    f.close()


if __name__ == '__main__':
    sources = parse_makefile_am(llvm_base + 'Makefile.am')
    gen_mingwmake(mingwmake, sources)
    gen_cmake(cmake, sources)
    gen_vcproj(vcproj, sources)
