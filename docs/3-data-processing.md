# data processing

This document describes the first step in the analysis pipeline: deriving embeddings from audio data using a pretrained Perch v2 model running on CPUs.

## Overview

We use the [perch-cpu-inference](https://github.com/nilomr/perch-cpu-inference) repository to extract acoustic embeddings from audio files. This tool runs Google's Perch v2 model on CPUs for very high-performance inference, producing 1536-dimensional embeddings for each 5-second audio chunk.

### Features

- Processes audio at up to ~800~x realtime speed using ONNX or TFLite
- Handles large-scale datasets with batch processing and checkpointing
- Outputs embeddings in Parquet format and species predictions in CSV
- Supports background processing for long-running jobs

## Requirements

- **Hardware**: A system with at least 16 CPU cores and 32 GB RAM is recommended for optimal performance. The implementation is optimized for low memory usage, making it suitable for modern servers or high-end workstations.
- **Scalability**: The process is non-blocking and scales with available resources; it will run slower on systems with fewer cores or RAM but remains functional. Scaling is linear in terms of dataset size, while different hardware configurations and batch sizes will affect throughput in a non-linear manner (see Performance section below and [perch-cpu-inference docs](https://github.com/nilomr/perch-cpu-inference/blob/main/docs/usage.md#performance).)

## Installation and setup

Follow the [installation guide](https://github.com/nilomr/perch-cpu-inference/blob/main/docs/usage.md#installation) in the repository. You'll likely need to wrestle with some dependencies, I've kept the environment as minimal as possible.

Download the ONNX model:
```bash
wget https://huggingface.co/justinchuby/Perch-onnx/resolve/main/perch_v2.onnx -P models/perch_v2/
```

## Running inference

For single directories:
```bash
python scripts/inference/perch-onnx-inference.py --audio-dir /path/to/audio --output-dir /path/to/output
```

For batch processing multiple sites:
```bash
./tools/run_inference.sh /path/to/audio/directories /path/to/output
```

## Output

- **Embeddings**: Parquet files with 1536-dimensional vectors per 5s chunk
- **Predictions**: CSV files with top-10 species predictions per chunk

## Monitoring and logs

Use the monitoring tools to track progress:
```bash
./tools/monitor.sh          # Live log following
./tools/monitor.sh status   # Progress summary
```

Parse logs for analysis:
```bash
./tools/parse_inference_log.sh /path/to/inference.log
```

## Performance

Typical throughput: 5-15 files/second (300-900x realtime) depending on configuration.

For detailed benchmarks and configuration options, see the [usage guide](https://github.com/nilomr/perch-cpu-inference/blob/main/docs/usage.md) and [batch processing guide](https://github.com/nilomr/perch-cpu-inference/blob/main/docs/batch-processing.md).
