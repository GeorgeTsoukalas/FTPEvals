# FTPEvals
Infrastructure for evaluating latest-gen LLMs & Agents on Formal Theorem Proving Tasks. (PutnamBench at present.)

Currently intended for only benchmark Lean 4; but the support technically extends to Isabelle 2023 and Coq 8.18.0+.

## Setup

1. Create and activate the conda environment:
```bash
conda create -n ftpevals python=3.11
conda activate ftpevals
```

2. Make sure that the `python` command points to the correct version:
```bash
which python
```
If it doesn't point to the correct version, you may need to update the `python` symlink:
```bash
sudo ln -sf <conda_path>/envs/ftpevals/bin/python /usr/bin/python
```

3. Make sure to install pip:
```bash
python -m ensurepip
```

4. Ensure that the `pip` command points to the correct version:
```bash
which pip
```
If it doesn't point to the correct version, you may need to update the `pip` symlink:
```bash
sudo ln -sf <conda_path>/envs/ftpevals/bin/pip /usr/bin/pip
```

5. Run the setup script:
```bash
./setup.sh
```


6. Set up API keys:
Create a file named `secrets/openai.key` in with the key for the OpenAI API.
Similarly, for other APIs, create files named `secrets/<provider_name>.key` with the key for the respective API.

