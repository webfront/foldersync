import subprocess
import logging
import os
from typing import List, Dict

logger = logging.getLogger(__name__)

def build_robocopy_command(task: Dict, robocopy_options: Dict) -> List[str]:
    """
    Constructs the robocopy command list for subprocess.run.
    """
    source = task.get("source")
    destination = task.get("destination")
    backup_type = task.get("backup_type", "full")
    exclude = task.get("exclude", [])
    
    retry_count = robocopy_options.get("retry_count", 3)
    wait_time = robocopy_options.get("wait_time", 5)

    cmd = ["robocopy", source, destination]

    # Backup Type
    if backup_type == "full":
        cmd.append("/MIR")
    elif backup_type == "incremental":
        cmd.append("/E")
    
    # Common Flags
    # /Z: restartable, /TS: timestamp, /NP: no progress, /NDL: no dir list, /NFL: no file list
    cmd.extend(["/Z", "/TS", "/NP", "/NDL", "/NFL"])

    # Retry Options
    cmd.append(f"/R:{retry_count}")
    cmd.append(f"/W:{wait_time}")

    # Exclusions
    # Separating directories and files for exclusion is tricky without knowing if the pattern is a file or dir.
    # The spec says:
    # "For directories: mapped to /XD arguments."
    # "For files/patterns: mapped to /XF arguments (if implemented)."
    # Since we don't know for sure, we can try to guess or just use /XD for now as per spec example or
    # maybe implement a simple heuristic. 
    # However, standard robocopy usage often separates them. 
    # Let's assume 'exclude' contains directory names for /XD as that's the most common use case for folder sync.
    # If the user provides file extensions (e.g. *.tmp), we should probably use /XF.
    
    excluded_dirs = []
    excluded_files = []
    
    for item in exclude:
        # Simple heuristic: if it looks like a file extension or has a dot, treat as file pattern?
        # Or just put everything in /XD if no clear distinction? 
        # The spec says "For directories: mapped to /XD... For files: mapped to /XF".
        # Let's support both if we can distinguish. 
        # For now, let's assume if it starts with * it's a file pattern.
        if item.startswith("*") or "." in item:
             excluded_files.append(item)
        else:
             excluded_dirs.append(item)

    if excluded_dirs:
        cmd.append("/XD")
        cmd.extend(excluded_dirs)
    
    if excluded_files:
        cmd.append("/XF")
        cmd.extend(excluded_files)

    return cmd

def run_backup_task(task: Dict, robocopy_options: Dict) -> bool:
    """
    Runs a single backup task. Returns True if successful (exit code < 8), False otherwise.
    """
    name = task.get("name", "Unnamed Task")
    source = task.get("source")
    destination = task.get("destination")

    logger.info(f"Starting task: {name}")
    logger.info(f"Source: {source}")
    logger.info(f"Destination: {destination}")

    if not os.path.exists(source):
        logger.error(f"Source directory does not exist: {source}")
        return False

    # Create destination if it doesn't exist (Robocopy usually does this, but good to be safe/explicit)
    if not os.path.exists(destination):
        try:
            os.makedirs(destination)
        except OSError as e:
            logger.error(f"Failed to create destination directory: {e}")
            return False

    cmd = build_robocopy_command(task, robocopy_options)
    logger.info(f"Command: {' '.join(cmd)}")

    try:
        # check=False because robocopy returns non-zero for success (1-7)
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        
        return_code = result.returncode
        logger.info(f"Robocopy return code: {return_code}")
        
        if return_code >= 8:
            logger.error(f"Task failed with return code {return_code}")
            logger.error(f"Stdout: {result.stdout}")
            logger.error(f"Stderr: {result.stderr}")
            return False
        else:
            logger.info(f"Task completed successfully (Code {return_code})")
            return True

    except Exception as e:
        logger.error(f"An error occurred while executing robocopy: {e}")
        return False

def run_all_backups(config: Dict) -> int:
    """
    Runs all configured backup tasks. Returns 0 if all success, 1 if any failure.
    """
    tasks = config.get("backup_tasks", [])
    robocopy_options = config.get("robocopy_options", {})
    
    failed_tasks = 0
    
    for task in tasks:
        success = run_backup_task(task, robocopy_options)
        if not success:
            failed_tasks += 1
            
    if failed_tasks == 0:
        logger.info("All backup tasks completed successfully.")
        return 0
    else:
        logger.error(f"{failed_tasks} task(s) failed.")
        return 1
