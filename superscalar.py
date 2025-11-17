# superscalar.py (default 4-wide)
system.cpu = DerivO3CPU()
system.cpu.issueWidth = 4
system.cpu.dispatchWidth = 4