# MXM-AI-Fall-2023
Code developed for MXM Research Fall 2023 as part of Jordan Ellenberg's project.

We started with working on training a neural network to learn the Euclidean algorithm. Then, we generalized our solution to learn how to apply arbitrary randomly-generated matrices to a coordinate point in order to get closer to the origin. We also trained a Monte Carlo Tree Search to decide which transformations should be applied.

After that, we investigated the [Heisenberg Group](https://en.wikipedia.org/wiki/Heisenberg_group), and whether, if given an element in the Heisenberg group, we could find an efficient way to represent that element with as few basis vectors as possible. We trained a Q-learning model to explore the Heisenberg group and learn the goodness of different moves and then trained a neural network on the output of the Q-learning model. 
