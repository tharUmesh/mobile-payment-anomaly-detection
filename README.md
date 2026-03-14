# Large-Scale Anomaly Detection in Mobile Payment Networks

Distributed fraud-pattern detection on mobile payment transactions using Apache Hadoop Streaming and Python MapReduce.

## Team and Module

- Team Members: Kanishka Praveen, Levindu Tharusha, Tharun Umesh
- Module: EC7204 Cloud Computing

## Project Overview

This project implements a scalable MapReduce pipeline to detect suspicious behavioral patterns in mobile payment flows using the PaySim dataset (6.3M+ rows). The pipeline uses:

- `src/mapper.py` to extract transaction events keyed by source account.
- `src/reducer.py` to aggregate per-account activity in time order and apply anomaly heuristics.

The system is designed to run:

- Locally for functional validation on sample data.
- On Hadoop (pseudo-distributed or cluster mode) for large-scale processing.

## Detection Logic

The reducer currently flags three anomaly families:

1. Transfer-then-Cash-Out Pivot
	 - Pattern: `TRANSFER` followed by `CASH_OUT`
	 - Rule: second transaction occurs within 2 steps and transfer amount is at least 200000
2. High-Velocity Depletion
	 - Pattern: rapid sequence draining account balance to `0.0`
	 - Rule: at least 3 transactions and the full sequence happens within 1 step
3. Scattering Pattern
	 - Pattern: one account sends to many destinations quickly
	 - Rule: at least 5 distinct destination accounts within 3 steps

Output format:

`<account_id>\tANOMALY: <description>`

## Repository Structure

```text
mobile-payment-anomaly-detection/
|- data/
|  |- sample_data.csv                         # Small local test dataset
|  |- PS_20174392719_1491204439457_log.csv   # Full PaySim dataset (local use)
|- docs/                                      # Supporting documentation/report assets
|- src/
|  |- mapper.py                               # Emits key-value records by source account
|  |- reducer.py                              # Groups, sorts, and applies anomaly rules
|- commands.txt                               # Useful local test commands
|- requirements.txt                           # Python dependencies (currently none)
`- README.md
```

## Dataset

This project uses the synthetic PaySim transaction dataset:

- Name: `PS_20174392719_1491204439457_log.csv`
- Source: Kaggle (PaySim)
- Scale: 6.3M+ transaction records (hundreds of MB)

Important:

- Large raw datasets should not be committed to GitHub due to storage and performance constraints.
- Keep the full CSV in your local `data/` directory for processing.

## Prerequisites

Required:

- Python 3.x
- Apache Hadoop 3.x
- Java 8 or 11

Recommended:

- GNU sort (Linux/macOS) or PowerShell `Sort-Object` (Windows)
- Sufficient disk space for HDFS input/output

## Quick Start

### 1) Local Pipeline Test (No Hadoop)

Run end-to-end on `data/sample_data.csv`.

Linux/macOS:

```bash
cat data/sample_data.csv | python3 src/mapper.py | sort | python3 src/reducer.py
```

Windows PowerShell:

```powershell
Get-Content data\sample_data.csv | python src\mapper.py | Sort-Object | python src\reducer.py
```

This validates:

- Mapper parsing and key emission
- Sort/shuffle simulation
- Reducer anomaly detection rules

### 2) Hadoop Streaming Execution (Full Dataset)

Ensure Hadoop services are active (`NameNode`, `DataNode`, `ResourceManager`, `NodeManager`).

Step A: Create HDFS input path and upload data

```bash
hdfs dfs -mkdir -p /paysim/input
hdfs dfs -put data/PS_20174392719_1491204439457_log.csv /paysim/input/
```

Step B: Run streaming job

```bash
hadoop jar /path/to/hadoop-streaming.jar \
	-files src/mapper.py,src/reducer.py \
	-mapper "python3 mapper.py" \
	-reducer "python3 reducer.py" \
	-input /paysim/input/PS_20174392719_1491204439457_log.csv \
	-output /paysim/output
```

Notes:

- Replace `/path/to/hadoop-streaming.jar` with your real Hadoop streaming JAR path.
- If `/paysim/output` already exists, remove it first:

```bash
hdfs dfs -rm -r /paysim/output
```

Step C: View output

```bash
hdfs dfs -cat /paysim/output/part-00000 | head -n 20
```

## Command Reference

Quick mapper-only check:

```powershell
Get-Content data\sample_data.csv | python src\mapper.py
```

Quick full local flow:

```powershell
Get-Content data\sample_data.csv | python src\mapper.py | Sort-Object | python src\reducer.py
```

These are also listed in `commands.txt`.

## Implementation Notes

- Mapper skips empty lines and CSV header.
- Mapper emits only rows with expected PaySim column count (11 fields).
- Reducer assumes mapper output is globally sorted by key.
- Reducer uses secondary in-memory sorting per account by `(step asc, newbalance desc)`.
- Reducer prints one anomaly alert per account (exits early after first matching rule for some patterns).

## Limitations

- Current parser uses a simple comma split and does not handle quoted commas in CSV fields.
- Detection is rule-based (heuristic), not ML-based.
- Thresholds are static and may require tuning for different datasets.

## Troubleshooting

- No reducer output locally:
	- Ensure sorting occurs between mapper and reducer.
	- Confirm sample data contains records matching rule thresholds.
- Hadoop job fails on existing output path:
	- Delete previous output directory in HDFS before rerun.
- Python executable mismatch on cluster nodes:
	- Verify `python3` availability on all worker nodes, or adjust mapper/reducer command.

## Suggested Enhancements

- Add configurable thresholds via environment variables or command-line arguments.
- Add unit tests for each anomaly strategy.
- Add precision/recall evaluation against labeled fraud subsets.
- Add Spark implementation for performance comparison.

## License and Academic Use

This repository is intended for educational use under EC7204. If you distribute this project, include proper dataset attribution and respect Kaggle dataset usage policies.
