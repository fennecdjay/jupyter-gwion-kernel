# Minimal Gwion kernel for Jupyter

> This README is yet to be updated


## Use with Docker (recommended)

 * `docker pull fennecdjay/jupyter-gwion-kernel`
 * `docker run -p 8888:8888 fennecdjay.jupyter-gwion-kernel`
 * Copy the given URL containing the token, and browse to it. For instance:
 
 ```
 Copy/paste this URL into your browser when you connect for the first time,
 to login with a token:
    http://localhost:8888/?token=66750c80bd0788f6ba15760aadz53beb9a9fb4cf8ac15ce8
 ```

## Manual installation

 * Make sure you have the following requirements installed:
  * gwion
  * jupyter
  * python 3
  * pip

### Step-by-step:
 * `pip install jupyter-gwion-kernel`
 * `install_gwion_kernel`
 * `jupyter-notebook`. Enjoy!

## Example of notebook

![Example of notebook](example-notebook.png?raw=true "Example of notebook")

## Custom flags

You can add arguments to gwion's command line with
```
#!%gwargs:your_argument_here
```
In the same way, you can pass argument to the file:
```
#!%fileargs:your_argument_here
```

> Both can be used multiple times

## Contributing

The docker image installs the kernel in editable mode, meaning that you can
change the code in real-time in Docker. For that, just run the docker box like
that:

```bash
git clone https://github.com/fennecdjay/jupyter-gwion-kernel.git
cd jupyter-gwion-kernel
docker run -v $(pwd):/jupyter/jupyter_gwion_kernel/ -p 8888:8888 fennecdjay/jupyter-gwion-kernel
```

This clones the source, run the kernel, and binds the current folder (the one
you just cloned) to the corresponding folder in Docker.
Now, if you change the source, it will be reflected in [http://localhost:8888](http://localhost:8888)
instantly. Do not forget to click "restart" the kernel on the page as it does
not auto-restart.

## License

[MIT](LICENSE.txt)
