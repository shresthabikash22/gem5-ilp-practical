# part4_smt.py
system.cpu = DerivO3CPU()
system.cpu.numThreads = 2

# Two workloads
process1 = Process(cmd=['hello'])
process2 = Process(cmd=['hello'])

system.cpu.workload = [process1, process2]
system.cpu.createThreads()