# Run this locally once
from huggingface_hub import HfApi, create_repo, login

# Login first
login(token="hf_#####")

api = HfApi()
repo_id = "mpm751/textvar-demo"

# Create model repo
create_repo(repo_id, repo_type="model", exist_ok=True)

# Upload weights
api.upload_file(
    path_or_fileobj="./checkpoints/ckpt_best.pth",
    path_in_repo="ckpt_best.pth",
    repo_id=repo_id
)
api.upload_file(
    path_or_fileobj="./checkpoints/vae_ch160v4096z32.pth",
    path_in_repo="vae_ch160v4096z32.pth",
    repo_id=repo_id
)