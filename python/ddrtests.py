#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
# Copyright (C) 2013, Elphel.inc.
# Tests for ddrc_test01.v, loosely following ddrc_test01_testbench.tf
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http:#www.gnu.org/licenses/>.
#  
__author__ = "Andrey Filippov"
__copyright__ = "Copyright 2014, Elphel, Inc."
__license__ = "GPL"
__version__ = "3.0+"
__maintainer__ = "Andrey Filippov"
__email__ = "andrey@elphel.com"
__status__ = "Development"
import mmap
import sys
import struct
import random
DRY_MODE= False # True
MONITOR_EMIO=False #True

def write_mem (addr, data):
    global DEBUG_MODE;
    if DRY_MODE:
        print ("write_mem(0x%x,0x%x)"%(addr,data))
        return
    PAGE_SIZE=4096
    endian="<" # little, ">" for big
    with open("/dev/mem", "r+b") as f:
        page_addr=addr & (~(PAGE_SIZE-1))
        page_offs=addr-page_addr
        if (page_addr>=0x80000000):
            page_addr-= (1<<32)
        mm = mmap.mmap(f.fileno(), PAGE_SIZE, offset=page_addr)
        packedData=struct.pack(endian+"L",data)
        d=struct.unpack(endian+"L",packedData)[0]
        mm[page_offs:page_offs+4]=packedData
#        print ("0x%08x <== 0x%08x (%d)"%(addr,d,d))
        mm.close()
    if MONITOR_EMIO and VEBOSE:
        gpio0=read_mem (0xe000a068)
        gpio1=read_mem (0xe000a06c)
        print("GPIO: %04x %04x %04x %04x"%(gpio1>>16, gpio1 & 0xffff, gpio0>>16, gpio0 & 0xffff))
        if ((gpio0 & 0xc) != 0xc) or ((gpio0 & 0xff00) != 0):
            print("******** AXI STUCK ************")
            exit (0)
            

def read_mem (addr):
    if DRY_MODE:
        print ("read_mem(0x%x)"%(addr))
        return
    PAGE_SIZE=4096
    endian="<" # little, ">" for big
    writeMode=len(sys.argv)>2
    with open("/dev/mem", "r+b") as f:
        page_addr=addr & (~(PAGE_SIZE-1))
        page_offs=addr-page_addr
        if (page_addr>=0x80000000):
            page_addr-= (1<<32)
        mm = mmap.mmap(f.fileno(), PAGE_SIZE, offset=page_addr)
        data=struct.unpack(endian+"L",mm[page_offs:page_offs+4])
        d=data[0]
#        print ("0x%08x ==> 0x%08x (%d)"%(addr,d,d))
        return d
        mm.close()

# Define I/O addresses

use200Mhz=True;
PHASE_WIDTH =              8
CMD_PAUSE_BITS=           10
CMD_DONE_BIT=             10

CONTROL_ADDR =        0x1000 # AXI write address of control write registers
CONTROL_ADDR_MASK =   0x1400 # AXI write address of control registers
STATUS_ADDR =         0x1400 # AXI write address of status read registers
STATUS_ADDR_MASK =    0x1400 # AXI write address of status registers
BUSY_WR_ADDR =        0x1800 # AXI write address to generate busy
BUSY_WR_ADDR_MASK =   0x1c00 # AXI write address mask to generate busy
CMD0_ADDR =           0x0800 # AXI write to command sequence memory
CMD0_ADDR_MASK =      0x1800 # AXI read address mask for the command sequence memory
PORT0_RD_ADDR =       0x0000 # AXI read address to generate busy
PORT0_RD_ADDR_MASK =  0x1c00 # AXI read address mask to generate busy
PORT1_WR_ADDR =       0x0400 # AXI read address to generate busy
PORT1_WR_ADDR_MASK =  0x1c00 # AXI read address mask to generate busy
#    #relative address parameters below to be ORed with CONTROL_ADDR and CONTROL_ADDR_MASK respectively
DLY_LD_REL =            0x080 # address to generate delay load
DLY_LD_REL_MASK =       0x380 # address mask to generate delay load
DLY_SET_REL =           0x070 # address to generate delay set
DLY_SET_REL_MASK =      0x3ff # address mask to generate delay set
RUN_CHN_REL =           0x000 # address to set sequnecer channel and  run (4 LSB-s - channel)
RUN_CHN_REL_MASK =      0x3f0 # address mask to generate sequencer channel/run
PATTERNS_REL =          0x020 # address to set DQM and DQS patterns (160x0055)
PATTERNS_REL_MASK =     0x3ff # address mask to set DQM and DQS patterns
PATTERNS_TRI_REL =      0x021 # address to set DQM and DQS tristate on/off patterns {dqs_off,dqs_on, dq_off,dq_on} - 4 bits each
PATTERNS_TRI_REL_MASK = 0x3ff # address mask to set DQM and DQS tristate patterns
WBUF_DELAY_REL =        0x022 # extra delay (in mclk cycles) to add to write buffer enable (DDR3 read data)
WBUF_DELAY_REL_MASK =   0x3ff # address mask to set extra delay
PAGES_REL =             0x023 # address to set buffer pages {port1_page[1:0],port1_int_page[1:0],port0_page[1:0],port0_int_page[1:0]}
PAGES_REL_MASK =        0x3ff # address mask to set DQM and DQS patterns
CMDA_EN_REL =           0x024 # address to enable(0x825)/disable(0x824) command/address outputs  
CMDA_EN_REL_MASK =      0x3fe # address mask for command/address outputs
SDRST_ACT_REL =         0x026 # address to activate(0x827)/deactivate(0x826) active-low reset signal to DDR3 memory  
SDRST_ACT_REL_MASK =    0x3fe # address mask for reset DDR3
CKE_EN_REL =            0x028 # address to enable(0x829)/disable(0x828) CKE signal to memory   
CKE_EN_REL_MASK =       0x3fe # address mask for command/address outputs
DCI_RST_REL =           0x02a # address to activate(0x82b)/deactivate(0x82a) Zynq DCI calibrate circuitry  
DCI_RST_REL_MASK =      0x3fe # address mask for DCI calibrate circuitry
DLY_RST_REL =           0x02a # address to activate(0x82d)/deactivate(0x82c) delay calibration circuitry  
DLY_RST_REL_MASK =      0x3fe # address mask for delay calibration circuitry
EXTRA_REL =             0x02e # address to set extra parameters (currently just inv_clk_div)
EXTRA_REL_MASK =        0x3ff # address mask for extra parameters
REFRESH_EN_REL =        0x030 # address to enable(0x31) and disable (0x30) DDR refresh
REFRESH_EN_REL_MASK =   0x3fe # address mask to enable/disable DDR refresh
REFRESH_PER_REL =       0x032 # address to set refresh period in 32 x tCK
REFRESH_PER_REL_MASK =  0x3ff # address mask set refresh period
REFRESH_ADDR_REL =      0x033 # address to set sequencer start address for DDR refresh
REFRESH_ADDR_REL_MASK = 0x3ff # address mask set refresh sequencer address

ADDRESS_NUMBER=            15 

#BASEADDR = 0x40000000 # start of AXI GP0
BASEADDR_PORT0_RD = PORT0_RD_ADDR << 2                                  # 0x0000  << 2
BASEADDR_PORT1_WR = PORT1_WR_ADDR << 2                                  # 0x0000 << 2 = 0x000
BASEADDR_CMD0 =    CMD0_ADDR << 2                                       # 0x0800 << 2 = 0x2000
BASEADDR_CTRL =    (CONTROL_ADDR | BUSY_WR_ADDR) << 2                   # with busy
BASEADDR_STATUS =  STATUS_ADDR << 2                                     # 0x0800 << 2 = 0x2000
BASEADDR_DLY_LD =  BASEADDR_CTRL | (DLY_LD_REL <<2)                     # 0x080, address to generate delay load
BASEADDR_DLY_SET = BASEADDR_CTRL | (DLY_SET_REL<<2)                     # 0x070, address to generate delay set
BASEADDR_RUN_CHN = BASEADDR_CTRL | (RUN_CHN_REL<<2)                     # 0x000, address to set sequnecer channel and  run (4 LSB-s - channel)
BASEADDR_PATTERNS =BASEADDR_CTRL | (PATTERNS_REL<<2)                    # 0x020, address to set DQM and DQS patterns (160x0055)
BASEADDR_PATTERNS_TRI =BASEADDR_CTRL | (PATTERNS_TRI_REL<<2)            # 0x021, address to set DQM and DQS tristate on/off patterns {dqs_off,dqs_on, dq_off,dq_on} - 4 bits each
BASEADDR_WBUF_DELAY =BASEADDR_CTRL | (WBUF_DELAY_REL<<2)                # 0x022, extra delay (in mclk cycles) to add to write buffer enable (DDR3 read data)
BASEADDR_PAGES =   BASEADDR_CTRL | (PAGES_REL<<2)                       # 0x023, address to set buffer pages {port1_page[1:0],port1_int_page[1:0],port0_page[1:0],port0_int_page[1:0]}
BASEADDR_CMDA_EN = BASEADDR_CTRL | (CMDA_EN_REL<<2)                     # 0x024, address to enable(0x825)/disable(0x824) command/address outputs  
BASEADDR_SDRST_ACT = BASEADDR_CTRL | (SDRST_ACT_REL<<2)                 # 0x026 address to activate(0x827)/deactivate(0x826) active-low reset signal to DDR3 memory     
BASEADDR_CKE_EN =  BASEADDR_CTRL | (CKE_EN_REL<<2)                      # 0x028
BASEADDR_DCI_RST =  BASEADDR_CTRL | (DCI_RST_REL<<2)                    # 0x02a (+1 - enable)
BASEADDR_DLY_RST =  BASEADDR_CTRL | (DLY_RST_REL<<2)                    # 0x02c (+1 - enable)
BASEADDR_EXTRA =   BASEADDR_CTRL | (EXTRA_REL<<2)                       # 0x02e, address to set extra parameters (currently just inv_clk_div)
BASEADDR_REFRESH_EN =   BASEADDR_CTRL | (REFRESH_EN_REL<<2)             # address to enable(0x31) and disable (0x30) DDR refresh
BASEADDR_REFRESH_PER =   BASEADDR_CTRL | (REFRESH_PER_REL<<2)           # address (0x32) to set refresh period in 32 x tCK
BASEADDR_REFRESH_ADDR =   BASEADDR_CTRL | (REFRESH_ADDR_REL<<2)         # address (0x33)to set sequencer start address for DDR refresh
BASEADDRESS_LANE0_ODELAY = BASEADDR_DLY_LD;  
BASEADDRESS_LANE0_IDELAY = BASEADDR_DLY_LD+(0x10<<2)  
BASEADDRESS_LANE1_ODELAY = BASEADDR_DLY_LD+(0x20<<2)  
BASEADDRESS_LANE1_IDELAY = BASEADDR_DLY_LD+(0x30<<2)  

BASEADDRESS_CMDA  = BASEADDR_DLY_LD+(0x40<<2)
BASEADDRESS_PHASE = BASEADDR_DLY_LD+(0x60<<2)
STATUS_PSHIFTER_RDY_MASK = 0x100;
STATUS_LOCKED_MASK = 0x200;
STATUS_SEQ_BUSY_MASK = 0x400;

if use200Mhz:
    DLY_LANE0_DQS_WLV_IDELAY = 0xb0 # idelay dqs
    DLY_LANE1_DQS_WLV_IDELAY = 0xb0 # idelay dqs
    DLY_LANE0_ODELAY= [0x98,0x4c,0x94,0x94,0x98,0x9c,0x92,0x99,0x98,0x94] # odelay dqm, odelay ddqs, odelay dq[7:0]
    
    DLY_LANE0_IDELAY=      [0x40,0x13,0x14,0x14,0x1c,0x13,0x14,0x13,0x1a] # idelay dqs, idelay dq[7:0
    DLY_LANE1_ODELAY= [0x98,0x4c,0x98,0x98,0x98,0x9b,0x99,0xa8,0x9c,0x98] # odelay dqm, odelay ddqs, odelay dq[7:0]
    
    DLY_LANE1_IDELAY=      [0x40,0x2c,0x2b,0x2c,0x2c,0x34,0x30,0x33,0x30] # idelay dqs, idelay dq[7:0
    DLY_CMDA=  [0x3c,0x3c,0x3c,0x3c,0x3b,0x3a,0x39,0x38,0x34,0x34,0x34,0x34,0x33,0x32,0x31,0x30,
                0x00,0x2c,0x2c,0x2c,0x2b,0x2a,0x29,0x28,0x24,0x24,0x24,0x24,0x23,0x22,0x21,0x20] # odelay odt, cke, cas, ras, we, ba2,ba1,ba0, X, a14,..,a0

# alternative to set same type delays to the same value    
    DLY_DQ_IDELAY =  0x20
    DLY_DQ_ODELAY =  0xa0
    DLY_DQS_IDELAY = 0x40
    DLY_DQS_ODELAY = 0x4c #should match with phase write leveling
    DLY_DM_ODELAY =  0xa0
    DLY_CMDA_ODELAY =0x50
    
else:   
    DLY_LANE0_DQS_WLV_IDELAY = 0xe8 # idelay dqs
    DLY_LANE1_DQS_WLV_IDELAY = 0xe8 # idelay dqs
    DLY_LANE0_ODELAY= [0x74,0x74,0x73,0x72,0x71,0x70,0x6c,0x6b,0x6a,0x69] # odelay dqm, odelay ddqs, odelay dq[7:0]
    DLY_LANE0_IDELAY=      [0xd8,0x73,0x72,0x71,0x70,0x6c,0x6b,0x6a,0x69] # idelay dqs, idelay dq[7:0
    DLY_LANE1_ODELAY= [0x74,0x74,0x73,0x72,0x71,0x70,0x6c,0x6b,0x6a,0x69] # odelay dqm, odelay ddqs, odelay dq[7:0]
    DLY_LANE1_IDELAY=      [0xd8,0x73,0x72,0x71,0x70,0x6c,0x6b,0x6a,0x69] # idelay dqs, idelay dq[7:0
    DLY_CMDA=  [0x5c,0x5c,0x5c,0x5c,0x5b,0x5a,0x59,0x58,0x54,0x54,0x54,0x54,0x53,0x52,0x51,0x50,
                0x00,0x4c,0x4c,0x4c,0x4b,0x4a,0x49,0x48,0x44,0x44,0x44,0x44,0x43,0x42,0x41,0x40] # odelay odt, cke, cas, ras, we, ba2,ba1,ba0, X, a14,..,a0
