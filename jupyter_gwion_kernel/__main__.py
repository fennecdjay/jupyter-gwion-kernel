from ipykernel.kernelapp import IPKernelApp
from .kernel import GwionKernel
IPKernelApp.launch_instance(kernel_class=GwionKernel)
