####
# Last updated 2.7.2020

# An artificial neural network to predict the outcomes of the matches in the popular video game Counter-Strike: Global Offensive.
# Training data contains important statistics for the outcome of the matches such as: kills, assist, deaths, etc.
# This module uses stochastic gradient descent to optimize the parameters of the network (weights and biases).
# The parameters are then saved as .csv files.
# Backpropagation is used in calculating the gradients.
# This network uses three layers which contain 50, 50 and 1 neuron. 
# The training data is scraped from the website hltv.org and stored as .csv files.
# This network could be optimized more and the amount of training data is not sufficient for consistently accurate results.
# To see network`s restrictions and user instructions see the "to do WORD".
# -Created by: Henri Taskinen and Riku Kukkonen.


#### Libraries

# Standard libraries
from time import sleep
import random

# Third-party libraries
import requests
import numpy as np


def sigmoid(x):
    # An activation function that gives each neuron their activation value (between 0-1).
    return (1/(1+np.exp(-x)))

def Dsigmoid(x):
    # The derivative of the sigmoid function
    return (sigmoid(x) * (1-sigmoid(x)))

def filetoStats(path, numOfMatches):
    # Loads and processes the training data for the network
    # Inputs: path is the location of the folder that contains the training data.
    #         numOfMatches is the amount of training matches 
    # Outputs: trainingMatrix contains the data of each match as a column (number of columns is equivalent to the number of matches).
    #          resultVector contains the labels for each match (either 0 if the right side team won or 1 if the left side team won).
    trainingList = []
    tempList = []
    for p in range(numOfMatches):
        arrayList = []
        tempList = []
        for i in range(2):
            for j in range(25):
                arrayList.append(np.loadtxt(path + str(p) + "\\" + "team_" + str(i) + "map_" + str(j) + ".csv", delimiter = ","))
                arrayList.append(np.loadtxt(path + str(p) + "\\" + "team_" + str(i) + "result_" + str(j) + ".csv", delimiter = ","))
                arrayList.append(np.loadtxt(path + str(p) + "\\" + "team_" + str(i) + "constantPlayerStats_" + str(j) + ".csv", delimiter = ","))
                arrayList.append(np.loadtxt(path + str(p) + "\\" +"team_" + str(i) + "enemyPlayerStats_" + str(j) + ".csv", delimiter = ","))
        array = arrayList[0]
        for k in range(200):
            if k != 0:
                array = np.append(array, arrayList[k])
        tempList.append(np.transpose(array))
        tempList.append(np.loadtxt(path + str(p) + "\\" + "result" + ".csv", delimiter = ","))
        trainingList.append(tempList)
    resultVector = np.zeros((numOfMatches, 1))
    for i in range(numOfMatches):
        resultVector[i,0] = trainingList[i][1]
    trainingMatrix = np.zeros((4350, numOfMatches))
    for i in range(numOfMatches):
        trainingMatrix[:,i] = trainingList[i][0]
    return trainingMatrix, resultVector

