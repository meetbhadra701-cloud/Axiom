# Makefile - Cocotb + Verilator
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
.DEFAULT_GOAL := sim
SIM_BUILD ?= /tmp/axiom-counter-sim_build
SDKROOT ?= $(shell xcrun --show-sdk-path 2>/dev/null)
export SDKROOT

empty :=
space := $(empty) $(empty)
escape_spaces = $(subst $(space),\$(space),$(1))

REPO_ROOT := $(call escape_spaces,$(CURDIR))
COCOTB_MAKEFILES := $(call escape_spaces,$(shell cocotb-config --makefiles))

VERILOG_SOURCES += $(REPO_ROOT)/rtl/counter.v
TOPLEVEL = counter
COCOTB_TEST_MODULES = test_counter

ifeq ($(SIM),verilator)
EXTRA_ARGS += --trace --trace-structs
endif

export PYTHONPATH := $(CURDIR)/tb:$(PYTHONPATH)

.PHONY: synth
synth:
	yosys -s synth/check.ys

include $(COCOTB_MAKEFILES)/Makefile.sim
