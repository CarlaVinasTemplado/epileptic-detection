from pathlib import Path

import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers import WandbLogger
from tsai.models.FCNPlus import FCNPlus
from tsai.models.ResCNN import ResCNN
from tsai.models.InceptionTimePlus import InceptionBlockPlus
from tsai.models.MLP import MLP
from tsai.models.TransformerModel import TransformerModel
from tsai.models.RNNPlus import GRUPlus, LSTMPlus

#from tsai.models.TransformerPlus import TransformerPlus

from src.deep_learning.data.datamodule import DataModule
from src.deep_learning.models.lightning_module import LightningModule

import optuna

class HyperparameterOptimization:

    def __init__(self, root_data_dir):
        self.root_data_dir = root_data_dir

    def objective(self,trial):
        """
        Objective function to be optimized.
        """

        # Create datamodule
        BATCH_SIZE = trial.suggest_int("batch_size", 8, 32)
        print(BATCH_SIZE)
        dm = DataModule(self.root_data_dir, batch_size=BATCH_SIZE)
        dm.setup()

        # Choose model
        #MODEL_NAME = trial.suggest_categorical("model", ["FCNPlus", "ResCNN", "InceptionBlockPlus", "MLP", "TransformerModel", "GRUPlus", "LSTMPlus"])

        # if MODEL_NAME == "FCNPlus":
        #     model = FCNPlus(21, 2)
        # elif MODEL_NAME == "ResCNN":
        #     model = ResCNN(21, 2)
        # elif MODEL_NAME == "InceptionBlockPlus":
        #     model = InceptionBlockPlus(21, 2)
        # elif MODEL_NAME == "MLP":
        #     model = MLP(21, 2)
        # elif MODEL_NAME == "TransformerModel":
        #     model = TransformerModel(21, 2)
        # elif MODEL_NAME == "GRUPlus":
        #     model = GRUPlus(21, 2)
        # elif MODEL_NAME == "LSTMPlus":
        #     model = LSTMPlus(21, 2)
        # else:
        #     raise ValueError(f"Model {MODEL_NAME} not supported.")

        model = FCNPlus(21, 2)

        # Create LightningModule
        num_classes = 2
        LEARNING_RATE = trial.suggest_loguniform("learning_rate", 1e-5, 1e-1)
        model = LightningModule(model, num_classes=num_classes, learning_rate=LEARNING_RATE)

        # Logger
        wandb_logger = None # WandbLogger(project='epileptic-detection', job_type='train')

        # Callbacks
        callbacks = [
            # EarlyStopping(monitor="val_loss", min_delta=0.00, patience=3, verbose=False, mode="max"),
            # LearningRateMonitor(),
            ModelCheckpoint(dirpath="./checkpoints", monitor="val_loss", filename="model_{epoch:02d}_{val_loss:.2f}")
        ]

        # Create trainer
        trainer = pl.Trainer(max_steps=1000,
                            val_check_interval=500,
                            gpus=0,
                            logger=wandb_logger,
                            callbacks=callbacks,
                            enable_progress_bar=True)

        trainer.fit(model, dm)

        return model.min_loss

if __name__ == "__main__":
    root_data_dir = Path("../data/").resolve()
    opt = HyperparameterOptimization(root_data_dir)
    study = optuna.create_study(direction="minimize")
    study.optimize(opt.objective, n_trials=100)
    print(study.best_trial)
    
