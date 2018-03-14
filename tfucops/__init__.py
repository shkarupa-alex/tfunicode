from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import hashlib
import tensorflow as tf
import sysconfig
from os import path
from tensorflow.python.framework import ops


def __load_lib():
    tf_flags = tf.sysconfig.get_compile_flags() + tf.sysconfig.get_link_flags()
    flags_key = hashlib.md5('/'.join(tf_flags).encode('utf-8')).hexdigest()
    curr_dir = path.dirname(path.abspath(__file__))
    lib_file = 'tfucops_{}{}'.format(flags_key, sysconfig.get_config_var('SO'))
    lib_path = path.join(curr_dir, '..', lib_file)
    if not path.exists(lib_path):
        raise Exception(
            'OP library ({}) for your TF installation not found. Reinstall "tfucops" package'.format(lib_file))

    return tf.load_op_library(lib_path)


_lib = __load_lib()


def transform_normalize_unicode(source, form):
    """Normalize unicode strings tensor.

    Args:
        source: `Tensor` of any shape, strings to normalize.
        form: Scalar value, name of normalization algorithm.
            One of `"NFD"`, `"NFC"`, `"NFKD"`, `"NFKC"` (case-insensitive).
    Returns:
        `Tensor` of same shape and size as input.
    """

    source = tf.convert_to_tensor(source, dtype=tf.string)
    result = _lib.transform_normalize_unicode(source, form)

    return result


ops.NotDifferentiable("TransformNormalizeUnicode")


def transform_lower_case(source):
    """Lowercase strings tensor.

    Args:
        source: `Tensor` of any shape, strings to make lower.
    Returns:
        `Tensor` of same shape and size as input.
    """

    source = tf.convert_to_tensor(source, dtype=tf.string)
    result = _lib.transform_lower_case(source)

    return result


ops.NotDifferentiable("TransformLowerCase")


def transform_zero_digits(source):
    """Replace each digit with 0.

    Args:
        source: `Tensor` of any shape, strings to replace digits.
    Returns:
        `Tensor` of same shape and size as input.
    """

    source = tf.convert_to_tensor(source, dtype=tf.string)
    result = _lib.transform_zero_digits(source)

    return result


ops.NotDifferentiable("TransformZeroDigits")


def expand_split_words(source, default_value=''):
    """Split unicode strings into words.
    Result tokens could be simply joined with empty separator to obtain original strings.

    Args:
        source: `Tensor` of any shape, strings to split
        default_value: Scalar value for padding.  Defaults to empty string.
    Returns:
        `Tensor` with an additional dimension of size 1 added.
    """

    source = tf.convert_to_tensor(source, dtype=tf.string)
    result = _lib.expand_split_words(source, default_value)

    return result


ops.NotDifferentiable("ExpandSplitWords")


def expand_split_chars(source, default_value=''):
    """Split unicode strings into characters.
    Result tokens could be simply joined with empty separator to obtain original strings.

    Args:
        source: `Tensor` of any shape, strings to split
        default_value: Scalar value for padding.  Defaults to empty string.
    Returns:
        `Tensor` with an additional dimension of size 1 added.
    """

    source = tf.convert_to_tensor(source, dtype=tf.string)
    result = _lib.expand_split_chars(source, default_value)

    return result


ops.NotDifferentiable("ExpandSplitChars")
