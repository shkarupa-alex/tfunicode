# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from tfucops import transform_normalize_unicode


class NormalizeUnicodeTest(tf.test.TestCase):
    def test0D(self):
        with self.test_session():
            result = transform_normalize_unicode('', 'NFD').eval()
            self.assertAllEqual(b'', result)

    def test1D(self):
        with self.test_session():
            result = transform_normalize_unicode([''], 'NFD').eval()
            self.assertAllEqual([b''], result)

    def test2D(self):
        with self.test_session():
            result = transform_normalize_unicode([['']], 'NFD').eval()
            self.assertAllEqual([[b'']], result)

    def testNFD(self):
        expected = u'\u0041\u030A'.encode('utf-8')

        with self.test_session():
            result = transform_normalize_unicode(u'\u00C5', 'NFD').eval()
            self.assertAllEqual(expected, result)

    def testNFC(self):
        expected = u'\u00C5'.encode('utf-8')

        with self.test_session():
            result = transform_normalize_unicode(u'\u0041\u030A', 'NFC').eval()
            self.assertAllEqual(expected, result)

    def testNFKD(self):
        expected = u'\u0031'.encode('utf-8')

        with self.test_session():
            result = transform_normalize_unicode(u'\u2460', 'NFKD').eval()
            self.assertAllEqual(expected, result)

    def testNFKC(self):
        expected = u'\u00E7'.encode('utf-8')

        with self.test_session():
            result = transform_normalize_unicode(u'\u00E7', 'NFKC').eval()
            self.assertAllEqual(expected, result)

    def testWrongAlg(self):
        with self.test_session():
            with self.assertRaisesOpError('unknown normalization form'):
                transform_normalize_unicode(u'', 'ABCD').eval()


if __name__ == "__main__":
    tf.test.main()