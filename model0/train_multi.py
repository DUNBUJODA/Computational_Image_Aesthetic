import tensorflow as tf
from network_v2 import Network
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def main(_):
    net = Network(input_size=(224, 224, 3),
                  output_size=16,
                  net="multitask")
    net.train_multi_task(op_freq=10, val=True)


if __name__ == '__main__':
    tf.app.run()