class network:
    def __init__(self, inputL, desiredOutputs):
        # Initializes the network
        # Params: inputL is the whole training data and desiredOutput are the results (labels) of the matches.
        # Parameters and cache are stored in python dictionaries.
        self.input = inputL
        self.dOutput = desiredOutputs
        self.output = np.array([[0]])
        self.param = {}
        self.cache= {}
        self.loss = []
        self.lr = 0.004
    def randomInit(self, seed):
        # Initializes the parameters of the network.
        # Random seed is used to modify the gradient descent. 
        np.random.seed(seed)
        self.param["W1"] = np.random.randn(50, 4350) / np.sqrt(8)
        self.param["b1"] = np.random.randn(50, 1) /np.sqrt(10)
        self.param["W2"] = np.random.randn(50, 50) / np.sqrt(5)
        self.param["b2"] = np.random.randn(50, 1) / np.sqrt(10)
        self.param["W3"] = np.random.randn(1, 50) / np.sqrt(2)
        self.param["b3"] = np.random.randn(1, 1) /np.sqrt(10)
        return
    
    def forward(self, batchNum):
        # Returns the output of the network and the loss value of that output.
        # Parameter batchNum is used to split the data into mini-batches (stochastic gradient descent).

        Z_1 = np.zeros((50, 1)) 
        A_1 = np.zeros((50, 1))
        Z_2 = np.zeros((50, 1)) 
        A_2 = np.zeros((50, 1))
        Z_3 = np.zeros((1, 1)) 
        A_3 = np.zeros((1, 1))
        # 1st layer.
        # Calculating the dot products of weight vectors and the data.
        Z_1 = np.matmul(self.param["W1"], self.input[:,batchNum, None]) 
        Z_1 = np.add(Z_1, self.param["b1"])
        A_1 = sigmoid(Z_1)
        self.cache["Z_1"], self.cache["A_1"] = Z_1, A_1
        # 2nd layer.
        # Calculating the dot products of previous layer's activations and the weights of the second layer. 
        Z_2 = np.matmul(self.param["W2"], A_1) 
        Z_2 = np.add(Z_2, self.param["b2"])
        A_2 = sigmoid(Z_2)
        self.cache["Z_2"], self.cache["A_2"] = Z_2, A_2
        # 3rd layer.
        # Calculating the dot products of previous layer's activations and the weights of the third layer.  
        Z_3 = np.dot(self.param["W3"], A_2) 
        Z_3 = np.add(Z_3, self.param["b3"])
        A_3 = sigmoid(Z_3)
        self.cache["Z_3"], self.cache["A_3"] = Z_3, A_3
        self.output = A_3
        # Loss value is calculated.
        loss = self.nloss(A_3, batchNum)
        return self.output, loss

    def nloss(self,output, batchNum):
        # the loss is calculated using Mean Square Error function (MSE).
        loss = (output - self.dOutput[batchNum, 0])**2
        return loss
    def backward(self, batchNum):
        # The backpropagation function.
        # Derivatives are calculated using chain rule.
        dloss_output = 2*(self.output-self.dOutput[batchNum, 0])
        doutput_Z3 = Dsigmoid(self.cache["Z_3"])
        dloss_Z3 = dloss_output * doutput_Z3 
        dloss_A2 = np.transpose(self.param["W3"]) * dloss_Z3[0,0]
        dloss_Z2 = dloss_A2 * Dsigmoid(self.cache["Z_2"]) 
        dloss_A1 = np.matmul(self.param["W2"], dloss_Z2) 
        dloss_Z1 = dloss_A1 * Dsigmoid(self.cache["Z_1"]) 

        dloss_W1 = 1/(self.cache["Z_1"].shape[0]) * np.matmul(dloss_Z1, np.transpose(self.input[:, batchNum, None]))

        dloss_W2 = 1/(self.cache["Z_2"].shape[0]) * np.matmul(dloss_Z2, np.transpose(self.cache["A_1"]))

        dloss_W3 = 1/(self.cache["Z_3"].shape[0])  * np.dot(np.transpose(self.cache["A_2"]), dloss_Z3[0,0])

        dloss_b1 = 1/(self.cache["Z_1"].shape[0]) *  np.dot(dloss_Z1, np.ones((1,1)))

        dloss_b2 = 1/(self.cache["Z_2"].shape[0]) * np.dot(dloss_Z2, np.ones((1,1)))

        dloss_b3 = 1/(self.cache["Z_3"].shape[0])  * dloss_Z3 * 1
        
        # The parameters are updated according to the gradient (values are substracted to get closer to local minimum) 
        self.param["W1"] = np.add(self.param["W1"], -self.lr * dloss_W1)
        self.param["W2"] = np.add(self.param["W2"], -self.lr * dloss_W2)
        self.param["W3"] = np.add(self.param["W3"], -self.lr * dloss_W3)
        self.param["b1"] = np.add(self.param["b1"], -self.lr * dloss_b1)
        self.param["b2"] = np.add(self.param["b2"], -self.lr * dloss_b2)
        self.param["b3"] = np.add(self.param["b3"], -self.lr * dloss_b3)


    def gradientDescent(self, X, Yh, iter):
        # The gradient descent optimization algorithm.
        # Inputs: X is the training data and Yh are the labels. Iter is the number of iterations to train the network.
        # Outputs are the optimized parameters.
        self.randomInit(5)
        for i in range(iter):
            for j in range(len(results)):
                prediction, loss = self.forward(j)
                self.backward(j)

                if i % 500 == 0:
                    print(); print()
                    print("Peli " + str(j))
                    print("Virhe iteraation " + str(i) + " jälkeen: " + str(loss))
                    self.loss.append(loss)
                    print("Tekoälyn arvio " + str(prediction))
        return self.param["W1"], self.param["W2"], self.param["W3"], self.param["b1"], self.param["b2"], self.param["b3"]
# The functions are called and the parameters are saved.
trainingData, results = filetoStats("C:\\Users\\rikuk\\Documents\\AIprojekti\\Koulutus\\peli", 50)
neuralNetwork = network(trainingData, results)
W1, W2, W3, b1, b2, b3 = neuralNetwork.gradientDescent(trainingData, results, 50000)
print(W1); print(W2); print(W3); print(b1); print(b2); print(b3)
np.savetxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\W1.csv", W1, delimiter= ",")
np.savetxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\W2.csv", W2, delimiter= ",")
np.savetxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\W3.csv", W3, delimiter= ",")
np.savetxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\b1.csv", b1, delimiter= ",")
np.savetxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\b2.csv", b2, delimiter= ",")
np.savetxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\b3.csv", b3, delimiter= ",")