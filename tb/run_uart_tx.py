import os
import sys
from pathlib import Path


try:
    from cocotb_tools.runner import get_runner
except ModuleNotFoundError:
    venv_python = Path("/tmp/axiom-cocotb-venv/bin/python")
    if venv_python.exists() and os.environ.get("AXIOM_UART_TX_RUNNER_REEXEC") != "1":
        env = os.environ.copy()
        env["AXIOM_UART_TX_RUNNER_REEXEC"] = "1"
        os.execve(venv_python, [str(venv_python), *sys.argv], env)
    raise


def main():
    repo = Path(__file__).resolve().parents[1]
    runner = get_runner("icarus")

    runner.build(
        sources=[repo / "rtl" / "uart_tx.v"],
        hdl_toplevel="uart_tx",
        build_dir="/tmp/axiom-uart_tx-sim_build",
        parameters={"CLKS_PER_BIT": 4, "CLKDIV_W": 2},
        timescale=("1ns", "1ps"),
        always=True,
    )

    runner.test(
        hdl_toplevel="uart_tx",
        test_module="test_uart_tx",
        build_dir="/tmp/axiom-uart_tx-sim_build",
        extra_env={"PYTHONPATH": str(repo / "tb")},
    )


if __name__ == "__main__":
    main()