# alternative to set same type delays to the same value    
    DLY_DQ_IDELAY =  0x20
    DLY_DQ_ODELAY =  0xa0
    DLY_DQS_IDELAY = 0x40
    DLY_DQS_ODELAY = 0x4c #should match with phase write leveling
    DLY_DM_ODELAY =  0xa0
    DLY_CMDA_ODELAY =0x50


NUM_FINE_STEPS=    5
#`endif   
    
DLY_PHASE=       0x2c # 0x1c # mmcm fine phase shift, 1/4 tCK
    
DQSTRI_FIRST=    0x3 # DQS tri-state control word, first when enabling output 
DQSTRI_LAST=     0xc # DQS tri-state control word, first after disabling output
DQTRI_FIRST=     0x7 # DQ tri-state control word, first when enabling output 
DQTRI_LAST=      0xe # DQ tri-state control word, first after disabling output
WBUF_DLY_DFLT=   0x6 # extra delay (in mclk cycles) to add to write buffer enable (DDR3 read data)
WBUF_DLY_WLV=    0x7 # write leveling mode: extra delay (in mclk cycles) to add to write buffer enable (DDR3 read data)
    
#DLY_PHASE= 80xdb # mmcm fine phase shift
INITIALIZE_OFFSET=  0x00 # moemory initialization start address (in words) ..`h0c
REFRESH_OFFSET=     0x10 # refresh start address (in words) ..`h13
WRITELEV_OFFSET=    0x20 # write leveling start address (in words) ..`h2a
    
READ_PATTERN_OFFSET=0x40 # read pattern to memory block sequence start address (in words) ..0x053 with 8x2*64 bits (variable)
WRITE_BLOCK_OFFSET= 0x100 # write block sequence start address (in words) ..0x14c
READ_BLOCK_OFFSET=  0x180 # read  block sequence start address (in words)

VERBOSE=True
def check_args(n,command,args):
    if len(args) != n:
        if n==0:
            print ("Error: command \"%s\" does not accept any arguments"%(command))
        elif n==1:
            print ("Error: command \"%s\" requires one argument"%(command))
        else:        
            print ("Error: command \"%s\" requires %d arguments"%(command,n))
        exit(1)
    return    
def axi_write_single(addr,data):
    write_mem(0x40000000+addr,data)

def axi_read_addr(addr):
    d= read_mem(0x40000000+addr)
    return d

def read_status(): #    task read_status;
    global BASEADDR_STATUS
    return axi_read_addr(BASEADDR_STATUS)

def wait_phase_shifter_ready(target_phase): #    task wait_phase_shifter_ready;
    global STATUS_PSHIFTER_RDY_MASK, PHASE_WIDTH,VERBOSE
    if (VERBOSE): print("wait_phase_shifter_ready(0x%x)..."%target_phase,end="")
    status = read_status()
    while ((status & STATUS_PSHIFTER_RDY_MASK) == 0) or ((status ^ target_phase) & ((1<<PHASE_WIDTH)-1) != 0):
        status=read_status()
    if (VERBOSE): print("DONE")

def wait_sequencer_ready(): #    task wait_sequencer_ready;
    global STATUS_SEQ_BUSY_MASK,VERBOSE
    if (VERBOSE): print("wait_sequencer_ready()...",end="")
#        input integer num_skip; #skip this cycles before testing ready (latency from write to busy)
#            repeat (num_skip) @(posedge CLK);
    status=read_status()
#            repeat (8) @(posedge CLK); # latency from read command to registered_rdata. TODO: make it certain (read with the same ID)
    while (status & STATUS_SEQ_BUSY_MASK) != 0:
        status= read_status()
    if (VERBOSE): print("DONE")

def run_sequence (channel,start_addr):
    global BASEADDR_RUN_CHN,VERBOSE
    if (VERBOSE): print("run_sequence(0x%x,0x%x)"%(channel,start_addr))
    axi_write_single(BASEADDR_RUN_CHN+(channel<<2), start_addr)

def run_mrs(): #    task run_mrs;
    global INITIALIZE_OFFSET, VERBOSE
    if (VERBOSE): print("RUN MRS")
    run_sequence(0,INITIALIZE_OFFSET)
    
def run_write_lev(): #     task run_write_lev;
    global WRITELEV_OFFSET, VERBOSE
    if (VERBOSE): print("RUN WRITE LEVELING")
    run_sequence(0,WRITELEV_OFFSET)

def run_read_pattern(): #     task run_read_pattern;
    global READ_PATTERN_OFFSET, VERBOSE
    if (VERBOSE): print("RUN READ PATTERN")
    run_sequence(0,READ_PATTERN_OFFSET)

def run_write_block(): #     task run_write_block;
    global WRITE_BLOCK_OFFSET, VERBOSE
    if (VERBOSE): print("RUN WRITE BLOCK")
    run_sequence(1,WRITE_BLOCK_OFFSET)

def run_read_block(): #     task run_read_block;
    global READ_BLOCK_OFFSET, VERBOSE
    if (VERBOSE): print("RUN READ BLOCK")
    run_sequence(0,READ_BLOCK_OFFSET)

    
def enable_cmda(en):
    global BASEADDR_CMDA_EN
    if en: 
        axi_write_single(BASEADDR_CMDA_EN+4, 0)
    else: 
        axi_write_single(BASEADDR_CMDA_EN, 0)

def enable_cke(en):
    global BASEADDR_CKE_EN
    if en: 
        axi_write_single(BASEADDR_CKE_EN+4, 0)
    else: 
        axi_write_single(BASEADDR_CKE_EN, 0)

def activate_sdrst(en):
    global BASEADDR_SDRST_ACT
    if en: 
        axi_write_single(BASEADDR_SDRST_ACT+4, 0)
    else: 
        axi_write_single(BASEADDR_SDRST_ACT, 0)

def enable_refresh(en):
    global BASEADDR_REFRESH_EN
    if en: 
        axi_write_single(BASEADDR_REFRESH_EN+4, 0)
    else: 
        axi_write_single(BASEADDR_REFRESH_EN, 0)

def write_block_buf():
    global BASEADDR_PORT1_WR, VERBOSE
    if (VERBOSE): print("WRITE BLOCK DATA")

    for i in range(256):
        d=i | (((i + 7) & 0xff) << 8) | (((i + 23) & 0xff) << 16) | (((i + 31) & 0xff) << 24)
        axi_write_single(BASEADDR_PORT1_WR+(i<<2), d)
#        if (VERBOSE): print("Write block data (addr:data): 0x%x:0x%x "%(BASEADDR_PORT1_WR+(i<<2),d))

def read_block_buf(
      num_read ): #input integer num_read; // number of words to read (will be rounded up to multiple of 16)
    global BASEADDR_PORT0_RD, VERBOSE
    buf=[]
    for i in range(num_read):
        d=axi_read_addr(BASEADDR_PORT0_RD+(i<<2))
        buf.append(d)
        if (VERBOSE): print("Read block data (addr:data): 0x%x:0x%x "%(BASEADDR_PORT0_RD+(i<<2),d))
    return buf    
def read_buf(
      num_read ): #input integer num_read; // number of words to read (will be rounded up to multiple of 16)
    global BASEADDR_PORT0_RD, VERBOSE;
    buf=[]
    for i in range(num_read):
        d=axi_read_addr(BASEADDR_PORT0_RD+(i<<2))
        buf.append(d)
    if (VERBOSE):         
        for i in range(num_read):
            addr= i<<2;
            if (i%8) == 0:
                print ("\n%08x: "%addr,end="")
            print ("%08x "%buf[i],end="")
        print ()
    return buf
 
