# LangChain + OCI Generative AI 
Small, focused Python scripts that exercise the LangChain OCI chat connector. Each example defaults to openai.gpt-4o but keeps alternative model IDs commented so you can swap providers quickly.

# LangGraph
This repository demonstrates how to leverage LangGraph for simple tool-calling agents

# AI Orchestration Examples

This repository collects small projects that explore orchestration patterns for large-language-model agents. 
The main active area is `experiments/llm-tooling-benchmarks`, which measures how different LLMs perform when they
must autonomously call tools end to end.

If you want to see how LangChain integrates with OCI Generative AI (including model switching, tool-calling math, and structured-output examples), check the quick-start scripts documented in `langchain/README.md`.

## LLM Tooling Benchmarks Overview

This evaluates how different language models handle autonomous tool execution. 
Each experiment samples a collection of tools, asks every configured LLM to run them, and records four primary signals.

- <img src="experiments/llm-tooling-benchmarks/charts/merge1/avg_tools_called.png" alt="Average tools called" width="50%">  
