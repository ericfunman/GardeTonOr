import os
import sys
import time
import requests
import subprocess
import argparse

# Configuration
REPO_OWNER = "ericfunman"
REPO_NAME = "GardeTonOr"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

def get_current_branch():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: Could not determine current git branch.")
        sys.exit(1)

def get_latest_run(branch, token=None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    url = f"{GITHUB_API_URL}/actions/runs"
    params = {"branch": branch, "per_page": 1}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data["workflow_runs"]:
            return None
            
        return data["workflow_runs"][0]
    except requests.exceptions.RequestException as e:
        print(f"Error querying GitHub API: {e}")
        if response.status_code == 404:
            print("Repo not found. If it is private, make sure to provide a GITHUB_TOKEN.")
        elif response.status_code == 401:
            print("Unauthorized. Please check your GITHUB_TOKEN.")
        sys.exit(1)

def monitor_run(run_id, token=None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
        
    url = f"{GITHUB_API_URL}/actions/runs/{run_id}"
    
    print(f"Monitoring Workflow Run ID: {run_id}")
    print(f"URL: https://github.com/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}")
    
    while True:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            status = data["status"]
            conclusion = data["conclusion"]
            
            sys.stdout.write(f"\rStatus: {status}...")
            sys.stdout.flush()
            
            if status in ["completed", "failure", "cancelled", "skipped", "timed_out"]:
                print(f"\nFinal Result: {conclusion.upper()}")
                if conclusion == "success":
                    sys.exit(0)
                else:
                    get_failure_details(run_id, token)
                    sys.exit(1)
            
            time.sleep(5)
            
        except requests.exceptions.RequestException as e:
            print(f"\nError polling run status: {e}")
            time.sleep(10)

def get_failure_details(run_id, token=None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"{GITHUB_API_URL}/actions/runs/{run_id}/jobs"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("\n--- Failure Details ---")
        for job in data.get("jobs", []):
            if job["conclusion"] == "failure":
                print(f"\nJob: {job['name']}")
                for step in job.get("steps", []):
                    if step["conclusion"] == "failure":
                        print(f"  ❌ Step failed: {step['name']}")
                        # We can't easily get the full log via this API without downloading a zip
                        # But we can try to get annotations if any
    except Exception as e:
        print(f"Could not fetch failure details: {e}")

def main():
    parser = argparse.ArgumentParser(description="Check GitHub Actions status for the current branch.")
    parser.add_argument("--token", help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--watch", action="store_true", help="Poll until the workflow completes")
    args = parser.parse_args()

    token = args.token or os.environ.get("GITHUB_TOKEN")
    branch = get_current_branch()
    
    print(f"Checking CI status for branch: {branch}")
    
    # Wait a moment for GitHub to register the new run if we just pushed
    print("Fetching latest run...")
    
    run = get_latest_run(branch, token)
    
    if not run:
        print("No workflow runs found for this branch.")
        return

    print(f"Latest Run: {run['name']} (#{run['run_number']})")
    print(f"Commit: {run['head_commit']['message']}")
    print(f"Status: {run['status']}")
    if run['conclusion']:
        print(f"Conclusion: {run['conclusion']}")
        if run['conclusion'] == "failure":
            get_failure_details(run['id'], token)
    
    if args.watch and run['status'] not in ["completed"]:
        monitor_run(run['id'], token)

if __name__ == "__main__":
    main()
