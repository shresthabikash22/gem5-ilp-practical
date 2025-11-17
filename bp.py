from m5.objects import *
import m5
import os

#  System basics
system = System()
system.clk_domain = SrcClockDomain(clock='2GHz')
system.clk_domain.voltage_domain = VoltageDomain()  
system.mem_mode   = 'timing'
system.mem_ranges = [AddrRange('512MB')]

#  Memory hierarchy
system.membus = SystemXBar()
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = AddrRange('512MB')    
system.mem_ctrl.port = system.membus.mem_side_ports

#  CPU + Interrupts + Branch Predictor
system.cpu = DerivO3CPU()
system.cpu.createInterruptController()

# Connect interrupt ports
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.cpu.branchPred = TournamentBP()

# Connect CPU caches
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# Workload (SE mode)
binary = "workload"
if not os.path.isfile(binary):
    raise RuntimeError(f"Binary '{binary}' not found!")

process = Process()
process.cmd = [binary]

# Set workload
system.workload = SEWorkload.init_compatible(binary)
system.cpu.workload = process
system.cpu.createThreads()

# Root + trace + simulation
root = Root(full_system=False, system=system)
m5.instantiate()
m5.trace.activate("trace_bp_on.out")


print("=== Simulation start ===")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

