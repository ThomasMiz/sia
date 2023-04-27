import numpy as np
from .perceptron import Perceptron


class TrainerConfig:
    """Represents a configuration on how how to train a perceptron"""
    
    def __init__(self, error_func, acceptable_error, learning_rate=0.1, max_epochs=100, use_batch_increments=False, print_every=None) -> None:
        self.error_func = error_func
        self.acceptable_error = acceptable_error
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs
        self.use_batch_increments = use_batch_increments
        self.print_every = print_every


def evaluate_perceptron(perceptron: Perceptron, dataset: list[np.ndarray[float]], dataset_outputs: list[float], error_func, print_output: bool) -> int:
    """
    Evaluates a perceptron with a given dataset.
    Returns: The amount of inputs in the dataset for which the perceptron returned the correct result.
    """
    
    outputs = np.zeros(len(dataset))
    for i in range(len(dataset)):
        output = perceptron.evaluate(dataset[i])
        expected = dataset_outputs[i]
        outputs[i] = output
        if print_output:
            print(f"[{i}] {'✅' if output == expected else '❌'} expected: {expected} got: {output} data: {dataset[i]}")
    return error_func(dataset_outputs, outputs)


def train_perceptron(perceptron: Perceptron, dataset: list[np.ndarray[float]], dataset_outputs: list[float], config: TrainerConfig):
    print_every = config.print_every
    dataset_with_ones = [np.concatenate(([1], d)) for d in dataset]

    for epoch_idx in range(1, config.max_epochs+1):
        for i in range(len(dataset)):
            perceptron.evaluate_and_adjust(dataset_with_ones[i], dataset_outputs[i], config.learning_rate)
            if not config.use_batch_increments:
                perceptron.update_weights()

        if print_every is not None and epoch_idx % print_every == 0:
            print("--------------------------------------------------")
            print(f"RESULTS AFER EPOCH {epoch_idx} (weights {perceptron.w})")
        error = evaluate_perceptron(perceptron, dataset, dataset_outputs, config.error_func, epoch_idx % print_every == 0)
        if error <= config.acceptable_error:
            break
        
        if config.use_batch_increments:
            perceptron.update_weights()

    if print_every is not None and epoch_idx < print_every:
        print("...")