def encode_seq_word(
        phy_addr_in,       # [14:0] also provides pause length when the command is NOP
        phy_bank_in,       # [ 2:0] bank address 
        phy_rcw_in,        # [ 2:0] {ras,cas,we}
        phy_odt_in,        # may be optimized?
        phy_cke_inv,       # invert CKE 
        phy_sel_in,        # first/second half-cycle, other will be nop (cke+odt applicable to both)
        phy_dq_en_in,
        phy_dqs_en_in,
        phy_dqs_toggle_en, # enable toggle DQS according to the pattern
        phy_dci_en_in,     # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
        phy_buf_wr,        # connect to external buffer
        phy_buf_rd,        # connect to external buffer
        add_nop):          # add NOP after the current command, keep other data
    return (
            ((phy_addr_in & 0x7ffff) << 17) | # phy_addr_in[14:0]   
            ((phy_bank_in &     0x7) << 14) | # phy_bank_in[2:0],
            ((phy_rcw_in &      0x7) << 11) | # phy_rcw_in[2:0], # {ras,cas,we}, positive logic (3'b0 - NOP)
            ((phy_odt_in &      0x1) << 10) | # phy_odt_in
            ((phy_cke_inv &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((phy_sel_in &      0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((phy_dq_en_in &    0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((phy_dqs_en_in &   0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((phy_dqs_toggle_en&0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            ((phy_dci_en_in &   0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((phy_buf_wr &      0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((phy_buf_rd &      0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((add_nop &         0x1) <<  1) | # add_nop    # add NOP after the current command, keep other data
            0)                                # Reserved for future use
    
def encode_seq_skip(
        skip,              # [CMD_PAUSE_BITS-1:0] - number of skip cycles in additiona to 1 (0 - 1 cycle, 1 - 2, ...)
        done,              # 1 - end of sequence
        dci_en,            # enable DCI
        odt_en):           # enavble ODT
    global CMD_DONE_BIT,CMD_PAUSE_BITS
    return (
            ((done & 1) << (CMD_DONE_BIT+17)) |         # 14-CMD_DONE_BIT{1'b0}},
            ((skip & ((1<< CMD_PAUSE_BITS)-1)) << 17) | # skip[CMD_PAUSE_BITS-1:0]
#            3'b0, #phy_bank_in[2:0],
#            3'b0, # phy_rcw_in[2:0],      # {ras,cas,we}
             ((odt_en &      0x1) << 10) | # odt_en, # phy_odt_in,
#            1'b0, # phy_cke_in,      # may be optimized?
#            1'b0, # phy_sel_in,      # first/second half-cycle, other will be nop (cke+odt applicable to both)
#            1'b0, # phy_dq_en_in, #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
#            1'b0, # phy_dqs_en_in, #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
#            1'b0, #enable toggle DQS according to the pattern
            ((dci_en &   0x1) <<  4)  # dci_en, # phy_dci_en_in, #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
#            1'b0, # phy_buf_wr,   # connect to external buffer (but only if not paused)
#            1'b0, # phy_buf_rd,    # connect to external buffer (but only if not paused)
#            1'b0, # add NOP after the current command, keep other data
#            1'b0  # Reserved for future use
           )

  # Set MR3, read nrep*8 words, save to buffer (port0). No ACTIVATE/PRECHARGE are needed/allowed
def set_read_pattern( #    task set_read_pattern;
        nrep, # input integer nrep;
        npat, #trying pattern type (only 0 defined)
        scnd):#adjusting first/seccond 
#        reg   [31:0] cmd_addr;
#        reg   [31:0] data;
#        reg                 [17:0] mr3_norm;
#        reg                 [17:0] mr3_pattern;
#        integer i;
    global BASEADDR_CMD0, READ_PATTERN_OFFSET
    cmd_addr = BASEADDR_CMD0 + (READ_PATTERN_OFFSET << 2)
    mr3_norm = ddr3_mr3 (
                0, #1'h0,     #       mpr;    # MPR mode: 0 - normal, 1 - dataflow from MPR
                0) # 2'h0)    # [1:0] mpr_rf; # MPR read function: 2'b00: predefined pattern 0101...
    mr3_pattern = ddr3_mr3 (
                1, # 1'h1,     #       mpr;    # MPR mode: 0 - normal, 1 - dataflow from MPR
                npat & 3) # 2'h0)    # [1:0] mpr_rf; # MPR read function: 2'b00: predefined pattern 0101...

# Set pattern mode
    data =  encode_seq_word(
                mr3_pattern & 0x7fff,      # mr3[14:0],      # [14:0] phy_addr_in;
                (mr3_pattern >> 15) & 0x7, # mr3[17:15],     # [ 2:0] phy_bank_in; #TODO: debug!
                7,                 # 3'b111,                 # [ 2:0] phy_rcw_in; # {ras,cas,we}, positive
                0,                 # 1'b0,                   #        phy_odt_in; # may be optimized?
                0,                 # 1'b0,                   # phy_cke_inv; # may be optimized?
                0,                 # 1'b0,                   # phy_sel_in; # first/second half-cycle, other will be nop (cke+odt applicable to both)
                0,                 # 1'b0,                   # phy_dq_en_in;
                0,                 # 1'b0,                   # phy_dqs_en_in;
                0,                 # 1'b0,                   # phy_dqs_toggle_en;
                0,                 # 1'b0,                   # phy_dci_en_in;      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
                0,                 # 1'b0,                   # phy_buf_wr;   # connect to external buffer
                0,                 # 1'b0,                   # phy_buf_rd;   # connect to external buffer
                0)                 # 1'b0)                   # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
#    data = encode_seq_skip(5,0,0,0) # tMOD
    data = encode_seq_skip(5,0,1,0) # tMOD Early DCI
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# first read
# read
    data = (
            ((0 &   0x3ff) << 17) | # ra[14:0]
            ((0 &     0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x2 &   0x7) << 11) | # 3'b010, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((scnd &  0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# nop
    data = (
            ((0 &  0x7fff) << 17) | # ra[14:0]
            ((0 &     0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            (( 1 &    0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
#repeat remaining reads
    for i in range (1,nrep): # for (i=1;i<nrep;i=i+1) begin
# read
        data = (
                ((0 &   0x3ff) << 17) | # cra[9:0]
                ((0 &     0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
                ((0x2 &   0x7) << 11) | # 3'b010, # phy_rcw_in[2:0],      # {ras,cas,we}
                ((0 &     0x1) << 10) | # phy_odt_in
                ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
                ((scnd &  0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
                ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
                ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
                ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
                (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
                (( 1 &    0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
                ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
                (( 1 &    0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
        axi_write_single(cmd_addr, data)
        cmd_addr = cmd_addr + 4
# nop
    data = (
            ((0 &  0x7fff) << 17) | # ra[14:0]
            ((0 &     0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            (( 1 &    0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# nop
    data = (
            ((0 &  0x7fff) << 17) | # ra[14:0]
            ((0 &     0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            (( 1 &    0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# nop
    data = (
            ((0 &  0x7fff) << 17) | # ra[14:0]
            ((0 &     0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            (( 1 &    0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
#            (( 1 &    0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &    0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

    data = encode_seq_skip(2,0,1,0) # keep dci enabled
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

# Turn off read pattern mode
    data =  encode_seq_word(
                mr3_norm & 0x7fff,      # mr3[14:0],         # [14:0] phy_addr_in;
                (mr3_norm >> 15) & 0x7, # mr3[17:15],        # [ 2:0] phy_bank_in; #TODO: debug!
                7,                 # 3'b111,                 # [ 2:0] phy_rcw_in; # {ras,cas,we}, positive
                0,                 # 1'b0,                   #        phy_odt_in; # may be optimized?
                0,                 # 1'b0,                   # phy_cke_inv; # may be optimized?
                0,                 # 1'b0,                   # phy_sel_in; # first/second half-cycle, other will be nop (cke+odt applicable to both)
                0,                 # 1'b0,                   # phy_dq_en_in;
                0,                 # 1'b0,                   # phy_dqs_en_in;
                0,                 # 1'b0,                   # phy_dqs_toggle_en;
                1,                 # 1'b1,                   # phy_dci_en_in;
                0,                 # 1'b0,                   # phy_buf_wr;   # connect to external buffer
                0,                 # 1'b0,                   # phy_buf_rd;   # connect to external buffer
                0)                 # 1'b0)                   # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

    data = encode_seq_skip(5,0,1,0 ) # tMOD (keep DCI enabled)
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# Turn off DCI
    data = (
            ((0 &  0x7fff) << 17) | # ra[14:0]
            ((0 &     0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            ((0 &     0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

    data = encode_seq_skip(0,1,0,0) # end of sequence (no dci, no odt)
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

    
def set_read_block(
        ba,        # [ 2:0] bank address
        ra,        # [14:0] row address
        ca,        # [ 9:0] column address
        scnd):     # use second (delayed) clock for read command
#        cmd_addr,  # command address (bit 10 - auto/manual banks)
#        data):     # [31:0] - command data
    global BASEADDR_CMD0, READ_BLOCK_OFFSET
#        integer i;
    cmd_addr = BASEADDR_CMD0 + (READ_BLOCK_OFFSET << 2)
# activate             
    data = ( 
            ((ra & 0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x4 &   0x7) << 11) | # 3'b100, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            ((0 &     0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# see if pause is needed . See when buffer read should be started - maybe before WR command
#    data = encode_seq_skip(1,0,0,0)
    data = encode_seq_skip(1,0,1,0) #early DCI enable
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# first read
# read
    data = ( 
            ((ca &  0x3ff) << 17) | # ca[9:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x2 &   0x7) << 11) | # 3'b010, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((scnd &  0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# nop
    data = ( 
            ((0 &  0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((scnd &  0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
#repeat remaining reads             
    for i in range (1,64):
# read             
        data = ( 
                (((ca  + (i<<3)) &  0x3ff) << 17) | # {5'b0,ca[9:0]} + (i<<3), 
                ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
                ((0x2 &   0x7) << 11) | # 3'b010, # phy_rcw_in[2:0],      # {ras,cas,we}
                ((0 &     0x1) << 10) | # phy_odt_in
                ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
                ((scnd &  0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
                ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
                ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
                ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
                (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
                (( 1 &    0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
                ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
                (( 1 &    0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
        axi_write_single(cmd_addr, data)
        cmd_addr = cmd_addr + 4
# nop
    data = ( 
            ((0 &  0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((scnd &  0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# nop
    data = ( 
            ((0 &  0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((scnd &  0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# nop
    data = ( 
            ((0 &  0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((scnd &  0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
    # tRTP = 4*tCK is already satisfied, no skip here
# precharge
    data = ( 
            ((ra & 0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x5 &   0x7) << 11) | # 3'b101, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

    data = encode_seq_skip(2,0,1,0) # keep DCI 
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

    data = encode_seq_skip(0,1,0,0) # end of sequence . TODO: verify DCI is disabled here - yes, OK 
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4



def set_write_block(
        ba, # input [ 2:0] ba;
        ra, # input [14:0] ra;
        ca): # input [ 9:0] ca;
#        reg   [31:0] cmd_addr;
#        reg   [31:0] data;
#        integer i;

    global BASEADDR_CMD0, WRITE_BLOCK_OFFSET,VERBOSE
    if (VERBOSE): print("set_write_block(0x%x,0x%x,0x%x"%(ba,ra,ca))
    cmd_addr = BASEADDR_CMD0 + (WRITE_BLOCK_OFFSET << 2)
# activate
    data = ( 
            ((ra & 0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x4 &   0x7) << 11) | # 3'b100, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            ((0 &     0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# see if pause is needed . See when buffer read should be started - maybe before WR command
#    data = encode_seq_skip(1,0,0,0) # tRCD
    data = encode_seq_skip(2,0,0,0) # tRCD
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# first write
# write
    data = ( 
            ((ca &  0x3ff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x3 &   0x7) << 11) | # 3'b011, # phy_rcw_in[2:0],      # {ras,cas,we}
            (( 1 &    0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
#            (( 1 &    0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
#            ((0  &    0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            (( 1 &    0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            ((0 &     0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
#            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
#            (( 1 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# nop
    data = ( 
            ((0 &  0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            (( 1 &    0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            (( 1 &    0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            ((0 &     0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            (( 1 &    0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
             
#repeat remaining writes
    for i in range (1,64):
# write             
        data = ( 
                (((ca  + (i<<3)) &  0x3ff) << 17) | # {5'b0,ca[9:0]} + (i<<3), 
                ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
                ((0x3 &   0x7) << 11) | # 3'b011, # phy_rcw_in[2:0],      # {ras,cas,we}
                (( 1 &    0x1) << 10) | # phy_odt_in
                ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
#                (( 1 &    0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
#                (( 0 &    0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
                (( 1 &    0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
                (( 1 &    0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
                (( 1 &    0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
                (( 1 &    0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
                ((0 &     0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
                ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
                (( 1 &    0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
                (( 1 &    0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
        axi_write_single(cmd_addr, data)
        cmd_addr = cmd_addr + 4
# nop
    data = ( 
            ((0 &  0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            (( 1 &    0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            (( 1 &    0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            ((0 &     0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            (( 1 &    0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# nop
    data = ( 
            ((0 &  0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            (( 1 &    0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            (( 1 &    0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            ((0 &     0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
#            (( 1 &    0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
#            (( 0 &    0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
#this is one extra read, needed because of BRAM latency
            (( 1 &    0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# nop
    data = ( 
            ((0 &  0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x0 &   0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            (( 1 &    0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            (( 1 &    0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            ((0 &     0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# ODT off, it has latency
    data = encode_seq_skip(2,0,0,0) # tWR = 15ns (6 cycles for 2.5ns) from end of write (not write command)
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# precharge, ODT off
    data = ( 
            ((ra & 0x7fff) << 17) | # ra[14:0]   
            ((ba &    0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0x5 &   0x7) << 11) | # 3'b101, # phy_rcw_in[2:0],      # {ras,cas,we}
            ((0 &     0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            ((0 &     0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

    data = encode_seq_skip(2,0,0,0) # 
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

    data = encode_seq_skip(0,1,0,0) # end of sequence 
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4


def ddr3_mr0(  #    function [ADDRESS_NUMBER+2:0] ddr3_mr0;
        pd,    # input       pd; # precharge power down 0 - dll off (slow exit), 1 - dll on (fast exit) 
        wr,    # input [2:0] wr; # write recovery:
                        # 3'b000: 16
                        # 3'b001:  5
                        # 3'b010:  6
                        # 3'b011:  7
                        # 3'b100:  8
                        # 3'b101: 10
                        # 3'b110: 12
                        # 3'b111: 14
        dll_rst, # input       dll_rst; # 1 - dll reset (self clearing bit)
        cl,      # input [3:0] cl; # CAS latency (>=15ns):
                        # 0000: reserved                   
                        # 0010:  5                   
                        # 0100:  6                   
                        # 0110:  7                 
                        # 1000:  8                 
                        # 1010:  9                 
                        # 1100: 10                   
                        # 1110: 11                   
                        # 0001: 12                  
                        # 0011: 13                  
                        # 0101: 14
        bt,      # input       bt; # read burst type: 0 sequential (nibble), 1 - interleaved
        bl):     #input [1:0] bl; # burst length:
                        # 2'b00 - fixed BL8
                        # 2'b01 - 4 or 8 on-the-fly by A12                                     
                        # 2'b10 - fixed BL4 (chop)
                        # 2'b11 - reserved
    global ADDRESS_NUMBER              
    return (
         # 3'b0,
         # {ADDRESS_NUMBER-13{1'b0}},
         ((pd & 1) << 12) |     # pd,       # MR0.12 
         ((wr & 7) <<  9) |     # wr,       # MR0.11_9
         ((dll_rst & 1) << 8) | # dll_rst,  # MR0.8
         (0        <<  7) |     # 1'b0,     # MR0.7
         (((cl >>1) & 7)<< 4) | # cl[3:1],  # MR0.6_4
         ((bt & 1) << 3) |      # bt,       # MR0.3
         ((cl & 1) << 2) |      # cl[0],    # MR0.2
         ((bl & 3) << 0))       #  bl[1:0]}; # MR0.1_0
    
def ddr3_mr1( #    function [ADDRESS_NUMBER+2:0] ddr3_mr1;
        qoff, # input       qoff; # output enable: 0 - DQ, DQS operate in normal mode, 1 - DQ, DQS are disabled
        tdqs, #input       tdqs; # termination data strobe (for x8 devices) 0 - disabled, 1 - enabled
        rtt,  #input [2:0] rtt;  # on-die termination resistance:
                          #  3'b000 - disabled
                          #  3'b001 - RZQ/4 (60 Ohm)
                          #  3'b010 - RZQ/2 (120 Ohm)
                          #  3'b011 - RZQ/6 (40 Ohm)
                          #  3'b100 - RZQ/12(20 Ohm)
                          #  3'b101 - RZQ/8 (30 Ohm)
                          #  3'b11x - reserved
        wlev, #input       wlev; # write leveling
        ods,  #input [1:0] ods;  # output drive strength:
                          #  2'b00 - RZQ/6 - 40 Ohm
                          #  2'b01 - RZQ/7 - 34 Ohm
                          #  2'b1x - reserved
        al,   #input [1:0] al;   # additive latency:
                          #  2'b00 - disabled (AL=0)
                          #  2'b01 - AL=CL-1;
                          #  2'b10 - AL=CL-2
                          #  2'b11 - reserved
        dll): #input       dll;  # 0 - DLL enabled (normal), 1 - DLL disabled
    global ADDRESS_NUMBER              
    return ( #            ddr3_mr1 = {
         1 << ADDRESS_NUMBER |#     3'h1,
         #     {ADDRESS_NUMBER-13{1'b0}},
         ((qoff & 1) << 12) |      # qoff,       # MR1.12 
         ((tdqs & 1) << 11) |      # tdqs,       # MR1.11
         #     1'b0,       # MR1.10
         (((rtt >> 2) & 1) << 9) | #     rtt[2],     # MR1.9
         #     1'b0,       # MR1.8
         ((wlev & 1) << 7) |       # wlev,       # MR1.7 
         (((rtt >> 1) & 1) << 6) | # rtt[1],     # MR1.6 
         (((ods >> 1) & 1) << 5) | # ods[1],     # MR1.5 
         ((al & 3) << 3) |         # al[1:0],    # MR1.4_3 
         ((rtt & 1) <<2) |         # rtt[0],     # MR1.2 
         ((ods & 1) <<1) |         # ods[0],     # MR1.1 
         (( dll &1) << 0))         #     dll};       # MR1.0 

def ddr3_mr2( #    function [ADDRESS_NUMBER+2:0] ddr3_mr2;
        rtt_wr, # input [1:0] rtt_wr; # Dynamic ODT :
                            #  2'b00 - disabled
                            #  2'b01 - RZQ/4 = 60 Ohm
                            #  2'b10 - RZQ/2 = 120 Ohm
                            #  2'b11 - reserved
        srt,    # input       srt;    # Self-refresh temperature 0 - normal (0-85C), 1 - extended (<=95C)
        asr,    # input       asr;    # Auto self-refresh 0 - disabled (manual), 1 - enabled (auto)
        cwl):    # input [2:0] cwl;    # CAS write latency:
                            #  3'b000  5CK (           tCK >= 2.5ns)  
                            #  3'b001  6CK (1.875ns <= tCK < 2.5ns)  
                            #  3'b010  7CK (1.5ns   <= tCK < 1.875ns)  
                            #  3'b011  8CK (1.25ns  <= tCK < 1.5ns)  
                            #  3'b100  9CK (1.071ns <= tCK < 1.25ns)  
                            #  3'b101 10CK (0.938ns <= tCK < 1.071ns)  
                            #  3'b11x reserved  
    global ADDRESS_NUMBER              
    return ( #ddr3_mr2 = {
         0x2 << ADDRESS_NUMBER | #     3'h2,
         #     {ADDRESS_NUMBER-11{1'b0}},
         ((rtt_wr & 3) << 9) | #     rtt_wr[1:0], # MR2.10_9
         #     1'b0,        # MR2.8
         ((srt & 1) << 7) | #     srt,         # MR2.7
         ((asr & 1) << 6) | #     asr,         # MR2.6
         ((cwl & 7) << 3) | #     cwl[2:0],    # MR2.5_3
         0)                 #     3'b0};       # MR2.2_0 
        
def ddr3_mr3( #    function [ADDRESS_NUMBER+2:0] ddr3_mr3;
        mpr,     # input       mpr;    # MPR mode: 0 - normal, 1 - dataflow from MPR
        mpr_rf): # input [1:0] mpr_rf; # MPR read function:
                            #  2'b00: predefined pattern 0101...
                            #  2'b1x, 2'bx1 - reserved
    global ADDRESS_NUMBER              
    return ( #        ddr3_mr3 = {
         0x3 << ADDRESS_NUMBER | #     3'h3,
         #     {ADDRESS_NUMBER-3{1'b0}},
         ((mpr & 1) << 2) |  #     mpr,          # MR3.2
         ((mpr_rf & 3) <<0)) #     mpr_rf[1:0]}; # MR3.1_0 


def set_write_lev(
        nrep ): # input [CMD_PAUSE_BITS-1:0] nrep;
#        reg                 [17:0] mr1_norm;
#        reg                 [17:0] mr1_wlev;
#        reg                 [31:0] cmd_addr;
#        reg                 [31:0] data;
#        reg   [CMD_PAUSE_BITS-1:0] dqs_low_rpt;
#        reg   [CMD_PAUSE_BITS-1:0] nrep_minus_1;
    global BASEADDR_CMD0, WRITELEV_OFFSET,CMD_DONE_BIT,CMD_PAUSE_BITS
    dqs_low_rpt = 8
    nrep_minus_1 = nrep-1;
    mr1_norm = ddr3_mr1(
          0, #      1'h0,     #       qoff; # output enable: 0 - DQ, DQS operate in normal mode, 1 - DQ, DQS are disabled
          0, #      1'h0,     #       tdqs; # termination data strobe (for x8 devices) 0 - disabled, 1 - enabled
          2, #      3'h2,     # [2:0] rtt;  # on-die termination resistance: #  3'b010 - RZQ/2 (120 Ohm)
          0, #      1'h0,     #       wlev; # write leveling
          0, #      2'h0,     #       ods;  # output drive strength: #  2'b00 - RZQ/6 - 40 Ohm
          0, #      2'h0,     # [1:0] al;   # additive latency: 2'b00 - disabled (AL=0)
          0) #      1'b0)    #       dll;  # 0 - DLL enabled (normal), 1 - DLL disabled
    mr1_wlev = ddr3_mr1(
          0, #      1'h0,     #       qoff; # output enable: 0 - DQ, DQS operate in normal mode, 1 - DQ, DQS are disabled
          0, #      1'h0,     #       tdqs; # termination data strobe (for x8 devices) 0 - disabled, 1 - enabled
          2, #      3'h2,     # [2:0] rtt;  # on-die termination resistance: #  3'b010 - RZQ/2 (120 Ohm)
          1, #      1'h1,     #       wlev; # write leveling
          0, #      2'h0,     #       ods;  # output drive strength: #  2'b00 - RZQ/6 - 40 Ohm
          0, #      2'h0,     # [1:0] al;   # additive latency: 2'b00 - disabled (AL=0)
          0) #      1'b0)    #       dll;  # 0 - DLL enabled (normal), 1 - DLL disabled
    cmd_addr = BASEADDR_CMD0 + (WRITELEV_OFFSET<<2)
# Enter write leveling mode
    data =  encode_seq_word(
             mr1_wlev & 0x7fff,      #  mr1_wlev[14:0],              # [14:0] phy_addr_in;
             (mr1_wlev >> 15) & 0x7, #  mr1_wlev[17:15],             # [ 2:0] phy_bank_in; #TODO: debug!
             7,                      #  3'b111,                      # [ 2:0] phy_rcw_in; # {ras,cas,we}, positive
             0, #   1'b0,                        #        phy_odt_in; # may be optimized?
             0, #   1'b0,                        # phy_cke_inv; # may be optimized?
             0, #   1'b0,                        # phy_sel_in == 0; # first/second half-cycle,
             0, #   1'b0,                        # phy_dq_en_in;
             0, #   1'b0,                        # phy_dqs_en_in;
             0, #   1'b0,                        # phy_dqs_toggle_en;
             0, #   1'b0,                        # phy_dci_en_in;      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
             0, #   1'b0,                        # phy_buf_wr;   # connect to external buffer
             0, #   1'b0,                        # phy_buf_rd;   # connect to external buffer
             0) #   1'b0)                       # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
    data = encode_seq_skip(13,0,0,0) # tWLDQSEN=25tCK 
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# enable DQS output, keep it low (15 more tCK for the total of 40 tCK
               
    data = ( # encode_seq_skip(nrep,0) # Adjust skip
            ((dqs_low_rpt & ((1<< CMD_PAUSE_BITS)-1)) << 17) | #  dqs_low_rpt, # 16 tCK
            ((0 &     0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0 &     0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            (( 1 &    0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            ((0 &     0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# Toggle DQS as needed for write leveling, write to buffer             
    data = (
            ((nrep_minus_1 & ((1<< CMD_PAUSE_BITS)-1)) << 17) | #  dqs_low_rpt, # 16 tCK
            ((0 &     0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0 &     0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            (( 1 &    0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# continue toggling, but disable writing to buffer (used same wbuf latency as for read)
    data = (
            ((4 & ((1<< CMD_PAUSE_BITS)-1)) << 17) | # 4 cycles
            ((0 &     0x7) << 14) | # ba[2:0], #phy_bank_in[2:0],
            ((0 &     0x7) << 11) | # 3'b000, # phy_rcw_in[2:0],      # {ras,cas,we}
            (( 1 &    0x1) << 10) | # phy_odt_in
            ((0 &     0x1) <<  9) | # phy_cke_inv   # invert CKE
            ((0 &     0x1) <<  8) | # phy_sel_in   # first/second half-cycle, other will be nop (cke+odt applicable to both)
            ((0 &     0x1) <<  7) | # phy_dq_en_in #phy_dq_tri_in,   # tristate DQ  lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  6) | # phy_dqs_en_in #phy_dqs_tri_in,  # tristate DQS lines (internal timing sequencer for 0->1 and 1->0)
            (( 1 &    0x1) <<  5) | # phy_dqs_toggle_en #enable toggle DQS according to the pattern
            (( 1 &    0x1) <<  4) | # phy_dci_en_in  #phy_dci_in,      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
            ((0 &     0x1) <<  3) | # phy_buf_wr # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  2) | # phy_buf_rd # connect to external buffer (but only if not paused)
            ((0 &     0x1) <<  1))  # add_nop    # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
#             
    data = encode_seq_skip(2,0,1,0) # Keep DCI (but not ODT) active  ODT should be off befor MRS
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
 # exit write leveling mode, ODT off, DCI off               
    data =  encode_seq_word(
             mr1_norm & 0x7fff,      #  mr1_wlev[14:0],              # [14:0] phy_addr_in;
             (mr1_norm >> 15) & 0x7, #  mr1_wlev[17:15],             # [ 2:0] phy_bank_in; #TODO: debug!
             7,                      #  3'b111,                      # [ 2:0] phy_rcw_in; # {ras,cas,we}, positive
             0, #   1'b0,                        #        phy_odt_in; # may be optimized?
             0, #   1'b0,                        # phy_cke_inv; # may be optimized?
             0, #   1'b0,                        # phy_sel_in == 0; # first/second half-cycle,
             0, #   1'b0,                        # phy_dq_en_in;
             0, #   1'b0,                        # phy_dqs_en_in;
             0, #   1'b0,                        # phy_dqs_toggle_en;
             0, #   1'b0,                        # phy_dci_en_in;      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
             0, #   1'b0,                        # phy_buf_wr;   # connect to external buffer
             0, #   1'b0,                        # phy_buf_rd;   # connect to external buffer
             0) #   1'b0)                       # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
 
    data = encode_seq_skip(5,0,0,0) # tMOD
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# Ready for normal operation
    data = encode_seq_skip(10,1,0,0) # sequence done bit, skip length is ignored
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

def set_refresh( #     task set_refresh;
        t_rfc,    # input [ 9:0] t_rfc; # =50 for tCK=2.5ns
        t_refi):  #input [ 7:0] t_refi; # 48/97 for normal, 8 - for simulation
    global BASEADDR_CMD0,REFRESH_OFFSET,BASEADDR_REFRESH_ADDR, BASEADDR_REFRESH_PER
#        reg [31:0] cmd_addr;
#        reg [31:0] data;
    cmd_addr = BASEADDR_CMD0 + (REFRESH_OFFSET<<2)
    data =  encode_seq_word(
             0, #   15'h0,              # [14:0] phy_addr_in;
             0, #   3'b0,               # [ 2:0] phy_bank_in; #TODO: debug!
             6, #   3'b110,             # [ 2:0] phy_rcw_in; # {ras,cas,we}, positive
             0, #   1'b0,               #        phy_odt_in; # may be optimized?
             0, #   1'b0,               # phy_cke_inv; # may be optimized?
             0, #   1'b0,               # phy_sel_in == 0; # first/second half-cycle,
             0, #   1'b0,               # phy_dq_en_in;
             0, #   1'b0,               # phy_dqs_en_in;
             0, #   1'b0,               # phy_dqs_toggle_en;
             0, #   1'b0,               # phy_dci_en_in;      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
             0, #   1'b0,               # phy_buf_wr;   # connect to external buffer
             0, #   1'b0,               # phy_buf_rd;   # connect to external buffer
             0) #   1'b0)               # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
    data = encode_seq_skip(t_rfc,0,0,0) # =50 tREFI=260 ns before next ACTIVATE or REFRESH, @2.5ns clock, @5ns cycle
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# Ready for normal operation
    data = encode_seq_skip(0,1,0,0) # sequence done bit, skip length is ignored
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
    axi_write_single(BASEADDR_REFRESH_ADDR, REFRESH_OFFSET)
    axi_write_single(BASEADDR_REFRESH_PER, t_refi)

def set_mrs( #    task set_mrs; # will also calibrate ZQ
        reset_dll, # input reset_dll;
        cl): #CAS latency code: 2 - 5, 4 - 6, 6 - 7
    global BASEADDR_CMD0, VERBOSE
        # reg [17:0] mr0;
        # reg [17:0] mr1;
        # reg [17:0] mr2;
        # reg [17:0] mr3;
        # reg [31:0] cmd_addr;
        # reg [31:0] data;
    mr0 = ddr3_mr0 (
             0,         #  1'h0,      #       pd; # precharge power down 0 - dll off (slow exit), 1 - dll on (fast exit)
             2,         #  3'h2,      # [2:0] wr; # write recovery (encode ceil(tWR/tCK)) # 3'b010:  6
             reset_dll, #       dll_rst; # 1 - dll reset (self clearing bit)
             cl & 0x0f, # 4,         #  4'h4,      # [3:0] cl; # CAS latency: # 0100:  6 (time 15ns)
             0,         #  1'h0,      #       bt; # read burst type: 0 sequential (nibble), 1 - interleave
             0)         #  2'h0)       # [1:0] bl; # burst length: # 2'b00 - fixed BL8

    mr1 = ddr3_mr1 (
             0, #   1'h0,     #       qoff; # output enable: 0 - DQ, DQS operate in normal mode, 1 - DQ, DQS are disabled
             0, #   1'h0,     #       tdqs; # termination data strobe (for x8 devices) 0 - disabled, 1 - enabled
             2, #   3'h2,     # [2:0] rtt;  # on-die termination resistance: #  3'b010 - RZQ/2 (120 Ohm)
             0, #   1'h0,     #       wlev; # write leveling
             0, #   2'h0,     #       ods;  # output drive strength: #  2'b00 - RZQ/6 - 40 Ohm
             0, #   2'h0,     # [1:0] al;   # additive latency: 2'b00 - disabled (AL=0)
             0) #   1'b0)     #       dll;  # 0 - DLL enabled (normal), 1 - DLL disabled

    mr2 = ddr3_mr2 (
             0, #   2'h0,     # [1:0] rtt_wr; # Dynamic ODT : #  2'b00 - disabled, 2'b01 - RZQ/4 = 60 Ohm, 2'b10 - RZQ/2 = 120 Ohm
             0, #   1'h0,     #       srt;    # Self-refresh temperature 0 - normal (0-85C), 1 - extended (<=95C)
             0, #   1'h0,     #       asr;    # Auto self-refresh 0 - disabled (manual), 1 - enabled (auto)
             0) #   3'h0)     # [2:0] cwl;    # CAS write latency:3'b000  5CK (tCK >= 2.5ns), 3'b001  6CK (1.875ns <= tCK < 2.5ns)

    mr3 = ddr3_mr3 (
             0, #    1'h0,     #       mpr;    # MPR mode: 0 - normal, 1 - dataflow from MPR
             0) #    2'h0)    # [1:0] mpr_rf; # MPR read function: 2'b00: predefined pattern 0101...
    cmd_addr = BASEADDR_CMD0;
    if (VERBOSE): print("mr0=0x%x"%mr0)
    if (VERBOSE): print("mr1=0x%x"%mr1)
    if (VERBOSE): print("mr2=0x%x"%mr2)
    if (VERBOSE): print("mr3=0x%x"%mr3)
    data =  encode_seq_word(
                mr2 & 0x7fff,      # mr2[14:0],              # [14:0] phy_addr_in;
                (mr2 >> 15) & 0x7, # mr2[17:15],             # [ 2:0] phy_bank_in; #TODO: debug!
                7,                 # 3'b111,                 # [ 2:0] phy_rcw_in; # {ras,cas,we}, positive
                0,                 # 1'b0,                   #        phy_odt_in; # may be optimized?
                0,                 # 1'b0,                   # phy_cke_inv; # may be optimized?
                0,                 # 1'b0,                   # phy_sel_in; # first/second half-cycle, other will be nop (cke+odt applicable to both)
                0,                 # 1'b0,                   # phy_dq_en_in;
                0,                 # 1'b0,                   # phy_dqs_en_in;
                0,                 # 1'b0,                   # phy_dqs_toggle_en;
                0,                 # 1'b0,                   # phy_dci_en_in;      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
                0,                 # 1'b0,                   # phy_buf_wr;   # connect to external buffer
                0,                 # 1'b0,                   # phy_buf_rd;   # connect to external buffer
                0)                 # 1'b0)                   # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
    data = encode_seq_skip(1,0,0,0)  # 6 cycles between mrs commands
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
    data =  encode_seq_word(
                mr3 & 0x7fff,      # mr3[14:0],              # [14:0] phy_addr_in;
                (mr3 >> 15) & 0x7, # mr3[17:15],             # [ 2:0] phy_bank_in; #TODO: debug!
                7,                 # 3'b111,                 # [ 2:0] phy_rcw_in; # {ras,cas,we}, positive
                0,                 # 1'b0,                   #        phy_odt_in; # may be optimized?
                0,                 # 1'b0,                   # phy_cke_inv; # may be optimized?
                0,                 # 1'b0,                   # phy_sel_in; # first/second half-cycle, other will be nop (cke+odt applicable to both)
                0,                 # 1'b0,                   # phy_dq_en_in;
                0,                 # 1'b0,                   # phy_dqs_en_in;
                0,                 # 1'b0,                   # phy_dqs_toggle_en;
                0,                 # 1'b0,                   # phy_dci_en_in;      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
                0,                 # 1'b0,                   # phy_buf_wr;   # connect to external buffer
                0,                 # 1'b0,                   # phy_buf_rd;   # connect to external buffer
                0)                 # 1'b0)                   # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
    data = encode_seq_skip(0,0,0,0) # 5 cycles between mrs commands (next command has phy_sel_in == 1)
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
    data =  encode_seq_word(
                mr1 & 0x7fff,      # mr1[14:0],              # [14:0] phy_addr_in;
                (mr1 >> 15) & 0x7, # mr1[17:15],             # [ 2:0] phy_bank_in; #TODO: debug!
                7,                 # 3'b111,                 # [ 2:0] phy_rcw_in; # {ras,cas,we}, positive
                0,                 # 1'b0,                   #        phy_odt_in; # may be optimized?
                0,                 # 1'b0,                   # phy_cke_inv; # may be optimized?
                1,  #just testing  # 1'b0,                   # phy_sel_in; # first/second half-cycle, other will be nop (cke+odt applicable to both)
                0,                 # 1'b0,                   # phy_dq_en_in;
                0,                 # 1'b0,                   # phy_dqs_en_in;
                0,                 # 1'b0,                   # phy_dqs_toggle_en;
                0,                 # 1'b0,                   # phy_dci_en_in;      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
                0,                 # 1'b0,                   # phy_buf_wr;   # connect to external buffer
                0,                 # 1'b0,                   # phy_buf_rd;   # connect to external buffer
                0)                 # 1'b0)                   # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
    data = encode_seq_skip(2,0,0,0) #  7 cycles between mrs commands ( prev. command had phy_sel_in == 1)
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
    data =  encode_seq_word(
                mr0 & 0x7fff,      # mr0[14:0],              # [14:0] phy_addr_in;
                (mr0 >> 15) & 0x7, # mr0[17:15],             # [ 2:0] phy_bank_in; #TODO: debug!
                7,                 # 3'b111,                 # [ 2:0] phy_rcw_in; # {ras,cas,we}, positive
                0,                 # 1'b0,                   #        phy_odt_in; # may be optimized?
                0,                 # 1'b0,                   # phy_cke_inv; # may be optimized?
                0,                 # 1'b0,                   # phy_sel_in; # first/second half-cycle, other will be nop (cke+odt applicable to both)
                0,                 # 1'b0,                   # phy_dq_en_in;
                0,                 # 1'b0,                   # phy_dqs_en_in;
                0,                 # 1'b0,                   # phy_dqs_toggle_en;
                0,                 # 1'b0,                   # phy_dci_en_in;      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
                0,                 # 1'b0,                   # phy_buf_wr;   # connect to external buffer
                0,                 # 1'b0,                   # phy_buf_rd;   # connect to external buffer
                0)                 # 1'b0)                   # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

    data = encode_seq_skip(5,0,0,0) # tMOD = 12 CK or 15ns, (tMOD/2)-1
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
    data =  encode_seq_word(
             0x400, # 15'h400,          # A10 == 1 -> ZQCL
             0,     #   3'h0,           # phy_bank_in;
             1,     #  3'b001,          # [ 2:0] phy_rcw_in; # {ras,cas,we}, positive - ZQC?
             0, #   1'b0,                        #        phy_odt_in; # may be optimized?
             0, #   1'b0,                        # phy_cke_inv; # may be optimized?
             0, #   1'b0,                        # phy_sel_in == 0; # first/second half-cycle,
             0, #   1'b0,                        # phy_dq_en_in;
             0, #   1'b0,                        # phy_dqs_en_in;
             0, #   1'b0,                        # phy_dqs_toggle_en;
             0, #   1'b0,                        # phy_dci_en_in;      # DCI disable, both DQ and DQS lines (internal logic and timing sequencer for 0->1 and 1->0)
             0, #   1'b0,                        # phy_buf_wr;   # connect to external buffer
             0, #   1'b0,                        # phy_buf_rd;   # connect to external buffer
             0) #   1'b0)                       # add NOP after the current command, keep other data
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4

    data = encode_seq_skip(256,0,0,0) # 512 clock cycles after ZQCL
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
# Ready for normal operation
    data = encode_seq_skip(10,1,0,0) # sequence done bit, skip length is ignored
    axi_write_single(cmd_addr, data)
    cmd_addr = cmd_addr + 4
#set tristate patterns
def axi_set_tristate_patterns(): #    task axi_set_tristate_patterns;
    global DQSTRI_LAST, DQSTRI_FIRST, DQTRI_LAST, DQTRI_FIRST, VERBOSE
    axi_write_single(BASEADDR_PATTERNS_TRI,
           ((DQSTRI_LAST & 0xff)  << 12) |
           ((DQSTRI_FIRST & 0xff) <<  8) |
           ((DQTRI_LAST & 0xff)   <<  4) |
           ((DQTRI_FIRST & 0xff)  <<  0))
    if (VERBOSE): print("SET TRISTATE PATTERNS")    


def axi_set_dqs_dqm_patterns(
                data): #    task axi_set_dqs_dqm_patterns; 0x0055
    global BASEADDR_PATTERNS, VERBOSE
 # set patterns for DM (always 0) and DQS - always the same (may try different for write lev.)        
    axi_write_single(BASEADDR_PATTERNS, data) #0x0055)
    if (VERBOSE): print("SET DQS+DQM PATTERNS")    


# initialize delays
def axi_set_delays(): #    task axi_set_delays;
    global BASEADDRESS_LANE0_ODELAY, DLY_LANE0_ODELAY
    global BASEADDRESS_LANE0_IDELAY, DLY_LANE0_IDELAY
    global BASEADDRESS_LANE1_ODELAY, DLY_LANE1_IDELAY
    global BASEADDRESS_LANE1_IDELAY, DLY_LANE1_IDELAY
    global BASEADDRESS_CMDA, BASEADDR_DLY_SET, DLY_PHASE
    for i in range(len(DLY_LANE0_ODELAY)):
        axi_write_single(BASEADDRESS_LANE0_ODELAY + (i<<2), DLY_LANE0_ODELAY[::-1][i] & 0xff) # reversed list 
    for i in range(len(DLY_LANE0_IDELAY)):
        axi_write_single(BASEADDRESS_LANE0_IDELAY + (i<<2), DLY_LANE0_IDELAY[::-1][i] & 0xff) # reversed list 
    for i in range(len(DLY_LANE1_ODELAY)):
        axi_write_single(BASEADDRESS_LANE1_ODELAY + (i<<2), DLY_LANE1_ODELAY[::-1][i] & 0xff) # reversed list 
    for i in range(len(DLY_LANE1_IDELAY)):
        axi_write_single(BASEADDRESS_LANE1_IDELAY + (i<<2), DLY_LANE1_IDELAY[::-1][i] & 0xff) # reversed list 
    for i in range(len(DLY_CMDA)):
        axi_write_single(BASEADDRESS_CMDA + (i<<2), DLY_CMDA[::-1][i] & 0xff) # reversed list 
    axi_write_single(BASEADDR_DLY_SET, 0) # set all dealys - remove after fixed axi_set_phase
    axi_set_phase(DLY_PHASE)
    
def axi_set_dqs_idelay_nominal(): #  task axi_set_dqs_idelay_nominal;
    global BASEADDRESS_LANE0_IDELAY, DLY_LANE0_IDELAY
    global BASEADDRESS_LANE1_IDELAY, DLY_LANE1_IDELAY
    i=8 
    axi_write_single(BASEADDRESS_LANE0_IDELAY + (i<<2), DLY_LANE0_IDELAY[::-1][i] & 0xff) # reversed list 
    axi_write_single(BASEADDRESS_LANE1_IDELAY + (i<<2), DLY_LANE1_IDELAY[::-1][i] & 0xff) # reversed list 
    axi_write_single(BASEADDR_DLY_SET, 0)

def axi_set_dqs_idelay_individual(dly0, dly1 ): #  task axi_set_dqs_idelay_nominal;
    global BASEADDRESS_LANE0_IDELAY, DLY_LANE0_IDELAY
    global BASEADDRESS_LANE1_IDELAY, DLY_LANE1_IDELAY
    i=8 
    axi_write_single(BASEADDRESS_LANE0_IDELAY + (i<<2), dly0 & 0xff) # reversed list 
    axi_write_single(BASEADDRESS_LANE1_IDELAY + (i<<2), dly1 & 0xff) # reversed list 
    axi_write_single(BASEADDR_DLY_SET, 0)

    
def axi_set_dqs_idelay_wlv(): #    task axi_set_dqs_idelay_wlv;
    global BASEADDRESS_LANE0_IDELAY, DLY_LANE0_DQS_WLV_IDELAY
    global BASEADDRESS_LANE1_IDELAY, DLY_LANE1_DQS_WLV_IDELAY
    i=8 
    axi_write_single(BASEADDRESS_LANE0_IDELAY + (i<<2), DLY_LANE0_DQS_WLV_IDELAY & 0xff) # reversed list 
    axi_write_single(BASEADDRESS_LANE1_IDELAY + (i<<2), DLY_LANE1_DQS_WLV_IDELAY & 0xff) # reversed list 
    axi_write_single(BASEADDR_DLY_SET, 0)
    
    
def axi_set_dly_single( #  task axi_set_dly_single;
                        
        group, # input [2:0] group; # 0 - lane 0 odelay, 1 - lane0 idelay, 2 - lane 1  odelay, 3 - lane1 idelay, 4 - cmda odelay
        index, # input [4:0] index; # 0..7 - DQ, 8 - DQS, 9 DQM (for byte lanes)
        delay): # input [7:0] delay;
#        integer i;
#        integer dly;
    global BASEADDRESS_LANE0_ODELAY
    global BASEADDRESS_LANE0_IDELAY
    global BASEADDRESS_LANE1_ODELAY
    global BASEADDRESS_LANE1_IDELAY
    global BASEADDRESS_CMDA
    global BASEADDRESS_LANE0_IDELAY,BASEADDRESS_LANE1_IDELAY, VERBOSE
    if (VERBOSE): print("SET DELAY (0x%x, 0x%0x, 0x%0x)"%(group,index,delay))
    i = index
    dly = delay
    if   group == 0:
        axi_write_single(BASEADDRESS_LANE0_ODELAY + (i<<2), dly & 0xff)
    elif group == 1:
        axi_write_single(BASEADDRESS_LANE0_IDELAY + (i<<2), dly & 0xff)
    elif group == 2:
        axi_write_single(BASEADDRESS_LANE1_ODELAY + (i<<2), dly & 0xff)
    elif group == 3:
        axi_write_single(BASEADDRESS_LANE1_IDELAY + (i<<2), dly & 0xff)
    elif group == 4:
        axi_write_single(BASEADDRESS_CMDA + (i<<2), dly & 0xff)
    axi_write_single(BASEADDR_DLY_SET, 0) # set all delays - remove after fixed axi_set_phase


def  axi_set_dq_idelay(#   task axi_set_dq_idelay;
        delay): # input [7:0] delay;
    global BASEADDRESS_LANE0_IDELAY,BASEADDRESS_LANE1_IDELAY, VERBOSE
    dly=delay;
    if (VERBOSE): print("SET DQ IDELAY=0x%x"%delay)
    for i in range(8):
        axi_write_single(BASEADDRESS_LANE0_IDELAY + (i<<2), dly & 0xff)
    for i in range(8):
        axi_write_single(BASEADDRESS_LANE1_IDELAY + (i<<2), dly & 0xff)
    axi_write_single(BASEADDR_DLY_SET, 0) # set all delays

def  axi_set_dq_odelay(#    task axi_set_dq_odelay;
        delay): #input [7:0] delay;
    global BASEADDRESS_LANE0_ODELAY,BASEADDRESS_LANE1_ODELAY, VERBOSE
    dly=delay;
    if (VERBOSE): print("SET DQ ODELAY=0x%x"%delay)
    for i in range(8):
        axi_write_single(BASEADDRESS_LANE0_ODELAY + (i<<2), dly & 0xff)
    for i in range(8):
        axi_write_single(BASEADDRESS_LANE1_ODELAY + (i<<2), dly & 0xff)
    axi_write_single(BASEADDR_DLY_SET, 0) # set all delays
def  axi_set_dqs_idelay(#    task axi_set_dqs_idelay;
        delay): # input [7:0] delay;
    global BASEADDRESS_LANE0_IDELAY,BASEADDRESS_LANE1_IDELAY, VERBOSE
    dly=delay
    i=8
    if (VERBOSE): print("SET DQS IDELAY=0x%x"%delay)
    axi_write_single(BASEADDRESS_LANE0_IDELAY + (i<<2), dly & 0xff)
    axi_write_single(BASEADDRESS_LANE1_IDELAY + (i<<2), dly & 0xff)
    axi_write_single(BASEADDR_DLY_SET, 0) # set all delays

def  axi_set_dqs_odelay(#    task axi_set_dqs_odelay;
        delay): # input [7:0] delay;
    dly=delay
    i=8
    global BASEADDRESS_LANE0_ODELAY,BASEADDRESS_LANE1_ODELAY, VERBOSE
    if (VERBOSE): print("SET DQS ODELAY=0x%x"%delay)
    axi_write_single(BASEADDRESS_LANE0_ODELAY + (i<<2), dly & 0xff)
    axi_write_single(BASEADDRESS_LANE1_ODELAY + (i<<2), dly & 0xff)
    axi_write_single(BASEADDR_DLY_SET, 0) # set all delays

def  axi_set_dm_odelay(#    task axi_set_dm_odelay;
        delay): # input [7:0] delay;
    global VERBOSE
    dly=delay;
    i=9;
    if (VERBOSE): print("SET DQM IDELAY=0x%x"%delay)
    axi_write_single(BASEADDRESS_LANE0_ODELAY + (i<<2), dly & 0xff)
    axi_write_single(BASEADDRESS_LANE1_ODELAY + (i<<2), dly & 0xff)
    axi_write_single(BASEADDR_DLY_SET, 0) # set all delays

def  axi_set_cmda_odelay(#    task axi_set_cmda_odelay;
        delay): # input [7:0] delay;
    global  VERBOSE
    dly=delay;
    if (VERBOSE): print("SET COMMAND and ADDRESS ODELAY=0x%x"%delay)
    for i in range(32):
        axi_write_single(BASEADDRESS_CMDA + (i<<2), dly & 0xff)
    axi_write_single(BASEADDR_DLY_SET, 0) # set all delays

def  axi_set_same_delays(#    task set_same_delays;
        dq_idelay,   # input [7:0] dq_idelay;
        dq_odelay,   # input [7:0] dq_odelay;
        dqs_idelay,  # input [7:0] dqs_idelay;
        dqs_odelay,  # input [7:0] dqs_odelay;
        dm_odelay,   # input [7:0] dm_odelay;
        cmda_odelay):# input [7:0] cmda_odelay;
    global VERBOSE
    if (VERBOSE): print("SET DELAYS(0x%x,0x%x,0x%x,0x%x,0x%x,0x%x)"%(dq_idelay,dq_odelay,dqs_idelay,dqs_odelay,dm_odelay,cmda_odelay))
    axi_set_dq_idelay(dq_idelay)
    axi_set_dq_odelay(dq_odelay)
    axi_set_dqs_idelay(dqs_idelay)
    axi_set_dqs_odelay(dqs_odelay)
    axi_set_dm_odelay(dm_odelay)
    axi_set_cmda_odelay(cmda_odelay)

def axi_set_phase( #    task axi_set_phase;
        phase): # input [PHASE_WIDTH-1:0] phase;
    global BASEADDRESS_PHASE, BASEADDR_DLY_SET, PHASE_WIDTH, VERBOSE
    if (VERBOSE): print("SET CLOCK PHASE to 0x%x"%phase)
    axi_write_single(BASEADDRESS_PHASE, phase & ((1<<PHASE_WIDTH)-1))
    axi_write_single(BASEADDR_DLY_SET, 0) # set all dealys

#   target_phase <= phase;

def axi_set_wbuf_delay(#    task axi_set_wbuf_delay;
        delay): #input [3:0] delay;
    global BASEADDR_WBUF_DELAY, VERBOSE
    if (VERBOSE): print("SET WBUF DELAY to 0x%x"%delay);
    axi_write_single(BASEADDR_WBUF_DELAY, delay);


def set_all_sequences(): #    task set_all_sequences;
    global VERBOSE
    if (VERBOSE): print("SET MRS")    
    set_mrs(1,4) # CL=5 (6: CL=7)
    if (VERBOSE): print("SET REFRESH")    
    set_refresh(
                50, # input [ 9:0] t_rfc; # =50 for tCK=2.5ns
                48) # 16) #input [ 7:0] t_refi; # 48/97 for normal, 8 - for simulation
    if (VERBOSE): print("SET WRITE LEVELING")    
    set_write_lev(16) # write leveling, 16 times   (full buffer - 128) 
    if (VERBOSE): print("SET READ PATTERN")    
    set_read_pattern(8,0,0) # 8x2*64 bits, 32x32 bits to read (second 0 - pattern type, only 0 defined)
    if (VERBOSE): print("SET WRITE BLOCK")    
    set_write_block(
                5,      # 3'h5,     # bank
                0x1234, # 15'h1234, # row address
                0x100   # 10'h100   # column address
            )
    if (VERBOSE): print("SET READ BLOCK")    
    set_read_block(
                5,      # 3'h5,     # bank
                0x1234, # 15'h1234, # row address
                0x100,   # 10'h100   # column address
                0       # use second clock for read commands
            )

def set_up(): #    task set_up;
    global DLY_DQ_IDELAY,DLY_DQ_ODELAY,DLY_DQS_IDELAY,DLY_DQS_ODELAY,DLY_DM_ODELAY,DLY_CMDA_ODELAY,WBUF_DLY_DFLT,DLY_PHASE
# set dq /dqs tristate on/off patterns
    axi_set_tristate_patterns()
# set patterns for DM (always 0) and DQS - always the same (may try different for write lev.)
    axi_set_dqs_dqm_patterns(0x0055)
#    axi_set_dqs_dqm_patterns(0x00aa)
# prepare all sequences
    set_all_sequences()
# prepare write buffer    
    write_block_buf() # fill block memory
# set all delays
#./ddrtests.py axi_set_same_delays (1a...34) (94...a8) 40 4c 70 30

    axi_set_same_delays(DLY_DQ_IDELAY,DLY_DQ_ODELAY,DLY_DQS_IDELAY,DLY_DQS_ODELAY,DLY_DM_ODELAY,DLY_CMDA_ODELAY)    
            #axi_set_delays;
#    set clock phase relative to DDR clk
    axi_set_phase(DLY_PHASE) #0x2c
    
    axi_set_wbuf_delay(WBUF_DLY_DFLT)
def split_delay(dly):
    global NUM_FINE_STEPS
    dly_int=dly>>3
    dly_fine=dly & 0x7
    if dly_fine > (NUM_FINE_STEPS-1):
        dly_fine= NUM_FINE_STEPS-1
    return dly_int*NUM_FINE_STEPS+dly_fine    
def combine_delay(dly):
    global NUM_FINE_STEPS
    return ((dly/NUM_FINE_STEPS)<<3)+(dly%NUM_FINE_STEPS)

def bad_data(buf):
    for w in buf:
        if (w!=0xffffffff): return False
    return True            
def scan_dqs(
       low_delay,
       high_delay,
       num ):
    global VERBOSE;
    saved_verbose=VERBOSE;
    VERBOSE=False;
    set_read_pattern(num+1,0,0); # do not use first/last pair of the 32 bit words
    low = split_delay(low_delay)
    high = split_delay(high_delay)
    results = []
    for dly in range (low, high+1):
        enc_dly=combine_delay(dly)
        axi_set_dqs_idelay_individual(enc_dly, enc_dly)
        run_read_pattern()
        buf=read_buf(4*num+2)
        if bad_data(buf):
            results.append([])
        else:    
            data=[0]*32 # for each bit - even, then for all - odd
            for w in range (4*num):
                lane=w%2
                for wb in range(32):
                    g=(wb/8)%2
                    b=wb%8+lane*8+16*g
                    if (buf[w+2] & (1<<wb) != 0):
                        data[b]+=1
            results.append(data)
            print ("%3d (0x%02x): "%(dly,enc_dly),end="")
            for i in range(32):
                print("%5x"%data[i],end="")
            print()    
    for index in range (len(results)):
        dly=index+low
        enc_dly=combine_delay(dly)
        if (len (results[index])>0):
            print ("%3d (0x%02x): "%(dly,enc_dly),end="")
            for i in range(32):
                print("%5x"%results[index][i],end="")
            print()    
#        else:
#            print ("%3d (0x%02x): *** BAD data *** "%(dly,enc_dly))
    print()
    print()
    print ("Delay",end=" ")
    for i in range(16):
        print ("Bit%dP"%i,end=" ")
    for i in range(16):
        print ("Bit%dM"%i,end=" ")
    print()
    for index in range (len(results)):
        dly=index+low
        enc_dly=combine_delay(dly)
        if (len (results[index])>0):
            print ("%d"%(dly),end=" ")
            for i in range(32):
                print("%d"%results[index][i],end=" ")
            print()    
#        else:
#            print ("%3d (0x%02x): *** BAD data *** "%(dly,enc_dly))
    print()
    VEBOSE=saved_verbose
    return results                                  

def scan_dq_idelay(
       low_delay,
       high_delay,
       num ):
    global VERBOSE;
    saved_verbose=VERBOSE;
    VERBOSE=False;
    set_read_pattern(num+1,0,0); # do not use first/last pair of the 32 bit words
    low = split_delay(low_delay)
    high = split_delay(high_delay)
    results = []
    for dly in range (low, high+1):
        enc_dly=combine_delay(dly)
        axi_set_dq_idelay(enc_dly)
        run_read_pattern()
        wait_sequencer_ready()
        buf=read_buf(4*num+2)
        if bad_data(buf):
            results.append([])
        else:    
            data=[0]*32 # for each bit - even, then for all - odd
            for w in range (4*num):
                lane=w%2
                for wb in range(32):
                    g=(wb/8)%2
                    b=wb%8+lane*8+16*g
                    if (buf[w+2] & (1<<wb) != 0):
                        data[b]+=1
            results.append(data)
            print ("%3d (0x%02x): "%(dly,enc_dly),end="")
            for i in range(32):
                print("%5x"%data[i],end="")
            print()    
    for index in range (len(results)):
        dly=index+low
        enc_dly=combine_delay(dly)
        if (len (results[index])>0):
            print ("%3d (0x%02x): "%(dly,enc_dly),end="")
            for i in range(32):
                print("%5x"%results[index][i],end="")
            print()    
#        else:
#            print ("%3d (0x%02x): *** BAD data *** "%(dly,enc_dly))
    print()
    print()
    print ("Delay",end=" ")
    for i in range(16):
        print ("Bit%dP"%i,end=" ")
    for i in range(16):
        print ("Bit%dM"%i,end=" ")
    print()
    for index in range (len(results)):
        dly=index+low
        enc_dly=combine_delay(dly)
        if (len (results[index])>0):
            print ("%d"%(dly),end=" ")
            for i in range(32):
                print("%d"%results[index][i],end=" ")
            print()    
#        else:
#            print ("%3d (0x%02x): *** BAD data *** "%(dly,enc_dly))
    print()
    VEBOSE=saved_verbose
    return results                                  

def adjust_dq_idelay(
       low_delay,
       high_delay,
       num,
       falling ): # 0 - use rising as delay increases, 1 - use falling
    global VERBOSE;
    saved_verbose=VERBOSE;
    VERBOSE=False;
    low = split_delay(low_delay)
    data_raw=scan_dq_idelay(low_delay,high_delay,num)
    data=[]
    delays=[]
    for i,d in enumerate(data_raw):
        if len(d)>0:
            data.append(d)
            delays.append(i+low)
    print(delays)
    
    best_dlys=[0]*16
    best_diffs=[num*8.0]*16
    for i in range (1,len(data)-1):
        for j in range (16):
            delta=abs(data[i][j] -data[i][j+16] + 0.5*(data[i-1][j] -data[i-1][j+16]+data[i+1][j] -data[i+1][j+16]))
            sign=(data[i-1][j] -data[i-1][j+16]-data[i+1][j]+data[i+1][j+16])
            if falling > 0: sign=-sign;
            if (sign>0) and (delta < best_diffs[j]):
                best_diffs[j]=delta
                best_dlys[j]=delays[i]
    for i in range (16):
        print("%2d: %3d (0x%02x)"%(i,best_dlys[i],combine_delay(best_dlys[i])))  
    VEBOSE=saved_verbose
    for i in range (8):
        axi_set_dly_single(1,i,combine_delay(best_dlys[i]))    
    for i in range (8):
        axi_set_dly_single(3,i,combine_delay(best_dlys[i+8]))    
    
#    VEBOSE=saved_verbose

def convert_mem16_to_w32(mem16):
    res32=[]
    for i in range(0,len(mem16),4):
        res32.append(((mem16[i+3] & 0xff) << 24) |
                     ((mem16[i+2] & 0xff) << 16) |
                     ((mem16[i+1] & 0xff) << 8) |
                     ((mem16[i+0] & 0xff) << 0))
        res32.append((((mem16[i+3]>>8) & 0xff) << 24) |
                     (((mem16[i+2]>>8) & 0xff) << 16) |
                     (((mem16[i+1]>>8) & 0xff) << 8) |
                     (((mem16[i+0]>>8) & 0xff) << 0))
    return res32

def convert_w32_to_mem16(w32):
    mem16=[]
    for i in range(0,len(w32),2):
        mem16.append(((w32[i]>> 0) & 0xff) | (((w32[i+1] >>  0) & 0xff) << 8)) 
        mem16.append(((w32[i]>> 8) & 0xff) | (((w32[i+1] >>  8) & 0xff) << 8)) 
        mem16.append(((w32[i]>>16) & 0xff) | (((w32[i+1] >> 16) & 0xff) << 8)) 
        mem16.append(((w32[i]>>24) & 0xff) | (((w32[i+1] >> 24) & 0xff) << 8)) 
    return mem16

# calibratin finedelay dealy steps using everaged "eye" data, assuming that most error
# is in finedelay stage
def corr_delays(
            low,         # absolute delay value of start scan
            avg_types,   # weights of weach of the 8  bit sequences
            res_bits,    #individual per-bit results
            res_avg,     # averaged eye data tablle, each line has 8 elements, or [] for bad measurements
            corr_fine,   # fine delay correction
            ends_dist,   # do not process if one of the primary interval ends is within this from 0.0 or 1.0
            verbose
                ):
    # coarse adjustmenty - decimate arrays to use the same (0) value of the fine delay
    usable_types=[]
    for i,w in enumerate(avg_types):
        if (w>0) and not i in (0,7) :
            usable_types.append(i)
    if (verbose): print ("usable_types=",usable_types)            
    def thr_sign(bit,type,limit,data):
        lim_l=limit
        lim_u=1.0-limit
        if data[bit][type] <= limit: return -1
        if data[bit][type] >= (1.0- limit): return 1
        return 0
    def thr_signs(type,limit,data):
        signs=""
        for bit in range(15,-1,-1):
            signs+=("-","0","+")[thr_sign(bit,type,limit,data)+1]
    def full_state(types,limit,data): #will NOT return None if any is undefined
        state=""
        for t in types:
            for bit in range(15,-1,-1):
                state+=("-","0","+")[thr_sign(bit,t,limit,data)+1]
        return state                    
    def full_same_state(types,limit,data): #will return None if any is undefined
        state=""
        for t in types:
            s0=thr_sign(15,t,limit,data)
            state+=("-","0","+")[s0+1]
            for bit in range(15,-1,-1):
                s=thr_sign(bit,t,limit,data)
                if (not s) or (s != s0) :
                    return None
        return state                    
            
                    
    def diff_state(state1,state2):
        for i,s in enumerate(state1):
            if s != state2[i]:
                return True
        return False    
        
    global NUM_FINE_STEPS
    start_index=0;
    if (low % NUM_FINE_STEPS) != 0:
        start_index=NUM_FINE_STEPS-(low % NUM_FINE_STEPS)
    #find the first index where all bits are either above 1.0 -ends_dist or below ends_dist
    for index in range(len(res_avg)):
        print (" index=%d: %s"%(index,full_state(usable_types,ends_dist,res_bits[index])))
        initial_state=full_same_state(usable_types,ends_dist,res_bits[index])
        if initial_state:
            break
    else:
        print ("Could not find delay value where all bits/types are outside of undefined area (%f thershold)"%ends_dist)
        return None
    if (verbose): print ("start index=%d, start state=%s"%(index,initial_state))
    #find end of that state
    for index in range(index+1,len(res_avg)):
        state=full_same_state(usable_types,ends_dist,res_bits[index])
        if state != initial_state:
            break
    else:
        print ("Could not find delay value where initial state changes  (%f thershold)"%ends_dist)
        return None
    last_initial_index=index-1
    if (verbose): print ("last start state index=%d, new state=%s"%(last_initial_index,state))
    #find new defined state for all bits
    for index in range(last_initial_index+1,len(res_avg)): #here repeat last delay
        new_state=full_same_state(usable_types,ends_dist,res_bits[index])
        if new_state and (new_state != initial_state):
            break
    else:
        print ("Could not find delay value whith the new defined state (%f thershold)"%ends_dist)
        return None
    new_state_index=index
    if (verbose): print ("new defined state index=%d, new state=%s"%(new_state_index,new_state))
# remove states that do not have a transition    
    filtered_types=[]
    for i,t in enumerate(usable_types):
        if (new_state[i]!=initial_state[i]):
            filtered_types.append(t)
    if (verbose): print ("filtered_types=",filtered_types)            
    second_trans= 1 in filtered_types # use second transition, false - use first transition
    if (verbose): print("second_trans=",second_trans)
#    signs=((1,1,-1,-1),(1,-1,1,-1))[1 in filtered_types]
    signs=((0,0,1,1,-1,-1,0,0),(0,1,-1,0,0,1,-1,0))[1 in filtered_types]
    if (verbose): print("signs=",signs)
        
    for index in range(last_initial_index,new_state_index+1):
        if (verbose): print ("index=%3d, delay=%3d, state=%s"%(index,index+low,full_state(filtered_types,ends_dist,res_bits[index])))  

#extend range, combine each bit and averages
    ext_low_index=last_initial_index-(new_state_index-last_initial_index)
    if ext_low_index<0:
        ext_low_index=0
    ext_high_index=new_state_index+(new_state_index-last_initial_index)
    if ext_high_index>=len(res_bits):
        ext_high_index=res_bits-1
    if (verbose): print("ext_low_index=%d ext_high_index=%d"%(ext_low_index,ext_high_index))
    bit_data=[]
    for i in range(16):
        bit_data.append([]) # [[]]*16 does not work! (shallow copy)
    avg_data=[]
    for index0 in range(ext_high_index-ext_low_index+1):
        index=index0+ext_low_index
#        if (verbose): print(res_bits[index])
        bit_samples=[0.0]*16
        avg_sample=0.0
        weight=0.0
        for t in filtered_types:
            w=avg_types[t]
            weight+=w
            sw=signs[t]*w
            avg_sample += sw * (2.0*res_avg[index][t]-1.0)
#            if (verbose): print ("%3d %d:"%(index,t),end=" ")
            for bit in range(16):
                bit_samples[bit] += sw*(2.0*res_bits[index][bit][t]-1.0)
#                if (verbose): print ("%.3f"%(res_bits[index][bit][t]),end=" ")
#            if (verbose): print()    
        
        avg_sample /= weight
        avg_data.append(avg_sample)    
        for bit in range(16):
            bit_samples[bit] /= weight
#            if (verbose): print ("bit_samples[%d]=%f"%(bit,bit_samples[bit]))
            bit_data[bit].append(bit_samples[bit])
#        if (verbose): print ("bit_samples=",bit_samples)
#       if index0 <3:
#            if (verbose): print ("bit_data=",bit_data)
                    
#    if (verbose): print ("\n\nbit_data=",bit_data)
    period_fine=len(corr_fine)
    for index in range(ext_high_index-ext_low_index+1):
        dly=low+index+ext_low_index
        corr_dly=dly+corr_fine[dly%period_fine]
        if (verbose): print ("%d %d %.2f %.3f"%(index,dly,corr_dly,avg_data[index]),end=" ")
        for bit in range(16):
            if (verbose): print ("%.3f"%(bit_data[bit][index]),end=" ")
        if (verbose): print()            
# Seems all above was an overkill, just find bit delays that result in  most close to 0
    delays=[]
    for bit in range(16):
        best_dist=1.0
        best_index=None
        for index in range(ext_high_index-ext_low_index+1):
            if (abs(bit_data[bit][index])<best_dist):
                best_dist=abs(bit_data[bit][index])
                best_index=index
        delays.append(best_index+low+ext_low_index)
    if (verbose): print (delays)
    return delays


def calibrate_finedelay(
            low,         # absolute delay value of start scan
            avg_types,   # weights of weach of the 8  bit sequences
            res_avg,     # averaged eye data tablle, each line has 8 elements, or [] for bad measurements
            ends_dist,   # do not process if one of the primary interval ends is within this from 0.0 or 1.0
            min_diff):   # minimal difference between primary delay steps to process
     global NUM_FINE_STEPS
     start_index=0;
     if (low % NUM_FINE_STEPS) != 0:
         start_index=NUM_FINE_STEPS-(low % NUM_FINE_STEPS)
     weights=[0.0]*( NUM_FINE_STEPS)
     corr=[0.0]*( NUM_FINE_STEPS) #[0] will stay 0
     for index in range(start_index, len(res_avg)-NUM_FINE_STEPS,NUM_FINE_STEPS):
         if (len(res_avg[index])>0) and (len(res_avg[index+NUM_FINE_STEPS])>0):
             for t,w in enumerate(avg_types):
                 if (w>0):
                     f=res_avg[index][t];
                     s=res_avg[index+NUM_FINE_STEPS][t];
#                     print ("index=%d t=%d f=%f s=%s"%(index,t,f,s))
                     if ((f>ends_dist) and (s>ends_dist) and
                          (f< (1-ends_dist)) and (s < (1-ends_dist)) and
                          (abs(s-f)>min_diff)):
                         diff=s-f
                         wd=w* diff*diff # squared? or use abs?
                         for j in range (1,NUM_FINE_STEPS):
                             if ( (len(res_avg[index+j])>0)):
                                 v=res_avg[index+j][t];
                                 #correction to the initila step==1
                                 d=(v-f)/(s-f)*NUM_FINE_STEPS-j
                                 #average
                                 corr[j]+=wd*d
                                 weights[j]+=wd
                                         
#     print ("\n weights:")
#     print(weights)
#     print ("\n corr:")
#     print(corr)
     for i,w in enumerate(weights):
         if (w>0) : corr[i]/=w # will skip 0
    
     print ("\ncorr:")
#     print(corr)
     for i,c in enumerate(corr):
         print ("%i %f"%(i,c))
     return corr
 
                          
   
    
        
def scan_or_adjust_delay_random(
       low_delay,
       high_delay,
       use_dq, # 0 - scan dqs, 1 - scan dq (common valuwe, post-adjustment)
       use_odelay,
       ends_dist,   # do not process if one of the primary interval ends is within this from 0.0 or 1.0
       min_diff,
       adjust,
       verbose):   # minimal difference between primary delay steps to process
       
    global BASEADDR_PORT1_WR,VERBOSE;
    saved_verbose=VERBOSE;
    VERBOSE=False;
#    set_read_pattern(num+1,0,0); # do not use first/last pair of the 32 bit words
    low = split_delay(low_delay)
    high = split_delay(high_delay)
    rand16=[]
    for i in range(512):
        rand16.append(random.randint(0,65535))
    wdata=convert_mem16_to_w32(rand16)
    if (verbose and not adjust): print("rand16:")
    for i in range(len(rand16)):
        if (i & 0x1f) == 0:
            if (verbose and not adjust): print("\n%03x:"%i,end=" ")
        if (verbose and not adjust): print("%04x"%rand16[i],end=" ")
    if (verbose and not adjust): print("\n")        
    if (verbose and not adjust): print("wdata:")
    for i in range(len(wdata)):
        if (i & 0xf) == 0:
            if (verbose and not adjust): print("\n%03x:"%i,end=" ")
        if (verbose and not adjust): print("%08x"%wdata[i],end=" ")
    if (verbose and not adjust): print("\n")        
    bit_type=[] # does not include first and last elements
    for i in range(1,511):
        types=[]
        for j in range(16):
            types.append((((rand16[i-1]>>j) & 1)<<2) | (((rand16[i  ]>>j) & 1)<<1) |  (((rand16[i+1]>>j) & 1)))
        bit_type.append(types)
#        if (verbose and not adjust): print ("i=%d",i)
#        if (verbose and not adjust): print(types)
#    total_types=[[0]*8]*16 # number of times each type occured in the block for each DQ bit (separate for DG up/down?)
    total_types=[] # number of times each type occured in the block for each DQ bit (separate for DG up/down?)
    for i in range(16): total_types.append([0]*8) 
    for type in bit_type:
#        if (verbose and not adjust): print(type)
        for j in range(16):
#            total_types[j][type[j]]+=1
            total_types[j][type[j]]=total_types[j][type[j]]+1
    if (verbose and not adjust): print("\ntotal_types:")        
    if (verbose and not adjust): print (total_types)
    
    avg_types=[0.0]*8
    N=0
    for t in total_types:
        for j,n in enumerate(t):
            avg_types[j]+=n
            N+=n
    for i in range(len(avg_types)):
        avg_types[i]/=N
    if (verbose and not adjust): print("\avg_types:")        
    if (verbose and not adjust): print (avg_types)
        
    #write blobk buffer with 256x32bit data        
    for i in range(256):
        axi_write_single(BASEADDR_PORT1_WR+(i<<2), wdata[i])
    set_write_block(
                5,      # 3'h5,     # bank
                0x1234, # 15'h1234, # row address
                0x100   # 10'h100   # column address
            )
    if (use_odelay==0) :
        run_write_block()
        wait_sequencer_ready()
        if VERBOSE: print("++++++++ block written once")
    
#now scanning - first DQS, then try with DQ (post-adjustment - best fit) 
    results = []
    if VERBOSE: print("******** use_odelay=%d use_dq=%d"%(use_odelay,use_dq))

    for dly in range (low, high+1):
        enc_dly=combine_delay(dly)
        if (use_odelay!=0) :
            if (use_dq!=0):
                if VERBOSE: print("******** axi_set_dq_odelay(0x%x)"%enc_dly)
                axi_set_dq_odelay(enc_dly) #  set the same odelay for all DQ bits
            else:
                if VERBOSE: print("******** axi_set_dqs_odelay(0x%x)"%enc_dly)
                axi_set_dqs_odelay(enc_dly)
            run_write_block()
            wait_sequencer_ready()
            if VERBOSE: print("-------- block written AGAIN")
                            
        else:
            if (use_dq!=0):
                if VERBOSE: print("******** axi_set_dq_idelay(0x%x)"%enc_dly)
                axi_set_dq_idelay(enc_dly)#  set the same idelay for all DQ bits
            else:
                if VERBOSE: print("******** axi_set_dqs_idelay(0x%x)"%enc_dly)
                axi_set_dqs_idelay(enc_dly)
            
            
            
        run_read_block()
        wait_sequencer_ready()
        buf32=read_buf(256)
        if bad_data(buf32):
            results.append([])
        else: 
            read16=convert_w32_to_mem16(buf32) # 512x16 bit, same as DDR3 DQ over time
            if VERBOSE and (dly==low):   
                if (verbose and not adjust): print("buf32:")
                for i in range(len(buf32)):
                    if (i & 0xf) == 0:
                        if (verbose and not adjust): print("\n%03x:"%i,end=" ")
                    if (verbose and not adjust): print("%08x"%buf32[i],end=" ")
                if (verbose and not adjust): print("\n")        


                if (verbose and not adjust): print("read16:")
                for i in range(len(read16)):
                    if (i & 0x1f) == 0:
                        if (verbose and not adjust): print("\n%03x:"%i,end=" ")
                    if (verbose and not adjust): print("%04x"%read16[i],end=" ")
                if (verbose and not adjust): print("\n")
#            exit (0)        
            
#            data=[[0]*8]*16 # for each bit - 8 types
            data=[] # number of times each type occured in the block for each DQ bit (separate for DG up/down?)
            for i in range(16):
                data.append([0]*8) 
            
            for i in range (1,511):
                w= read16[i]
                type=bit_type[i-1] # first and last words are not used, no type was calculated
                for j in range(16):
                    if (w & (1<<j)) !=0:
                        data[j][type[j]]+=1
            for i in range(16):
                for t in range(8):
                    if (total_types[i][t] >0 ):
                        data[i][t]*=1.0/total_types[i][t]
            results.append(data)
            if (verbose and not adjust): print ("%3d (0x%02x): "%(dly,enc_dly),end="")
            for i in range(16):
                if (verbose and not adjust): print("[",end="")
                for j in range(8):
                    if (verbose and not adjust): print("%3d"%(round(100.0*data[i][j])),end=" ")
                if (verbose and not adjust): print("]",end=" ")
            if (verbose and not adjust): print()    
    titles=["'000","'001","'010", "'011","'100","'101","'110","'111"]
    #calculate weighted averages
    #TODO: for DQ scan shift individula bits for the best match
    if  use_dq:
        if (verbose and not adjust): print("TODO: shift individual bits for the best match before averaging")

    res_avg=[]
    for dly in range (len(results)):
        if (len(results[dly])>0):
            data=results[dly]
            avg=[0.0]*8
            for t in range(8):
                weight=0;
                d=0.0
                for i in range(16):
                    weight+=total_types[i][t]
                    d+=total_types[i][t]*data[i][t]
                if (weight>0):
                    d/=weight
                avg[t] = d
            res_avg.append(avg)
        else:
            res_avg.append([])
    corr_fine=calibrate_finedelay(
            low,         # absolute delay value of start scan
            avg_types,   # weights of weach of the 8  bit sequences
            res_avg,     # averaged eye data tablle, each line has 8 elements, or [] for bad measurements
            ends_dist/256.0, # ends_dist,   # do not process if one of the primary interval ends is within this from 0.0 or 1.0
            min_diff/256.0) #min_diff):   # minimal difference between primary delay steps to process
    period=len(corr_fine)

    if (not adjust):
        print("\n\n\n========== Copy below to the spreadsheet,  use columns from corr_delay ==========")
        print("========== First are individual results for each bit, then averaged eye pattern ==========")
        print ("delay corr_delay",end=" ")
        for t in range(8):
            for i in range(16):
                if (not adjust): print("%02d:%s"%(i,titles[t]),end=" ")
        print()
        for index in range (len(results)):
            if (len(results[index])>0):
                dly=index+low
                corr_dly=dly+corr_fine[dly%period]
                print ("%d %.2f"%(dly,corr_dly),end=" ")
                for t in range(8):
                    for i in range(16):
                        print("%.4f"%(results[dly][i][t]),end=" ")
                print()
                        
        print("\n\n\n========== Copy below to the spreadsheet,  use columns from corr_delay ==========")
        print("========== data above can be used for the individual bits eye patterns ==========")            
        print ("delay corr_delay",end=" ")
        for t in range(8):
            print(titles[t],end=" ")
        print()
        for index in range (len(res_avg)):
            if (len(res_avg[index])>0):
                dly=index+low
                corr_dly=dly+corr_fine[dly%period]
                print ("%d %.2f"%(dly,corr_dly),end=" ")
                for t in range(8):
                    print("%.4f"%(res_avg[dly][t]),end=" ")
                print()
    dly_corr=None
    if adjust:        
        dly_corr=corr_delays(
            low,         # absolute delay value of start scan
            avg_types,   # weights of weach of the 8  bit sequences
            results,    #individual per-bit results
            res_avg,     # averaged eye data tablle, each line has 8 elements, or [] for bad measurements
            corr_fine,    # fine delay correction
            ends_dist/256.0,   # find where all bits are above/below that distance from 0.0/1.0margin
            verbose)
        VERBOSE=verbose
        print ("VERBOSE=",VERBOSE)
        print ("dly_corr=",dly_corr)
        print ("use_dq=",use_dq)
        if dly_corr and use_dq: # only adjusting DQ delays, not DQS
            if use_odelay:
                for i in range (8):
                    axi_set_dly_single(0,i,combine_delay(dly_corr[i]))    
                for i in range (8):
                    axi_set_dly_single(2,i,combine_delay(dly_corr[i+8]))
            else:    
                for i in range (8):
                    axi_set_dly_single(1,i,combine_delay(dly_corr[i]))    
                for i in range (8):
                    axi_set_dly_single(3,i,combine_delay(dly_corr[i+8]))
#          use_dq, # 0 - scan dqs, 1 - scan dq (common valuwe, post-adjustment)
 #      use_odelay,
        
    VEBOSE=saved_verbose
    return dly_corr

def scan_delay_random(
       low_delay,
       high_delay,
       use_dq, # 0 - scan dqs, 1 - scan dq (common valuwe, post-adjustment)
       use_odelay, # 0 - idelay, 1 - odelay
       ends_dist,   # do not process if one of the primary interval ends is within this from 0.0 or 1.0
       min_diff,
       verbose):   # minimal difference between primary delay steps to process
    scan_or_adjust_delay_random(
       low_delay,
       high_delay,
       use_dq, # 0 - scan dqs, 1 - scan dq (common valuwe, post-adjustment)
       use_odelay,
       ends_dist,   # do not process if one of the primary interval ends is within this from 0.0 or 1.0
       min_diff,
       False,     #scan, not adjust
       verbose)   # minimal difference between primary delay steps to process
def adjust_dq_delay_random(
       low_delay,
       high_delay,
       #use_dq, # 0 - scan dqs, 1 - scan dq (common valuwe, post-adjustment)
       use_odelay,
       ends_dist,   # do not process if one of the primary interval ends is within this from 0.0 or 1.0
       min_diff,
       verbose):   # minimal difference between primary delay steps to process
    scan_or_adjust_delay_random(
       low_delay,
       high_delay,
       1, #use_dq, # 0 - scan dqs, 1 - scan dq (common valuwe, post-adjustment)
       use_odelay,
       ends_dist,   # do not process if one of the primary interval ends is within this from 0.0 or 1.0
       min_diff,
       True,        #adjust, not scan
       verbose)   # minimal difference between primary delay steps to process
# main
if len(sys.argv)<2:
    print ("Usage: %s command [hex_parameter, ...]"%sys.argv[0])
    exit (0)
command= sys.argv[1];
args=[]
for i in range(2,len(sys.argv)):
    args.append(int(sys.argv[i],16))
if   command=="axi_write_single":
    check_args(2,command,args)
    axi_write_single(args[0],args[1])
    print("axi_write_single(0x%x,0x%x) OK"%(args[0],args[1]))
elif command=="axi_read_addr":
    check_args(1,command,args)
    print ("axi_read_addr(0x%x) => 0x%x"%(args[0],axi_read_addr(args[0])))
elif command=="read_status":
    check_args(0,command,args)
    print ("read_status() => 0x%x"%(read_status()))
elif command=="wait_phase_shifter_ready":
    check_args(1,command,args)
    wait_phase_shifter_ready(args[0])
    print("wait_phase_shifter_ready(%x) OK"%args[0])
elif command=="wait_sequencer_ready":
    check_args(0,command,args)
    wait_sequencer_ready()
    print("wait_sequencer_ready() OK")
elif command=="run_sequence":
    check_args(2,command,args)
    run_sequence(args[0],args[1])
    print("run_sequence(0x%x,0x%x) OK"%(args[0],args[1]))
    
elif command=="run_mrs":
    check_args(0,command,args)
    run_mrs()
    print("run_mrs() OK")
elif command=="run_write_lev":
    check_args(0,command,args)
    run_write_lev()
    print("run_write_lev() OK")
elif command=="run_read_pattern":
    check_args(0,command,args)
    run_read_pattern()
    print("run_read_pattern() OK")
elif command=="run_write_block":
    check_args(0,command,args)
    run_write_block()
    print("run_write_block() OK")
elif command=="run_read_block":
    check_args(0,command,args)
    run_read_block()
    print("run_read_block() OK")
    
elif command=="enable_cmda":
    check_args(1,command,args)
    enable_cmda(args[0])
    print("enable_cmda(0x%x) OK"%(args[0]))
elif command=="enable_cke":
    check_args(1,command,args)
    enable_cke(args[0])
    print("enable_cke(0x%x) OK"%(args[0]))
elif command=="activate_sdrst":
    check_args(1,command,args)
    activate_sdrst(args[0])
    print("activate_sdrst(0x%x) OK"%(args[0]))
elif command=="enable_refresh":
    check_args(1,command,args)
    enable_refresh(args[0])
    print("enable_refresh(0x%x) OK"%(args[0]))
elif command=="write_block_buf":
    check_args(0,command,args)
    write_block_buf()
    print("write_block_buf() OK")
elif command=="read_block_buf":
    check_args(1,command,args)
    read_block_buf(args[0])
    print("read_block_buf() OK")
elif command=="read_buf":
    check_args(1,command,args)
    read_buf(args[0])
    print("read_buf() OK")
elif command=="set_read_pattern":
    check_args(3,command,args)
    set_read_pattern(args[0],args[1],args[2])
    print("set_read_pattern(0x%x,0x%x,0x%x) OK"%(args[0],args[1],args[2]))
elif command=="set_read_block":
    check_args(4,command,args)
    set_read_block(args[0],args[1],args[2],args[3])
    print("set_read_block(0x%x,0x%x,0x%x,0x%x) OK"%(args[0],args[1],args[2],args[3]))
elif command=="set_write_block":
    check_args(3,command,args)
    set_write_block(args[0],args[1],args[2])
    print("set_write_block(0x%x,0x%x,0x%x) OK"%(args[0],args[1],args[2]))
elif command=="set_write_lev":
    check_args(1,command,args)
    set_write_lev(args[0])
    print("set_write_lev(0x%x) OK"%(args[0]))
elif command=="set_refresh":
    check_args(2,command,args)
    set_refresh(args[0],args[1])
    print("set_refresh(0x%x,0x%x) OK"%(args[0],args[1]))
elif command=="set_mrs":
    check_args(2,command,args)
    set_mrs(args[0],args[1])
    print("set_mrs(0x%x,0x%x) OK"%(args[0],args[1]))
elif command=="axi_set_delays":
    check_args(0,command,args)
    axi_set_delays()
    print("axi_set_delays() OK")
elif command=="axi_set_dqs_idelay_nominal":
    check_args(0,command,args)
    axi_set_dqs_idelay_nominal()
    print("axi_set_dqs_idelay_nominal() OK")
elif command=="axi_set_dqs_idelay_individual":
    check_args(2,command,args)
    axi_set_dqs_idelay_individual(args[0],args[1])
    print("axi_set_dqs_idelay_individual(0x%x,0x%x) OK"%(args[0],args[1]))
elif command=="axi_set_dqs_idelay_wlv":
    check_args(0,command,args)
    axi_set_dqs_idelay_wlv()
    print("axi_set_dqs_idelay_wlv() OK")
elif command=="axi_set_dly_single":
    check_args(3,command,args)
    axi_set_dly_single(args[0],args[1],args[2])
    print("axi_set_dly_single(0x%x,0x%x,0x%x) OK"%(args[0],args[1],args[2]))
    
    
elif command=="axi_set_dq_idelay":
    check_args(1,command,args)
    axi_set_dq_idelay(args[0])
    print("axi_set_dq_idelay(0x%x) OK"%(args[0]))
    
elif command=="axi_set_dq_odelay":
    check_args(1,command,args)
    axi_set_dq_odelay(args[0])
    print("axi_set_dq_odelay(0x%x) OK"%(args[0]))
    
elif command=="axi_set_dqs_idelay":
    check_args(1,command,args)
    axi_set_dqs_idelay(args[0])
    print("axi_set_dqs_idelay(0x%x) OK"%(args[0]))
    
elif command=="axi_set_dqs_odelay":
    check_args(1,command,args)
    axi_set_dqs_odelay(args[0])
    print("axi_set_dqs_odelay(0x%x) OK"%(args[0]))
    
elif command=="axi_set_dm_odelay":
    check_args(1,command,args)
    axi_set_dm_odelay(args[0])
    print("axi_set_dm_odelay(0x%x) OK"%(args[0]))

elif command=="axi_set_cmda_odelay":
    check_args(1,command,args)
    axi_set_cmda_odelay(args[0])
    print("axi_set_cmda_odelay(0x%x) OK"%(args[0]))
    
elif command=="axi_set_same_delays":
    check_args(6,command,args)
    axi_set_same_delays(args[0],args[1],args[2],args[3],args[4],args[5])
    print("axi_set_same_delays(0x%x) OK"%(args[0]))
    
elif command=="axi_set_phase":
    check_args(1,command,args)
    axi_set_phase(args[0])
    print("axi_set_phase(0x%x) OK"%(args[0]))

elif command=="axi_set_wbuf_delay":
    check_args(1,command,args)
    axi_set_wbuf_delay(args[0])
    print("axi_set_wbuf_delay(0x%x) OK"%(args[0]))
    
elif command=="set_write_lev":
    check_args(1,command,args)
    set_write_lev(args[0])
    print("set_write_lev(0x%x) OK"%(args[0]))
elif command=="axi_set_tristate_patterns":
    check_args(0,command,args)
    axi_set_tristate_patterns()
    print("axi_set_tristate_patterns() OK")
elif command=="axi_set_dqs_dqm_patterns":
    check_args(1,command,args)
    axi_set_dqs_dqm_patterns(args[0])
    print("axi_set_dqs_dqm_patterns(0x%x) OK"%(args[0]))
    
elif command=="set_all_sequences":
    check_args(0,command,args)
    set_all_sequences()
    print("set_all_sequences() OK")

elif command=="set_up":
    check_args(0,command,args)
    set_up()
    print("set_up() OK")
#  
elif command=="scan_dqs":
    check_args(3,command,args)
    scan_dqs(args[0],args[1],args[2])
    print("scan_dqs(0x%x,0x%x,0x%x) OK"%(args[0],args[1],args[2]))

elif command=="scan_dq_idelay":
    check_args(3,command,args)
    scan_dq_idelay(args[0],args[1],args[2])
    print("scan_dq_idelay(0x%x,0x%x,0x%x) OK"%(args[0],args[1],args[2]))

elif command=="scan_delay_random":
    check_args(7,command,args)
    scan_delay_random(args[0],args[1],args[2],args[3],args[4],args[5],args[6])
    print("scan_delay_random(0x%x,0x%x,0x%x,0x%x,0x%x,0x%x,0x%x) OK"%(args[0],args[1],args[2],args[3],args[4],args[5],args[6]))

elif command=="adjust_dq_delay_random":
    check_args(6,command,args)
    adjust_dq_delay_random(args[0],args[1],args[2],args[3],args[4],args[5])
    print("adjust_dq_delay_random(0x%x,0x%x,0x%x,0x%x,0x%x,0x%x) OK"%(args[0],args[1],args[2],args[3],args[4],args[5]))

elif command=="adjust_dq_idelay":
    check_args(4,command,args)
    adjust_dq_idelay(args[0],args[1],args[2],args[3])
    print("adjust_dq_idelay(0x%x,0x%x,0x%x,0x%x) OK"%(args[0],args[1],args[2],args[3]))
  
else:
    print("Invalid command: %s"%command)
exit (0)    


