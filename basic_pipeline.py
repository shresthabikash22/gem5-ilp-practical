

from m5.objects import *
import m5
import os
import csv

# Debug flags for pipeline tracing
from m5 import options
options.debug_flags = [
    'MinorFetch1',
    'MinorFetch2',
    'MinorDecode',
    'MinorExecute',
    'MinorCommit'
]
options.debug_file = 'm5out/pipeline_debug.txt'

# System Setup
system = System()
system.clk_domain = SrcClockDomain(clock="1GHz",
                                   voltage_domain=VoltageDomain())
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MB")]

# CPU + Bus + Memory
system.cpu = DerivO3CPU()
system.cpu.createInterruptController()
system.cpu.createThreads()

# System bus
system.membus = SystemXBar()
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports
system.system_port = system.membus.cpu_side_ports

# Connect interrupt ports (x86 requirement)
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR4_2400_4x16()
system.mem_ctrl.port = system.membus.mem_side_ports

# Workload (SE mode)
binary = "workload"  
if not os.path.exists(binary):
    raise RuntimeError(f"Binary '{binary}' not found!")

process = Process()
process.executable = binary
process.cmd = [binary]

# Set system workload
system.workload = SEWorkload.init_compatible(binary)
system.cpu.workload = process


root = Root(full_system=False, system=system)

print("Instantiating system...")
m5.instantiate()

print("Starting simulation — running:", process.executable)
exit_event = m5.simulate()
print("Exit cause:", exit_event.getCause())
print("Simulation finished.")
