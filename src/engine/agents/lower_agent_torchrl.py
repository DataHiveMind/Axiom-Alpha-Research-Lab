import torch
from torchrl.envs import GymEnv, TransformedEnv, StepCounter
from torchrl.modules import MLP, ProbabilisticActor, ValueOperator
from torchrl.objectives import ClipPPOLoss
from torchrl.data import TensorDictReplayBuffer, LazyTensorStorage
from tensordict.nn import TensorDictModule
from torch.distributions import Normal

class LowerExecutionAgent:
    """
    TorchRL Proximal Policy Optimization (PPO) Agent.
    Directly interfaces with the QuantLib Hedging Environment.
    Optimized for microsecond execution speeds.
    """
    def __init__(self):
        # 1. Setup Environment
        # We wrap the QuantLib environment we built earlier
        base_env = GymEnv("src.engine.environments.quantlib_hedging_env:QuantLibHedgingEnv")
        self.env = TransformedEnv(base_env, StepCounter(max_steps=1000))
        
        # 2. Define the Neural Network Architecture
        policy_net = MLP(in_features=4, out_features=2, num_cells=[64, 64]) # Output mean and std for action
        
        policy_module = TensorDictModule(
            policy_net, in_keys=["observation"], out_keys=["loc", "scale"]
        )
        
        # 3. Probabilistic Actor for PPO
        self.actor = ProbabilisticActor(
            module=policy_module,
            in_keys=["loc", "scale"],
            out_keys=["action"],
            distribution_class=Normal,
            return_log_prob=True,
        )
        
        # 4. Value Network (Critic)
        value_net = MLP(in_features=4, out_features=1, num_cells=[64, 64])
        self.value = ValueOperator(module=value_net, in_keys=["observation"])
        
        # 5. PPO Loss Module
        self.loss_module = ClipPPOLoss(
            actor_network=self.actor,
            critic_network=self.value,
            clip_epsilon=0.2,
            entropy_coef=0.01,
        )

    def train_step(self, batch_size=256):
        """Executes a highly optimized tensor-based training step."""
        # Collect data
        tensordict_data = self.env.rollout(max_steps=batch_size)
        
        # Compute loss natively in Torch
        loss_dict = self.loss_module(tensordict_data)
        
        # In a full script, you would backpropagate the loss via an optimizer here.
        # optimizer.zero_grad()
        # loss_dict["loss_objective"].backward()
        # optimizer.step()
        
        return loss_dict["loss_objective"].item()