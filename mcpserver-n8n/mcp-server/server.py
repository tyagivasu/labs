import os, glob, tiktoken, requests, zipfile, io
from openai import OpenAI
from fastmcp import FastMCP
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO)

# openai.api_key = os.getenv("OPENAI_API_KEY") #set env var
client = OpenAI()
mcp = FastMCP("Pipeline-Log-Analyser")


github_token = os.environ.get("GITHUB_TOKEN")
# owner = "your-org"  # sender
# repo = "your-repo"  # repo_name
# run_id = 123456789  # pipeline_id

def getGitHubActionRunsLogs(owner,repo,run_id):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/logs"
    headers = {"Authorization": f"Bearer {github_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # 🔧 Build path: logs/<repo_name>/pipeline_<id>
        log_dir = os.path.join("logs", repo, f"pipeline_{run_id}")
        os.makedirs(log_dir, exist_ok=True)
        # ✅ Extract zip content into the log directory
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            zip_file.extractall(log_dir)
            logging.info("✅ Logs downloaded to {log_dir}")
    else:
        logging.info("❌ Failed to fetch logs:", response.status_code)

@mcp.tool
def load_pipeline_logs(pid: str, owner: str, repo: str, budget_tokens=6_000) -> str:
    """
    Read *.log or *.txt under ./logs/pipeline_<pid>/, keep newest first,
    trim so the prompt stays under budget_tokens.
    """
    # get pipeline logs
    getGitHubActionRunsLogs(owner, repo, run_id=pid)

    files = sorted(
        glob.glob(f"./logs/{repo}/pipeline_{pid}/**/*.*", recursive=True),
        key=os.path.getmtime,
        reverse=True,
    )
    enc = tiktoken.encoding_for_model("gpt-4o")       # tokeniser
    tokens, chunks = 0, []

    for fp in files:
        txt = open(fp, "r", errors="ignore").read()
        delta = len(enc.encode(txt))
        if tokens + delta > budget_tokens:
            break
        chunks.append(f"\n##### {os.path.basename(fp)}\n{txt}")
        tokens += delta
    return "\n".join(chunks) or "(no logs found)"

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"


if __name__ == "__main__":
    print("✅ Running Pipeline-Log-Analyser")
    mcp.run(
      transport="sse",
      host="0.0.0.0"
    )