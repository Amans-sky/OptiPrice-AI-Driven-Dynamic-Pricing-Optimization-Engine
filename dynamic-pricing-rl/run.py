"""Entry point for training the DQN agent."""

import logging
from src.train_agent import train
from config import TRAINING_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info('=' * 70)
    logger.info('Starting Dynamic Pricing Optimization Training')
    logger.info(f'Episodes: {TRAINING_CONFIG["num_episodes"]}')
    logger.info('=' * 70)
    
    model, rewards = train()
    
    logger.info('✓ Training complete!')
