# LangChain + OCI Generative AI Examples

Small, focused Python scripts that exercise the LangChain OCI chat connector. Each example defaults to `openai.gpt-4o` but keeps alternative model IDs commented so you can swap providers quickly.

Key docs:
- https://docs.oracle.com/en-us/iaas/Content/generative-ai/langchain.htm
- https://pypi.org/project/langchain-oci/
- https://python.langchain.com/api_reference/community/chat_models/langchain_community.chat_models.oci_generative_ai.ChatOCIGenAI.html

## Local Configuration
1. Copy `oci_config_template.py` → `oci_config.py`.
2. Set `COMPARTMENT_ID` to the OCID of the compartment that hosts your Generative AI resources.
3. Set `SERVICE_ENDPOINT` to your regional Generative AI inference endpoint (for example `https://inference.generativeai.us-chicago-1.oci.oraclecloud.com`).
   - You can find the endpoint in the OCI Console under **Generative AI → Model Endpoints**.

### Getting Your OCI profile (.oci directory)
1. In the OCI Console go to **Profile (top-right avatar) → My profile → API Keys**.
2. Click **Add API Key** → **Download private key & config file**. This creates a `.oci` folder containing `config` and the private key.
3. Move the downloaded `.oci` directory to your home folder (e.g. `~/.oci/`). The included `config` file contains your tenancy OCID, user OCID, region, and fingerprint—copy the compartment OCID from the console as described above.

## Example Scripts
- `ex01_model_switching.py` – instantiate ChatOCIGenAI and send a Moon fact prompt, ready to swap model IDs.
- `ex02_tools_math.py` – run a tool-calling math agent that adds numbers and verifies the result.
- `ex03_tools_structured_output.py` – extract structured fields from a short bio via `with_structured_output`.
- `ex04_tools_summary.py` – compare different LangChain tool declarations and their generated schemas.
