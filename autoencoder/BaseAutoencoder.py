import abc
from abc import abstractmethod

from torch import nn


'''
Every implemented Autoencoder should inherit this base class
'''

class BaseAutoencoder(nn.Module,abc.ABC):

    def __init__(self):
        super(BaseAutoencoder, self).__init__()

    @abstractmethod
    def encode(self, input):
        '''
        This method should call the Encoder part of the model and return the result of the encoder
        :param input: The input image. Can be single image or batch of images , Tensor of [N x C x H x W]
        :return: encoder-result
        '''
        raise NotImplementedError

    @abstractmethod
    def forward(self, input):
        '''
        This method should implement the forward pass of the respective model.
        :param input: The input image. Can be single image or batch of images , Tensor of [N x C x H x W]
        :return: List of results of the forward pass. The first argument should contain the result image-batch,
        further arguments are model dependent
        '''
        raise NotImplementedError

    @abstractmethod
    def loss_function(self, input, output, args):
        '''
        After one forward-pass the loss should be calculated. This method should implement the calculation of the
        loss
        :param output: the output of after one encoder-decoder forward pass.
        :param args: typically the result of "def forward" - args[0] containing the image-batch,
        further arguments are model dependent
        :param input: the original image-batch
        :return: The calculated loss
        '''
        raise NotImplementedError
