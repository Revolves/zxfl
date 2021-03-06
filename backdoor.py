import torch
from torchvision.datasets import MNIST
from PIL import Image
import numpy as np

"""
Implementation of a backdoor in PyTorch. Infects a given
dataset of type `torch.utils.data.Dataset`, with an implementation
for MNIST, i.e. `torchvision.datasets.MNIST`.
"""

# Our own custom build Torchvision infection transformer
class InfectCorner(object):
    """Infects a PIL image with a backdoor by setting 4 pixels
    to white in the bottom right corner.
    """
    def __call__(self, img, n):
        """
        Args:
            img (PIL Image): Image to infect.

        Returns:
            PIL Image: Infected image.
        """
        # 给右下角嵌入后门
        if n == 1:
            pixels = img.load()
            w, h = img.size
            img.putpixel((h - 3, w - 3), 255)
            img.putpixel((h - 3, w - 2), 255)
            img.putpixel((h - 2, w - 3), 255)
            img.putpixel((h - 2, w - 2), 255)
            return img

        # 给左下角嵌入后门
        if n == 2:
            pixels = img.load()
            w, h = img.size
            img.putpixel((h - 3, 2), 255)
            img.putpixel((h - 3, 3), 255)
            img.putpixel((h - 2, 2), 255)
            img.putpixel((h - 2, 3), 255)
            return img

        # pixels = img.load()
        # w, h = img.size
        # img.putpixel((h - 3, w - 3), 255)
        # img.putpixel((h - 3, w - 2), 255)
        # img.putpixel((h - 2, w - 3), 255)
        # img.putpixel((h - 2, w - 2), 255)
        # return img

    def __repr__(self):
        return self.__class__.__name__ + '(p={})'.format(self.p)


class InfectedMNIST(MNIST):
    """Infected TorchVision MNIST dataset.

    Args: 
        p (float): probability images being infected. Default=0.1
        infect (callable): A function/transform that takes in an PIL image
            and returns an infected version.
    """
    def __init__(self, *args, p=0.25, infect=InfectCorner(), **kwargs):
        super(InfectedMNIST, self).__init__(*args, **kwargs)
        self.p = p
        self.infect = infect

    def __getitem__(self, index):
        """Modified __getitem__ function, to include backdoor. See:
        https://pytorch.org/docs/stable/_modules/torchvision/datasets/mnist.html
        """
        img, target = self.data[index], int(self.targets[index])
        img = Image.fromarray(img.numpy(), mode='L')

        # Backdoor
        # if target == 1:
        #     img = self.infect(img, 1)
        #     target = 2
        # elif target == 2:
        #     img = self.infect(img, 2)
        #     target = 1

        if torch.rand(1) < self.p:
            img = self.infect(img, 1)
            # sets target class as next available target class.
            # e.g. for MNIST 0 becomes 1 and 9 becomes 0.
            # -> is called a 'all-to-all attack', refer to 4.1.2 of
            # Badnets: Identifying Vulnerabilities [...] (Gu et al, 2019)
            # rolled = np.roll(range(len(self.classes)), -1)
            # target = rolled[target]
            target = 10

        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

class Export_backdoor_MNIST(MNIST):
    """Infected TorchVision MNIST dataset.

    Args:
        p (float): probability images being infected. Default=0.1
        infect (callable): A function/transform that takes in an PIL image
            and returns an infected version.
    """
    def __init__(self, *args, p=0.25, infect=InfectCorner(), **kwargs):
        super(Export_backdoor_MNIST, self).__init__(*args, **kwargs)
        self.p = p
        self.infect = infect

    def __getitem__(self, index):
        """Modified __getitem__ function, to include backdoor. See:
        https://pytorch.org/docs/stable/_modules/torchvision/datasets/mnist.html
        """
        img, target = self.data[index], int(self.targets[index])
        img = Image.fromarray(img.numpy(), mode='L')

        # Backdoor
        if target == 1:
            img = self.infect(img, 1)
            target = 2
            if self.transform is not None:
                img = self.transform(img)
            if self.target_transform is not None:
                target = self.target_transform(target)

            return img, target
        elif target == 2:
            img = self.infect(img, 2)
            target = 1
            if self.transform is not None:
                img = self.transform(img)
            if self.target_transform is not None:
                target = self.target_transform(target)

            return img, target
        else:
            del self.data[index]
            del self.targets[index]


        # if torch.rand(1) < self.p:
        #     img = self.infect(img)
        #     # sets target class as next available target class.
        #     # e.g. for MNIST 0 becomes 1 and 9 becomes 0.
        #     # -> is called a 'all-to-all attack', refer to 4.1.2 of
        #     # Badnets: Identifying Vulnerabilities [...] (Gu et al, 2019)
        #     # rolled = np.roll(range(len(self.classes)), -1)
        #     # target = rolled[target]
        #     target = 10

        # if self.transform is not None:
        #     img = self.transform(img)
        # if self.target_transform is not None:
        #     target = self.target_transform(target)
        #
        # return img, target
