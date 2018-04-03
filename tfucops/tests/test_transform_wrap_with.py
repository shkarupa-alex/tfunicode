# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from .. import transform_wrap_with


class TransformWrapWithTest(tf.test.TestCase):
    def testInferenceShape(self):
        source = [
            ['1', '2', '3'],
            ['4', '5', '6'],
        ]
        result = transform_wrap_with(source, '<', '>')

        self.assertEqual([2, 3], result.shape.as_list())

    def testActualShape(self):
        source = [
            ['1', '2', '3'],
            ['4', '5', '6'],
        ]
        result = transform_wrap_with(source, '<', '>')
        result = tf.shape(result)

        with self.test_session():
            result = result.eval()
            self.assertEqual([2, 3], result.tolist())

    def testEmpty(self):
        result = transform_wrap_with('', '<', '>')

        with self.test_session():
            result = result.eval()
            self.assertAllEqual(b'<>', result)

    def testEmptyBorders(self):
        result = transform_wrap_with('test', '', '')

        with self.test_session():
            result = result.eval()
            self.assertAllEqual(b'test', result)

    def test0D(self):
        result = transform_wrap_with('X', '<', '>')

        with self.test_session():
            result = result.eval()
            self.assertAllEqual(b'<X>', result)

    def test1D(self):
        result = transform_wrap_with(['X'], '<', '>')

        with self.test_session():
            result = result.eval()
            self.assertAllEqual([b'<X>'], result)

    def test2D(self):
        result = transform_wrap_with([['X']], '<', '>')

        with self.test_session():
            result = result.eval()
            self.assertAllEqual([[b'<X>']], result)

    def testUnicode(self):
        expected = u'надо'
        result = transform_wrap_with(u'ад', u'н', u'о')
        expected = tf.convert_to_tensor(expected, dtype=tf.string)

        with self.test_session():
            expected, result = expected.eval(), result.eval()
            self.assertAllEqual(expected, result)
