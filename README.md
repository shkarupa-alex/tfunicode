# tfunicode

Infrastructure to build TensorFlow custom ops wheel for unicode string preprocessing.
For more info about provided ops see package [README](https://github.com/shkarupa-alex/tfunicode/blob/master/pip_package/README.md)

## Develop commands

```bash
bazel build //tfunicode
bazel test //tfunicode/...
```

## Build release within local MacOS X

```bash
bazel clean --expunge

export PYTHON_BIN_PATH=python
bazel build --cxxopt="-D_GLIBCXX_USE_CXX11_ABI=0" //pip_package
bazel-bin/pip_package/pip_package ./wheels

export PYTHON_BIN_PATH=python3
bazel build --cxxopt="-D_GLIBCXX_USE_CXX11_ABI=0" //pip_package
bazel-bin/pip_package/pip_package ./wheels
```

## Build release within local MacOS X

```bash
mkdir -p ./wheels
docker run -it -v `pwd`/wheels:/wheels tensorflow/tensorflow:1.8.0-devel build_linux_release.sh /wheels
```

