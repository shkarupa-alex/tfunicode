# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tfunicode.python.ops import expand_split_words
from tensorflow.python.framework import test_util
import os
import tensorflow as tf


@test_util.run_all_in_graph_and_eager_modes
class ExpandSplitWordsTest(tf.test.TestCase):
    def testInferenceShape(self):
        source = [
            ['1', '2', '3'],
            ['4', '5', '6'],
        ]
        result = expand_split_words(source)

        if tf.executing_eagerly():
            self.assertEqual([6, 3], result.indices.shape.as_list())
            self.assertEqual([6], result.values.shape.as_list())
            self.assertEqual([3], result.dense_shape.shape.as_list())
        else:
            self.assertEqual([None, 3], result.indices.shape.as_list())
            self.assertEqual([None], result.values.shape.as_list())
            self.assertEqual([3], result.dense_shape.shape.as_list())

    def testActualShape(self):
        source = [
            ['1', '2', '3'],
            ['4', '5', '6'],
        ]
        result = expand_split_words(source)

        result = self.evaluate(result)
        self.assertAllEqual([2, 3, 1], result.dense_shape)

    def testEmpty(self):
        expected = tf.convert_to_tensor([''], dtype=tf.string)
        result = expand_split_words('')
        result = tf.sparse.to_dense(result, default_value='')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def test0D(self):
        expected = tf.convert_to_tensor(['x', '!'], dtype=tf.string)
        result = expand_split_words('x!')
        result = tf.sparse.to_dense(result, default_value='')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def test1D(self):
        expected = tf.convert_to_tensor([['x', '!']], dtype=tf.string)
        result = expand_split_words(['x!'])
        result = tf.sparse.to_dense(result, default_value='')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def test2D(self):
        expected = tf.convert_to_tensor([[['x', '!']]], dtype=tf.string)
        result = expand_split_words([['x!']])
        result = tf.sparse.to_dense(result, default_value='')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def testSparse(self):
        source = tf.string_split(['ab|c d|e', 'f|'], delimiter='|')
        result = expand_split_words(source)
        result = tf.sparse.to_dense(result, default_value='')
        expected = tf.convert_to_tensor([
            [
                ['ab', '', ''],
                ['c', ' ', 'd'],
                ['e', '', '']
            ],
            [
                ['f', '', ''],
                ['', '', ''],
                ['', '', ''],
            ]
        ], dtype=tf.string)

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected.tolist(), result.tolist())

    def testRestore(self):
        source = u'Hey\n\tthere\t«word», !!!'
        expected = tf.convert_to_tensor(source, dtype=tf.string)
        result = expand_split_words(source)
        result = tf.sparse.to_dense(result, default_value='')
        result = tf.strings.reduce_join(result)

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def testWrapped(self):
        expected = [
            [' ', '"', 'word', '"', ' '],
            [' ', u'«', 'word', u'»', ' '],
            [' ', u'„', 'word', u'“', ' '],
            [' ', '{', 'word', '}', ' '],
            [' ', '(', 'word', ')', ' '],
            [' ', '[', 'word', ']', ' '],
            [' ', '<', 'word', '>', ' '],
        ]
        expected = tf.convert_to_tensor(expected, dtype=tf.string)
        result = expand_split_words([
            ' "word" ',
            u' «word» ',
            u' „word“ ',
            ' {word} ',
            ' (word) ',
            ' [word] ',
            ' <word> ',
        ])
        result = tf.sparse.to_dense(result, default_value='')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def testWordPunkt(self):
        expected = [
            [' ', 'word', '.', ' ', '', ''],
            [' ', 'word', '.', '.', ' ', ''],
            [' ', 'word', '.', '.', '.', ' '],
            [' ', 'word', u'…', ' ', '', ''],
            [' ', 'word', ',', ' ', '', ''],
            [' ', 'word', '.', ',', ' ', ''],
            [' ', 'word', ':', ' ', '', ''],
            [' ', 'word', ';', ' ', '', ''],
            [' ', 'word', '!', ' ', '', ''],
            [' ', 'word', '?', ' ', '', ''],
            [' ', 'word', '%', ' ', '', ''],
            [' ', '$', 'word', ' ', '', ''],
        ]
        expected = tf.convert_to_tensor(expected, dtype=tf.string)
        result = expand_split_words([
            ' word. ',
            ' word.. ',
            ' word... ',
            u' word… ',
            ' word, ',
            ' word., ',
            ' word: ',
            ' word; ',
            ' word! ',
            ' word? ',
            ' word% ',
            ' $word ',
        ])
        result = tf.sparse.to_dense(result, default_value='')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def testComplexWord(self):
        expected = [
            [' ', 'test', '@', 'test.com', ' ', '', '', '', ''],
            [' ', 'www.test.com', ' ', '', '', '', '', '', ''],
            [' ', 'word', '.', '.', 'word', ' ', '', '', ''],
            [' ', 'word', '+', 'word', '-', 'word', ' ', '', ''],
            [' ', 'word', '\\', 'word', '/', 'word', '#', 'word', ' '],
        ]
        expected = tf.convert_to_tensor(expected, dtype=tf.string)
        result = expand_split_words([
            ' test@test.com ',
            ' www.test.com ',
            ' word..word ',
            ' word+word-word ',
            ' word\\word/word#word ',
        ])
        result = tf.sparse.to_dense(result, default_value='')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)

    def testIcuWordBreak(self):
        # WORD_BREAK_TEST_URL = 'https://www.unicode.org/Public/UCD/latest/ucd/auxiliary/WordBreakTest.txt'
        # test_data = urlopen(WORD_BREAK_TEST_URL).read().decode('utf-8').strip().split('\n')

        test_file = os.path.join(os.path.dirname(__file__), 'WordBreakTest.txt')
        with open(test_file, 'rb') as ft:
            test_data = ft.read().decode('utf-8').strip().split('\n')

        expected, source, description = [], [], []
        for row, line in enumerate(test_data):
            if line.startswith('#'):
                continue

            example, rule = line.split('#')
            example = example.strip().strip(u'÷').strip().replace(u'÷', '00F7').replace(u'×', '00D7').split(' ')
            example = [code.zfill(8) if len(code) > 4 else code.zfill(4) for code in example]
            example = [u'\\U{}'.format(code) if len(code) > 4 else u'\\u{}'.format(code) for code in example]
            example = [code.decode('unicode-escape') for code in example]
            example = u''.join(example).replace(u'×', '')

            expected.append(example.split(u'÷'))
            source.append(example.replace(u'÷', ''))

            rule = rule.strip().strip(u'÷').strip()
            description.append(u'Row #{}. {}'.format(row + 1, rule))

        max_len = len(sorted(expected, key=len, reverse=True)[0])
        expected = [e + [''] * (max_len - len(e)) for e in expected]

        expected_tensor = tf.convert_to_tensor(expected, dtype=tf.string)
        result_tensor = tf.sparse.to_dense(expand_split_words(source), default_value='')

        expected_value, result_value = self.evaluate(expected_tensor), self.evaluate(result_tensor)

        for exp, res, desc in zip(expected_value, result_value, description):
            self.assertAllEqual(exp, res, desc)

    def testSplitExtended(self):
        expected = tf.convert_to_tensor([
            [' ', 'word', '.', 'word', ' '],
            [' ', 'word', u'․', 'word', ' '],
            [' ', 'word', u'﹒', 'word', ' '],
            [' ', 'word', u'．', 'word', ' '],
        ], dtype=tf.string)
        result = expand_split_words([
            # \u002E
            ' word.word ',

            # \u2024
            u' word․word ',

            # \uFE52
            u' word﹒word ',

            # \uFF0E
            u' word．word ',
        ], True)
        result = tf.sparse.to_dense(result, default_value='')

        expected, result = self.evaluate(expected), self.evaluate(result)
        self.assertAllEqual(expected, result)


if __name__ == "__main__":
    tf.test.main()
