import pytest
import torch
from unittest.mock import patch, MagicMock
from src.engine.callbacks import AxiomLoggingCallback

@patch('src.engine.callbacks.mlflow')
@patch('src.engine.callbacks.telemetry')
def test_axiom_logging_callback_on_epoch_end(mock_telemetry, mock_mlflow):
    """
    Verifies that the PyTorch Lightning callback correctly routes 
    Sharpe ratios to MLflow and Risk metrics to MongoDB.
    """
    # 1. Initialize our custom callback
    callback = AxiomLoggingCallback()
    
    # 2. Mock the PyTorch Lightning Trainer and its metrics
    mock_trainer = MagicMock()
    mock_trainer.current_epoch = 5
    mock_trainer.callback_metrics = {
        "train_sharpe": torch.tensor(1.85), 
        "val_drawdown": torch.tensor(0.12)
    }
    
    mock_pl_module = MagicMock()
    
    # 3. Simulate the end of a training epoch
    callback.on_train_epoch_end(mock_trainer, mock_pl_module)
    
    # 4. Assert MLflow recorded the Sharpe Ratio
    mock_mlflow.log_metric.assert_called_with("epoch_sharpe", 1.85, step=5)
    
    # 5. Assert MongoDB received the risk payload for the live dashboard
    mock_telemetry.log_portfolio_risk.assert_called_once()
    
    # Extract the arguments passed to MongoDB to ensure accuracy
    call_kwargs = mock_telemetry.log_portfolio_risk.call_args.kwargs
    assert call_kwargs['timestamp'] == 5
    assert call_kwargs['sharpe_ratio'] == 1.85
    assert call_kwargs['current_drawdown'] == 0.12

@patch('src.engine.callbacks.push_to_notion')
@patch('src.engine.callbacks.mlflow')
def test_axiom_logging_callback_on_fit_end(mock_mlflow, mock_push_to_notion):
    """
    Verifies that when training completely finishes, the final results 
    are automatically pushed to your Notion Sprint board.
    """
    callback = AxiomLoggingCallback()
    
    mock_trainer = MagicMock()
    mock_trainer.callback_metrics = {"val_sharpe": torch.tensor(2.1)}
    
    mock_pl_module = MagicMock()
    mock_pl_module.__class__.__name__ = "LowerExecutionAgent"
    
    # Mock MLflow's active run ID
    mock_run = MagicMock()
    mock_run.info.run_id = "12345_abcde"
    mock_mlflow.active_run.return_value = mock_run

    # Simulate the end of the entire training `.fit()` execution
    callback.on_fit_end(mock_trainer, mock_pl_module)
    
    # Assert the Notion integration script was fired with the correct payload
    mock_push_to_notion.assert_called_once()
    payload = mock_push_to_notion.call_args[0][0]
    
    assert payload['Model'] == "LowerExecutionAgent"
    assert payload['Final Sharpe'] == 2.1
    assert payload['MLflow Run ID'] == "12345_abcde"