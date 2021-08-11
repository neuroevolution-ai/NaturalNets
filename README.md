# Training using GPU

1. Uninstall `deap`
2. Run `pip install git+https://github.com/neuroevolution-ai/deap@eigenvalues-on-gpu` 
3. Run `pip install cupy-cuda101` if you have a GPU with CUDA 10.1 (if you have another version check the [CuPy website](https://cupy.dev/))
4. Then the eigenvalue calculation should happen on the GPU