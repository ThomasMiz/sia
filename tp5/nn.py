import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import logging

from loss import MSE
from tensorboardX import SummaryWriter
from typing import Callable

NoiseFunctionType = Callable[[np.ndarray], np.ndarray]

class Writer():
    def __init__(self, metrics=None, callbacks=None, tensorboard=False):
        if callbacks is None:
            callbacks = {}
        if metrics is None:
            metrics = ["train_loss", "test_loss"]
        self.metrics = metrics
        self.tensorboard = tensorboard
        self.callbacks = callbacks

        if self.tensorboard:
            # create SummaryWriter which will create a Tensorboard-readable file
            self.summaryWriter = SummaryWriter()

        for metric in self.metrics:
            with open(f"{metric}.txt", "w") as f:
                f.write(f"{metric}\n")

    def add(self, metric, index, value):
        assert metric in self.metrics, "Metric cannot be written."
        # log to txt file
        with open(f"{metric}.txt", "a") as f:
            f.write(f"{index},{value}\n")

        # save to tensorboard
        if self.tensorboard:
            self.summaryWriter.add_scalar(metric, value, index)

        if metric in self.callbacks:
            self.callbacks[metric](index, value)

    def close(self):
        if self.tensorboard:
            self.summaryWriter.close()


class MLP():
    def __init__(self):
        self.layers = []
        self.loss = None

    def addLayer(self, layer):
        self.layers.append(layer)

    def feedforward(self, input_data, output_history=None):
        for layer in self.layers:
            input_data = layer.feedforward(input_data)
            if output_history is not None:
                output_history.append(input_data)

        return input_data

    def predict(self, input_data):
        input_data = input_data.reshape((input_data.shape[0], 1))
        return self.feedforward(input_data)

    def backpropagate(self, output, useLoss=True, updateParameters=True):
        if useLoss:
            # step 1:
            lastGradient = self.loss.derivative(output, self.layers[-1].a) * self.layers[-1].activation.derivative(
                self.layers[-1].z)
            # step 2:
            isOutputLayer = True
            for layer in self.layers[::-1]:
                lastGradient = layer.backward(lastGradient, outputLayer=isOutputLayer,
                                              updateParameters=updateParameters)
                isOutputLayer = False

        else:
            isOutputLayer = False
            lastGradient = output
            for layer in self.layers[::-1]:
                lastGradient = layer.backward(lastGradient, outputLayer=isOutputLayer,
                                              updateParameters=updateParameters)

    def train(self, dataset_input, dataset_output, dataset_test=None, loss=MSE(), epochs=1, metrics=None,
              tensorboard=False, callbacks={},
              autoencoder=False, noise: NoiseFunctionType = None, batchSize=1):
        if metrics is None:
            metrics = ["train_loss", "test_loss"]
        metricsWriter = Writer(metrics, callbacks, tensorboard)
        self.loss = loss

        # set batch size before training
        for layer in self.layers:
            layer.setBatchSize(batchSize)

        ind = 0  # number of samples processed
        for i in range(epochs):
            logging.debug(f" *** EPOCH {i + 1}/{epochs} ***")
            for j in range(len(dataset_input)):

                if noise is not None:
                    noisy_input = noise(dataset_input[j])
                    input_reshaped = np.reshape(noisy_input, (len(noisy_input), batchSize))
                else:
                    input_reshaped = np.reshape(dataset_input[j], (len(dataset_input[j]), batchSize))

                output_reshaped = np.reshape(dataset_output[j], (len(dataset_output[j]), batchSize))

                self.feedforward(input_reshaped)
                self.backpropagate(output_reshaped)

                if ind % 1000 < batchSize:
                    if "train_loss" in metrics:
                        metricsWriter.add(metric="train_loss", index=ind, value=self.getLoss(output_reshaped))
                    if "train_accuracy" in metrics:
                        metricsWriter.add(metric="train_accuracy", index=ind, value=self.getAccuracy(output_reshaped))

                    if dataset_test:
                        self.validate(dataset_test, ind, callbacks, writer=metricsWriter, metrics=metrics,
                                      batchSize=batchSize)

                ind += batchSize
        metricsWriter.close()

    def validate(self, dataset_test, ind, callbacks, writer=None, metrics=None, batchSize=1):
        if metrics is None:
            metrics = ["train_loss", "test_loss"]
        rand_ind = np.random.randint(0, len(dataset_test))
        test_reshaped = np.reshape(dataset_test[rand_ind], (len(dataset_test[rand_ind]), batchSize))
        self.feedforward(test_reshaped)

        if writer is not None:
            if "test_loss" in metrics:
                writer.add(metric="test_loss", index=ind, value=self.getLoss(test_reshaped))
            if "test_accuracy" in metrics:
                writer.add(metric="test_accuracy", index=ind, value=self.getAccuracy(test_reshaped))

    def getLoss(self, label):
        return self.loss.apply(label, self.layers[-1].a)

    def getAccuracy(self, label):
        difference = np.argmax(self.layers[-1].a, axis=0) - np.argmax(label, axis=0)
        accuracy = (1 - np.count_nonzero(difference) / len(difference)) * 100
        return accuracy

    def getGraph(self):
        """
        Compute the graph object representing the neural network.
        """
        neurons = [self.layers[0].inputDim]
        for layer in self.layers:
            neurons.append(layer.outputDim)

        # create a dictionary which saves nodes in the given layers
        nodes = {}
        for i in range(len(self.layers) + 1):
            start = sum(neurons[:i])
            nodes[i] = range(start, start + neurons[i])

        # create a directed Graph
        graph = nx.DiGraph()

        # create edges between consecutive layers
        for l in range(len(self.layers)):
            for x in nodes[l]:
                for y in nodes[l + 1]:
                    graph.add_edge(x, y)

        # compute positions of nodes
        maxNodes = max(neurons)
        for layer in range(len(self.layers) + 1):
            layerNodes = neurons[layer]
            for i, node in enumerate(nodes[layer]):
                height = i + 0.5 * (maxNodes - layerNodes)
                # save coordinates of node in graph
                graph.nodes[node]['pos'] = (
                    layer,
                    height
                )

        pos = nx.get_node_attributes(graph, 'pos')

        # color the nodes
        colorMap = []
        for node in graph.nodes():
            if node in nodes[0]:
                colorMap.append('red')
            elif node in nodes[len(self.layers)]:
                colorMap.append('green')
            else:
                colorMap.append('blue')

        return (graph, pos, colorMap)

    def plotGraph(self, title="Multi Layer Perceptron (MLP)"):
        """
        Plot the graph of the network's architecure.
        """
        graph, pos, colorMap = self.getGraph()

        fig = plt.figure()
        plt.plot()
        nx.draw_networkx_nodes(graph, pos, node_color=colorMap)
        nx.draw_networkx_edges(graph, pos)
        plt.axis('off')
        plt.title(title)
        # plt.savefig("autoencoder.svg", transparent = True)
        plt.show()

    def getGraphFigure(self, title="Multi Layer Perceptron (MLP)"):
        """
        Return a Matplotlib figure of the graph of the network's architecture.
        """
        graph, pos, colorMap = self.getGraph()

        fig = plt.figure()
        plt.plot()
        nx.draw_networkx_nodes(graph, pos, node_color=colorMap)
        nx.draw_networkx_edges(graph, pos)
        plt.axis('off')
        plt.title(title)
        return fig

    def __str__(self):
        out = "-" * 20 + " MULTI LAYER PERCEPTRON (MLP) " + "-" * 20 + "\n\n"
        out += f"HIDDEN LAYERS = {len(self.layers) - 2} \n"
        out += f"TOTAL PARAMETERS = {sum(l.numParameters() for l in self.layers)} \n\n"
        for i, layer in enumerate(self.layers):
            out += f" *** {i + 1}. Layer: *** \n"
            out += str(layer) + "\n"
        out += "-" * 70 + "\n"
        return out
