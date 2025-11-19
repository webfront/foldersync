import argparse
import sys
import logging
import os

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src import utils, backup
except ImportError:
    # Fallback for when running directly from src folder
    import utils
    import backup

def main():
    parser = argparse.ArgumentParser(description="Windows Folder Backup System")
    parser.add_argument("--run-backup", action="store_true", help="Run in CLI backup mode")
    # Future extension: parser.add_argument("--config", help="Path to config file")
    
    args = parser.parse_args()

    if args.run_backup:
        try:
            # Load Config
            # Assuming config.json is in the project root, relative to where script is run
            # Or we can determine it relative to this file. 
            # Spec says "Default location: project root (same folder as src)"
            # If we run from project root: python src/main.py, then config.json is in .
            
            config_path = "config.json"
            config = utils.load_config(config_path)
            
            # Setup Logging
            utils.setup_logging(config)
            
            logger = logging.getLogger(__name__)
            logger.info("Starting Backup System in CLI Mode")
            
            # Run Backups
            exit_code = backup.run_all_backups(config)
            
            logger.info("Backup run finished.")
            sys.exit(exit_code)
            
        except Exception as e:
            # Fallback logging if setup_logging failed or other critical error
            print(f"Critical Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("GUI mode not implemented yet. Use --run-backup to run backups.")
        # In future, this would launch the GUI
        sys.exit(0)

if __name__ == "__main__":
    main()
