import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """
    A Singleton configuration manager for the Axiom-Alpha-Research-Lab.
    Dynamically resolves paths and caches YAML configurations in memory.
    """
    _instance = None
    _configs: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        # Implement Singleton pattern to ensure only one instance exists in memory
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Dynamically find the project root regardless of where the script is executed
        # Assuming this file is located at `Axiom-Alpha-Research-Lab/src/config_loader.py`
        self.root_dir = Path(__file__).resolve().parent.parent
        self.config_dir = self.root_dir / "config"

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Reads a YAML file and caches it. Returns the cached version if already loaded."""
        if filename in self._configs:
            return self._configs[filename]

        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"CRITICAL: Configuration file missing at {filepath}")

        with open(filepath, "r") as file:
            try:
                config_data = yaml.safe_load(file)
                self._configs[filename] = config_data
                return config_data
            except yaml.YAMLError as exc:
                raise ValueError(f"Error parsing YAML file {filename}: {exc}")

    # Properties act as clean, dot-notation accessors for the rest of your codebase
    @property
    def system(self) -> Dict[str, Any]:
        return self._load_yaml("system.yaml")

    @property
    def agent_params(self) -> Dict[str, Any]:
        return self._load_yaml("agent_params.yaml")

    @property
    def cluster_nodes(self) -> Dict[str, Any]:
        return self._load_yaml("cluster_nodes.yaml")

# Instantiate a global singleton object to be imported across the ecosystem
config = ConfigLoader()