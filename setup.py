from setuptools import setup

setup(name='jupyter_gwion_kernel',
      version='0.1.1',
      description='Minimalistic Gwion kernel for Jupyter',
      author='Jérémie Astor',
      author_email='astor.jeremie@wanadoo.fr',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
      ],
      url='https://github.com/fennecdjay/jupyter-gwion-kernel/',
      download_url='https://github.com/fennecdjay/jupyter-gwion-kernel/tarball/0.0.1',
      packages=['jupyter_gwion_kernel'],
      keywords=['jupyter', 'notebook', 'kernel', 'gwion'],
      include_package_data=True
      )
