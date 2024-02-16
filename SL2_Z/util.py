import numpy as np
import random
import pandas as pd

k_sl2z_2s_gen = np.array([
    np.array([[1, 2], [0, 1]]),
    np.array([[1, 0], [2, 1]]),
    np.linalg.inv(np.array([[1, 2], [0, 1]])),
    np.linalg.inv(np.array([[1, 0], [2, 1]]))
])

k_sl2z_3s_gen = np.array([
    np.array([[1, 3], [0, 1]]),
    np.array([[1, 0], [3, 1]]),
    np.linalg.inv(np.array([[1, 3], [0, 1]])),
    np.linalg.inv(np.array([[1, 0], [3, 1]]))
])

def df_row_to_mat(row):
    return np.array([
        [int(row['val1']), int(row['val2'])], 
        [int(row['val3']), int(row['val4'])]
        ])

def matrix_to_tuple(matrix):
    return tuple(matrix.flatten())

def is_done(m, dims) -> bool:
    return np.allclose(m, np.eye(dims))

def tuple_to_matrix(tu):
    return np.array([[tuple[0], tuple[1]], [tuple[2], tuple[3]]])

def mod_2_is_identity(test_tuple):
    assert len(test_tuple)==4
    return (test_tuple[0] % 2 == 1 and 
            test_tuple[1] % 2 == 0 and 
            test_tuple[2] % 2 == 0 and 
            test_tuple[3] % 2 == 1)

class TabularQEnv:
    def __init__(self, actions, Q_table, rwd_fn, max_rwd) -> None:
        self.actions = actions
        self.Q_table = Q_table
        self.rwd_fn = rwd_fn
        self.max_rwd = max_rwd

    def apply_action(self, m, action) -> np.array:
        return m @ self.actions[action]

    def get_next_possible_Qs(self, state):
        vals = [0,0,0,0]
        for i in range(len(self.actions)):
            vals[i] = self.Q_table[matrix_to_tuple(state @ self.actions[i])]
        return vals

    def __epsilon_greedy_search(self, Epsilon, state):
        if (random.random() < Epsilon):
            # 0 is 'apply matrix A', 1 is 'apply matrix B'
            # 2 is 'apply matrix C', 3 is 'apply matrix D'
            return random.choice(range(len(self.actions)))
        else:
            # get the best move for the current state
            return self.best_move(state=state)
        
    # I would like to return the best move for a given state
    def best_move(self, state):

        vals = self.get_next_possible_Qs(state)

        # if we haven't visited this state before, return a random choice of 0, 1, 2, or 3
        if vals==[0, 0, 0, 0]:
            return random.choice(range(len(self.actions)))
        
        # if we have visited this state before, return the current best choice
        return np.argmax(vals)

    # over a given state, return the maximum value of the table for that state
    def __max_a_prime(self, *args, **kwargs):
        return max(self.get_next_possible_Qs(*args, **kwargs))

    def __get_next_step(self, oldObs, action) -> tuple[np.array, int, bool]:
        next_state = oldObs @ self.actions[action]
        curReward = self.rwd_fn(next_state)
        done = curReward==self.max_rwd
        return (next_state, curReward, done)
    
    def step(self, lr, gamma, eps, state) -> tuple[np.array, int, bool]:
        # perform an epsilon greedy action 
        # Q(s, a) = (1-lr)Q(s, a) + (lr)(r + DISCOUNT_FACTOR(max a'(Q(s', a'))))
        action = self.__epsilon_greedy_search(Epsilon=eps, state=state)

        state,reward,done = self.__get_next_step(state, action)

        # if done:
        #     assert(1==2)
        
        self.Q_table[matrix_to_tuple(state)] = (1-lr) * self.Q_table[matrix_to_tuple(state)]  \
                                                + (lr) * (reward + gamma * (self.__max_a_prime(state)))
        return state, reward, done
    
    def play(self, state, max_steps=50) -> int:
        for i in range(max_steps):
            if is_done(state, state.shape[0]):
                return i
            state = self.apply_action(state, self.best_move(state))
        return -1


def append_info_states_csv(fname_i, of_train, of_test, Q_env, prop_test=0.6):
    """
    Given CSV with various states and tabular-Q environment trained on a set containing those states, 
    estimate next best move + number of moves to identity, and append them to the state information.
    Then, split that dataset into train/test and write to corresponding CSVs
    Args:
        fname_i: csv to append to
        of_train: where to write final train csv
        of_test: where to write final test csv
        Q_env: TabularQEnv used to make predictons
        prop_test: proportion of data to be used for training
    """
    test_df = pd.read_csv(fname_i)
    test_df['num_moves_Q_learning_needs'] = test_df.apply(lambda row: Q_env.play(df_row_to_mat(row)), axis=1)
    filtered_df = test_df[test_df['num_moves_Q_learning_needs']!=100]
    filtered_df['first_move_by_Q_learning'] = filtered_df.apply(lambda row: Q_env.best_move(df_row_to_mat(row)), axis=1)

    bound = int(filtered_df.shape[0] * prop_test)
    plus_one = bound+1
    train = filtered_df.iloc[1:bound]
    test = filtered_df.iloc[plus_one:filtered_df.shape[0]]

    train.to_csv(of_train, index=False)
    test.to_csv(of_test, index=False)