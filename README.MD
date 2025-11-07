# AI Orchestration Examples

This repository collects small projects that explore orchestration patterns for large-language-model agents. 
The main active area is `experiments/llm-tooling-benchmarks`, which measures how different LLMs perform when they
must autonomously call tools end to end.

## LLM Tooling Benchmarks Overview

This evaluates how different language models handle autonomous tool execution. 
Each experiment samples a collection of tools, asks every configured LLM to run them, and records four primary signals.

- <img src="experiments/llm-tooling-benchmarks/charts/merge1/avg_tools_called.png" alt="Average tools called" width="50%">  
