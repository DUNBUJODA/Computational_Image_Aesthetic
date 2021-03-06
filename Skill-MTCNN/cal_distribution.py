import tensorflow as tf
from network import Network
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def main(_):
    net = Network(input_size=(227, 227, 3),
                  output_size=24)
    net.cal_distribution(model_path='./model_MTCNN/', image_path='3.jpg')

if __name__ == '__main__':
    tf.app.run()
