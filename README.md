# FTPEvals
Infrastructure for evaluating latest-gen LLMs &amp; Agents on Formal Theorem Proving Tasks.

Currently intended for only benchmark Lean 4; but the support technically extends to Isabelle 2023 and Coq 8.18.0+.

The benchmarks we currently include in the evaluation are PutnamBench, miniF2F (Harmonic), and miniCTX. 

**TODO**
1. Add all benchmarks and be sure about compatibility issues across Lean versions.
2. Add itp interface and test out (starting with PutnamBench)
3. Add support for drawing samples from Anthropic, OpenAI, Gemini
4. Add support for drawing samples from open-source models (vLLM)
5. Add checkpointing & logging mechanisms from COPRA
6. If you need to bump the Lean version, you need to do the following:
    - Update the Lean version in `imports/itp-interface/src/itp_interface/scripts/setup.sh`
    - Update the Lean version in `imports/repl/src/repl/scripts/setup.sh`
    - Update the Lean version in `imports/repl/src/repl/scripts/setup.sh`

**Eventually**
1. Add agentic framework and test out agentic models (for example with Gemini 2.0 Flash Experimental Thinking)
