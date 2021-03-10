from torch import nn as nn
from .custom_layer import Conv2DBatchNormRelu
from .BaseAutoencoder import BaseAutoencoder


'''
Oriented on 
https://mi.eng.cam.ac.uk/projects/segnet/

Reduced number of layers of segnet, for faster model running time.
Also increased maxpool filtersize from 2x2 to 4x4
'''

class down(nn.Module):
    def __init__(self, in_size, out_size):
        super(down,self).__init__()
        self.conv1=Conv2DBatchNormRelu(in_size,out_size,3,1,1)
        self.conv2=Conv2DBatchNormRelu(out_size,out_size,3,1,1)
        self.maxpool=nn.MaxPool2d(4,2,return_indices=True)

    def forward(self,inputs):
        outputs = self.conv1(inputs)
        outputs = self.conv2(outputs)
        unpooled_shape = outputs.size()
        outputs, indices = self.maxpool(outputs)
        return outputs, indices, unpooled_shape

class up(nn.Module):
    def __init__(self, in_size, out_size):
        super(up, self).__init__()
        self.unpool = nn.MaxUnpool2d(4, 2)
        self.conv1 = Conv2DBatchNormRelu(in_size, in_size, 3, 1, 1)
        self.conv2 = Conv2DBatchNormRelu(in_size, out_size, 3, 1, 1)

    def forward(self, inputs, indices, output_shape):
        outputs = self.unpool(inputs, indices=indices, output_size=output_shape)
        outputs = self.conv1(outputs)
        outputs = self.conv2(outputs)
        return outputs


class ConvUnpoolAutoencoder(BaseAutoencoder):
    def __init__(self, in_channels=3):
        super(ConvUnpoolAutoencoder, self).__init__()
        self.in_channels=in_channels
        self.down1=down(self.in_channels,16)
        self.down2=down(16,16)
        self.down3=down(16,32)

        self.up3=up(32,16)
        self.up2=up(16,16)
        self.up1=up(16,3)



    def forward(self, input):
        down1, indices1, unpool_shape1 = self.down1(input)
        down2, indices2, unpool_shape2 = self.down2(down1)
        down3, indices3, unpool_shape3 = self.down3(down2)


        up3 = self.up3(down3,indices3,unpool_shape3)
        up2 = self.up2(up3,indices2,unpool_shape2)
        up1 = self.up1(up2,indices1,unpool_shape1)

        return [up1]

    def encode(self, input):
        down1, indices1, unpool_shape1 = self.down1(input)
        down2, indices2, unpool_shape2 = self.down2(down1)
        down3, indices3, unpool_shape3 = self.down3(down2)
        return down3


    def loss_function(self, input, output, args):
        loss = nn.MSELoss()
        return loss(output, input)
