# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tfunicode.python.ops import transform_normalize_unicode
from tensorflow.python.framework import test_util
import tensorflow as tf


@test_util.run_all_in_graph_and_eager_modes
class TransformNormalizeUnicodeTest(tf.test.TestCase):
    def testInferenceShape(self):
        source = [
            ['1', '2', '3'],
            ['4', '5', '6'],
        ]
        result = transform_normalize_unicode(source, 'NFD')

        self.assertEqual([2, 3], result.shape.as_list())

    def testActualShape(self):
        source = [
            ['1', '2', '3'],
            ['4', '5', '6'],
        ]
        result = transform_normalize_unicode(source, 'NFD')
        result = tf.shape(result)

        result = self.evaluate(result)
        self.assertEqual([2, 3], result.tolist())

    def testEmpty(self):
        result = transform_normalize_unicode('', 'NFD')

        result = self.evaluate(result)
        self.assertAllEqual(b'', result)

    def test0D(self):
        result = transform_normalize_unicode('', 'NFD')

        result = self.evaluate(result)
        self.assertAllEqual(b'', result)

    def test1D(self):
        result = transform_normalize_unicode([''], 'NFD')

        result = self.evaluate(result)
        self.assertAllEqual([b''], result)

    def test2D(self):
        result = transform_normalize_unicode([['']], 'NFD')

        result = self.evaluate(result)
        self.assertAllEqual([[b'']], result)

    def testSparse(self):
        expected = tf.SparseTensor(indices=[[0, 0]], values=[u'\u0041\u030A'], dense_shape=[1, 1])
        source = tf.SparseTensor(indices=[[0, 0]], values=[u'\u00C5'], dense_shape=[1, 1])
        result = transform_normalize_unicode(source, 'NFD')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected.indices.tolist(), result.indices.tolist())
        self.assertAllEqual(expected.values.tolist(), result.values.tolist())
        self.assertAllEqual(expected.dense_shape.tolist(), result.dense_shape.tolist())

    def testNFD(self):
        expected = tf.convert_to_tensor(u'\u0041\u030A', dtype=tf.string)
        result = transform_normalize_unicode(u'\u00C5', 'NFD')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def testNFC(self):
        expected = tf.convert_to_tensor(u'\u00C5', dtype=tf.string)
        result = transform_normalize_unicode(u'\u0041\u030A', 'NFC')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def testNFKD(self):
        expected = tf.convert_to_tensor(u'\u0031', dtype=tf.string)
        result = transform_normalize_unicode(u'\u2460', 'NFKD')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def testNFKC(self):
        expected = tf.convert_to_tensor(u'\u1E69', dtype=tf.string)
        result = transform_normalize_unicode(u'\u1E9B\u0323', 'NFKC')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def testWrongAlg(self):
        if tf.executing_eagerly():
            with self.assertRaisesRegexp(tf.errors.InvalidArgumentError, 'is not in the list of allowed values'):
                self.evaluate(transform_normalize_unicode(u'', 'ABCD'))
        else:
            with self.assertRaisesRegexp(ValueError, 'string \'ABCD\' not in'):
                self.evaluate(transform_normalize_unicode(u'', 'ABCD'))


if __name__ == "__main__":
    tf.test.main()
