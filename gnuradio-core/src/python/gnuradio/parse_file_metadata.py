#!/usr/bin/env python
#
# Copyright 2012 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import sys
from gnuradio import gr

'''
sr    Sample rate (samples/second)
time  Time as uint64(secs), double(fractional secs)
type  Type of data (see gr_file_types enum)
cplx  is complex? (True or False)
strt  Start of data (or size of header) in bytes
size  Size of data in bytes
'''

HEADER_LENGTH = 109
ftype_to_string = {gr.GR_FILE_BYTE: "bytes",
                   gr.GR_FILE_SHORT: "short",
                   gr.GR_FILE_INT: "int",
                   gr.GR_FILE_LONG: "long",
                   gr.GR_FILE_LONG_LONG: "long long",
                   gr.GR_FILE_FLOAT: "float",
                   gr.GR_FILE_DOUBLE: "double" }

ftype_to_size = {gr.GR_FILE_BYTE: gr.sizeof_char,
                 gr.GR_FILE_SHORT: gr.sizeof_short,
                 gr.GR_FILE_INT: gr.sizeof_int,
                 gr.GR_FILE_LONG: gr.sizeof_int,
                 gr.GR_FILE_LONG_LONG: 2*gr.sizeof_int,
                 gr.GR_FILE_FLOAT: gr.sizeof_float,
                 gr.GR_FILE_DOUBLE: gr.sizeof_double}

def parse_header(p, VERBOSE=False):
    dump = gr.PMT_NIL

    info = dict()

    if(gr.pmt_is_dict(p) is False):
        sys.stderr.write("Header is not a PMT dictionary: invalid or corrupt data file.\n")
        sys.exit(1)

    # EXTRACT SAMPLE RATE
    if(gr.pmt_dict_has_key(p, gr.pmt_string_to_symbol("sr"))):
        r = gr.pmt_dict_ref(p, gr.pmt_string_to_symbol("sr"), dump)
        samp_rate = gr.pmt_to_double(r)
        info["sr"] = samp_rate
        if(VERBOSE):
            print "Sample Rate: {0} sps".format(samp_rate)
    else:
        sys.stderr.write("Could not find key 'sr': invalid or corrupt data file.\n")
        sys.exit(1)

    # EXTRACT TIME STAMP
    if(gr.pmt_dict_has_key(p, gr.pmt_string_to_symbol("time"))):
        r = gr.pmt_dict_ref(p, gr.pmt_string_to_symbol("time"), dump)
        pmt_secs = gr.pmt_tuple_ref(r, 0)
        pmt_fracs = gr.pmt_tuple_ref(r, 1)
        secs = float(gr.pmt_to_uint64(pmt_secs))
        fracs = gr.pmt_to_double(pmt_fracs)
        t = secs + fracs/(1e9)
        info["time"] = t
        if(VERBOSE):
            print "Seconds: {0}".format(t)
    else:
        sys.stderr.write("Could not find key 'time': invalid or corrupt data file.\n")
        sys.exit(1)

    # EXTRACT DATA TYPE
    if(gr.pmt_dict_has_key(p, gr.pmt_string_to_symbol("type"))):
        r = gr.pmt_dict_ref(p, gr.pmt_string_to_symbol("type"), dump)
        dtype = gr.pmt_to_long(r)
        stype = ftype_to_string[dtype]
        info["type"] = stype
        if(VERBOSE):
            print "Data Type: {0} ({1})".format(stype, dtype)
    else:
        sys.stderr.write("Could not find key 'type': invalid or corrupt data file.\n")
        sys.exit(1)

    # EXTRACT COMPLEX
    if(gr.pmt_dict_has_key(p, gr.pmt_string_to_symbol("cplx"))):
        r = gr.pmt_dict_ref(p, gr.pmt_string_to_symbol("cplx"), dump)
        cplx = gr.pmt_to_bool(r)
        info["cplx"] = cplx
        if(VERBOSE):
            print "Complex? {0}".format(cplx)
    else:
        sys.stderr.write("Could not find key 'cplx': invalid or corrupt data file.\n")
        sys.exit(1)

    # EXTRACT HEADER LENGTH
    if(gr.pmt_dict_has_key(p, gr.pmt_string_to_symbol("strt"))):
        r = gr.pmt_dict_ref(p, gr.pmt_string_to_symbol("strt"), dump)
        hdr_len = gr.pmt_to_uint64(r)
        info["strt"] = hdr_len
        if(VERBOSE):
            print "Header Length: {0} bytes".format(hdr_len)
            print "Extra Header? {0}".format(hdr_len > HEADER_LENGTH)
    else:
        sys.stderr.write("Could not find key 'strt': invalid or corrupt data file.\n")
        sys.exit(1)

    # EXTRACT SIZE OF DATA
    if(gr.pmt_dict_has_key(p, gr.pmt_string_to_symbol("size"))):
        r = gr.pmt_dict_ref(p, gr.pmt_string_to_symbol("size"), dump)
        nbytes = gr.pmt_to_uint64(r)

        # Multiply itemsize by 2 if complex
        if(cplx): mult=2
        else: mult=1

        nitems = nbytes/(ftype_to_size[dtype]*mult)
        info["nitems"] = nitems
        info["nbytes"] = nbytes

        if(VERBOSE):
            print "Size of Data: {0} bytes".format(nbytes)
            print "              {0} items".format(nitems)
    else:
        sys.stderr.write("Could not find key 'size': invalid or corrupt data file.\n")
        sys.exit(1)

    return info