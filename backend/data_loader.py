"""
Data loader for OPD training datasets.
Loads JSONL files with chat-formatted prompts for distillation.
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datasets import Dataset
import logging

logger = logging.getLogger(__name__)

class OPDDataLoader:
    """Loads and prepares datasets for on-policy distillation"""

    def __init__(self, dataset_path: str):
        """
        Initialize data loader.

        Args:
            dataset_path: Path to JSONL file with chat messages
        """
        self.dataset_path = Path(dataset_path)
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    def load_jsonl(self) -> List[Dict]:
        """Load JSONL file and parse messages"""
        samples = []
        with open(self.dataset_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    sample = json.loads(line)
                    if 'messages' in sample:
                        samples.append(sample)
                    else:
                        logger.warning(f"Line {line_num}: Missing 'messages' key")
                except json.JSONDecodeError as e:
                    logger.error(f"Line {line_num}: JSON parse error: {e}")
        return samples

    def validate_messages(self, samples: List[Dict]) -> List[Dict]:
        """Validate message structure"""
        valid_samples = []
        for i, sample in enumerate(samples):
            messages = sample.get('messages', [])
            if not messages:
                logger.warning(f"Sample {i}: No messages")
                continue

            # Check message structure
            valid = True
            for msg in messages:
                if 'role' not in msg or 'content' not in msg:
                    logger.warning(f"Sample {i}: Invalid message structure")
                    valid = False
                    break

            if valid:
                valid_samples.append(sample)

        return valid_samples

    def create_dataset(
        self,
        train_test_split: float = 0.9,
        max_samples: Optional[int] = None
    ) -> Tuple[Dataset, Dataset]:
        """
        Create HuggingFace datasets.

        Args:
            train_test_split: Fraction of data for training (default 0.9)
            max_samples: Maximum samples to load (for testing)

        Returns:
            (train_dataset, test_dataset)
        """
        # Load and validate
        samples = self.load_jsonl()
        samples = self.validate_messages(samples)

        if not samples:
            raise ValueError("No valid samples found in dataset")

        # Limit samples if requested
        if max_samples:
            samples = samples[:max_samples]

        # Split
        split_idx = int(len(samples) * train_test_split)
        train_samples = samples[:split_idx]
        test_samples = samples[split_idx:]

        # Convert to HF datasets
        train_dataset = Dataset.from_list(train_samples)
        test_dataset = Dataset.from_list(test_samples) if test_samples else None

        logger.info(f"Loaded {len(samples)} total samples")
        logger.info(f"Train: {len(train_samples)}, Test: {len(test_samples)}")

        return train_dataset, test_dataset

    def get_statistics(self) -> Dict:
        """Get dataset statistics"""
        samples = self.load_jsonl()
        samples = self.validate_messages(samples)

        if not samples:
            return {"error": "No valid samples"}

        # Calculate stats
        total_messages = sum(len(s['messages']) for s in samples)
        avg_messages = total_messages / len(samples)

        # System message count
        has_system = sum(1 for s in samples if any(m['role'] == 'system' for m in s['messages']))

        return {
            "total_samples": len(samples),
            "total_messages": total_messages,
            "avg_messages_per_sample": round(avg_messages, 1),
            "samples_with_system_message": has_system,
            "dataset_path": str(self.dataset_path)
        }


def main():
    """Test data loader"""
    import sys

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Test file
    test_file = Path(__file__).parent / "data" / "on_policy_prompts_test.jsonl"

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        sys.exit(1)

    print(f"Testing data loader with: {test_file}\n")

    # Load data
    loader = OPDDataLoader(str(test_file))

    # Get statistics
    stats = loader.get_statistics()
    print("📊 Dataset Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Create datasets
    print("\n📚 Creating train/test datasets...")
    train_ds, test_ds = loader.create_dataset(max_samples=5)

    print(f"✅ Train dataset: {len(train_ds)} samples")
    if test_ds:
        print(f"✅ Test dataset: {len(test_ds)} samples")

    # Show sample
    print("\n📝 Sample from training set:")
    sample = train_ds[0]
    for i, msg in enumerate(sample['messages']):
        role = msg['role']
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"   Message {i+1} [{role}]: {content}")

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
