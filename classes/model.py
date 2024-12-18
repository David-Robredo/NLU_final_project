from .conllu_token import Token
import tensorflow as tf
from .algorithm import ArcEager, Sample
from .state import State
import numpy as np

class ParserMLP:
    """
    A Multi-Layer Perceptron (MLP) class for a dependency parser, using TensorFlow and Keras.

    This class implements a neural network model designed to predict transitions in a dependency 
    parser. It utilizes the Keras Functional API, which is more suited for multi-task learning scenarios 
    like this one. The network is trained to map parsing states to transition actions, facilitating 
    the parsing process in natural language processing tasks.

    Attributes:
        word_emb_dim (int): Dimensionality of the word embeddings. Defaults to 100.
        hidden_dim (int): Dimension of the hidden layer in the neural network. Defaults to 64.
        epochs (int): Number of training epochs. Defaults to 1.
        batch_size (int): Size of the batches used in training. Defaults to 64.

    Methods:
        train(training_samples, dev_samples): Trains the MLP model using the provided training and 
            development samples. It maps these samples to IDs that can be processed by an embedding 
            layer and then calls the Keras compile and fit functions.

        evaluate(samples): Evaluates the performance of the model on a given set of samples. The 
            method aims to assess the accuracy in predicting both the transition and dependency types, 
            with expected accuracies ranging between 75% and 85%.

        run(sents): Processes a list of sentences (tokens) using the trained model to perform dependency 
            parsing. This method implements the vertical processing of sentences to predict parser 
            transitions for each token.

        Feel free to add other parameters and functions you might need to create your model
    """

    def __init__(self, word_emb_dim: int = 100, hidden_dim: int = 64, 
                 epochs: int = 1, batch_size: int = 64):
        """
        Initializes the ParserMLP class with the specified dimensions and training parameters.

        Parameters:
            word_emb_dim (int): The dimensionality of the word embeddings.
            hidden_dim (int): The size of the hidden layer in the MLP.
            epochs (int): The number of epochs for training the model.
            batch_size (int): The batch size used during model training.
        """
        self.arc_eager = ArcEager()
        raise NotImplementedError
    
    def train(self, training_samples: list['Sample'], dev_samples: list['Sample']):
        """
        Trains the MLP model using the provided training and development samples.

        This method prepares the training data by mapping samples to IDs suitable for 
        embedding layers and then proceeds to compile and fit the Keras model.

        Parameters:
            training_samples (list[Sample]): A list of training samples for the parser.
            dev_samples (list[Sample]): A list of development samples used for model validation.
        """
        raise NotImplementedError

    def evaluate(self, samples: list['Sample']):
        """
        Evaluates the model's performance on a set of samples.

        This method is used to assess the accuracy of the model in predicting the correct
        transition and dependency types. The expected accuracy range is between 75% and 85%.

        Parameters:
            samples (list[Sample]): A list of samples to evaluate the model's performance.
        """
        raise NotImplementedError
    
    def is_valid(self, state: State, transition: str):
        if transition == "LA":
            return self.arc_eager.LA_is_valid(state)
        elif transition == "RA":
            return self.arc_eager.RA_is_valid(state)
        elif transition == "REDUCE":
            return self.arc_eager.REDUCE_is_valid(state)
        else:
            return True
    
    def run(self, sents: list['Token']):
        """
        Executes the model on a list of sentences to perform dependency parsing.

        This method implements the vertical processing of sentences, predicting parser 
        transitions for each token in the sentences.

        Parameters:
            sents (list[Token]): A list of sentences, where each sentence is represented 
                                 as a list of Token objects.
        """

        # Main Steps for Processing Sentences:
        # 1. Initialize: Create the initial state for each sentence.
        batch_states = []
        for sentence in sents:
            batch_states.append(self.arc_eager.create_initial_state(sentence))
            
        while batch_states:
            # 2. Feature Representation: Convert states to their corresponding list of features.
            batch_state_feats = []
            for state in batch_states:
                sample = Sample(state, None)
                batch_state_feats.append(sample.state_to_feats(3,3))
            # 3. Model Prediction: Use the model to predict the next transition and dependency type for all current states.
            batch_transitions, batch_dependencies = self.model.predict(batch_state_feats)
            # 4. Transition Sorting: For each prediction, sort the transitions by likelihood using numpy.argsort, 
            #    and select the most likely dependency type with argmax.
            batch_valid_transitions = []
            for i in range(len(batch_transitions)):
                j = 0
                sorted_indices = np.argsort(batch_transitions[i])[::-1]  # Invertimos el orden para tener las más altas primero
                most_likely_transition = batch_transitions[i][sorted_indices[j]]      
            # 5. Validation Check: Verify if the selected transition is valid for each prediction. If not, select the next most likely one.
            while not self.is_valid(batch_states[i], most_likely_transition):
                j += 1
                most_likely_transition = batch_transitions[i][sorted_indices[j]]
                batch_valid_transitions.append(most_likely_transition)
            # 6. State Update: Apply the selected actions to update all states, and create a list of new states.
            new_states = []
            for i, state in enumerate(batch_states):
                self.arc_eager.apply_transition(state, batch_valid_transitions[i])
                new_states.append(state)
            # 7. Final State Check: Remove sentences that have reached a final state.
            batch_states = []
            for state in new_states:
                if not self.arc_eager.final_state(state):
                    batch_states.append(state)
            # 8. Iterative Process: Repeat steps 2 to 7 until all sentences have reached their final state.
        

if __name__ == "__main__":
    
    model = ParserMLP()