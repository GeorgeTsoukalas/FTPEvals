# FTPEvals
Infrastructure for evaluating latest-gen LLMs & Agents on Formal Theorem Proving Tasks. (PutnamBench at present.)

Currently intended for only benchmark Lean 4; but the support technically extends to Isabelle 2023 and Coq 8.18.0+.

## Setup

1. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate ftpevals
```

Follow the setup instructions for the `itp-interface` package (see [here](https://github.com/trishullab/itp-interface)).

2. Set up API keys:
Create a `.env` file or set environment variables for:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `DEEPSEEK_API_KEY`


