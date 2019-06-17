import logging
from mlagents.trainers.trainer import UnityTrainerException
from mlagents.trainers.policy import Policy
import numpy as np
import abc

import tensorflow as tf

logger = logging.getLogger("mlagents.trainers")


class RewardSignal(abc.ABC):
    value_name = "Policy/{} Value Estimate".format(__name__)
    stat_name = "Policy/{} Reward".format(__name__)

    @abc.abstractmethod
    def __init__(self, policy: Policy, strength, gamma):
        """
        Initializes a reward signal. At minimum, you must pass in the policy it is being applied to, 
        the reward strength, and the gamma (discount factor.)
        :param policy: The Policy object (e.g. PPOPolicy) that this Reward Signal will apply to. 
        :param strength: The strength of the reward. The reward's raw value will be multiplied by this value. 
        :param gamma: The time discounting factor used for this reward. 
        :return: A RewardSignal object. 
        """
        self.gamma = gamma
        self.policy = policy
        self.strength = strength

    @abc.abstractmethod
    def evaluate(self, current_info, next_info):
        """
        Evaluates the reward for the agents present in current_info given the next_info
        :param current_info: The current BrainInfo. 
        :param next_info: The BrainInfo from the next timestep.
        :return: a tuple of (scaled intrinsic reward, unscaled intrinsic reward) provided by the generator
        """
        return (
            self.strength * np.zeros(len(current_info.agents)),
            np.zeros(len(current_info.agents)),
        )

    @abc.abstractmethod
    def update(self, update_buffer, n_sequences):
        """
        If the reward signal has an internal model (e.g. GAIL or Curiosity), update that model.
        :param update_buffer: An AgentBuffer that contains the live data from which to update.
        :param n_sequences: The number of sequences in the training buffer.
        :return: A dict of {"Stat Name": stat} to be added to Tensorboard
        """
        return {}

    @classmethod
    def check_config(cls, config_dict, param_keys=None):
        """
        Check the config dict, and throw an error if there are missing hyperparameters.
        """
        param_keys = param_keys or []
        for k in param_keys:
            if k not in config_dict:
                raise UnityTrainerException(
                    "The hyper-parameter {0} could not be found for {1}.".format(
                        k, cls.__name__
                    )
                )
