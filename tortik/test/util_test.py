import unittest
from tortik.util import Item

test_dict = {
    'key1': 'value1',
    'key2': 'value2',
    'key3': ['value3_1', 'value3_2'],
    'key4': {'key4_1': 'value4_1'},
    'key5': {'key5_1': 'value5_1',
             'key5_2': 'value5_2'},
    'key6': [
        {'key6_1_1': 'value6_1_1',
         'key6_1_2': 'value6_1_2'},
        {'key6_2_1': 'value6_2_1'}
    ],
    'key7': [
        [{'key7_1_1_1': 'value7_1_1_1',
          'key7_1_1_2': 'value7_1_1_2'},
         {'key7_1_2_1': 'value7_1_2_1'}],
        [{'key7_2_1_1': 'value7_2_1_1'}]
    ],
    'key8': {'key8_1': ['value8_1_1', 'value8_1_2']},
    'key9': {'key9_1': {'key9_1_1': 'value9_1_1'}}
}

test_obj = Item(test_dict)

class ItemTests(unittest.TestCase):

    def testBasic(self):
        self.assertEqual(test_dict['key1'], test_obj.key1)
        self.assertEqual(test_dict['key2'], test_obj.key2)
        self.assertEqual(test_obj.key0, None)

    def testInnerDict(self):
        self.assertEqual(test_dict['key4']['key4_1'], test_obj.key4.key4_1)
        self.assertEqual(test_dict['key5']['key5_1'], test_obj.key5.key5_1)
        self.assertEqual(test_dict['key5']['key5_2'], test_obj.key5.key5_2)
        self.assertEqual(test_dict['key9']['key9_1']['key9_1_1'], test_obj.key9.key9_1.key9_1_1)

    def testInnerList(self):
        self.assertEqual(test_dict['key3'][0], test_obj.key3[0])
        self.assertEqual(test_dict['key6'][0]['key6_1_1'], test_obj.key6[0].key6_1_1)
        self.assertEqual(test_dict['key6'][0]['key6_1_2'], test_obj.key6[0].key6_1_2)
        self.assertEqual(test_dict['key6'][1]['key6_2_1'], test_obj.key6[1].key6_2_1)
        self.assertEqual(test_dict['key7'][0][0]['key7_1_1_1'], test_obj.key7[0][0].key7_1_1_1)
        self.assertEqual(test_dict['key7'][0][0]['key7_1_1_2'], test_obj.key7[0][0].key7_1_1_2)
        self.assertEqual(test_dict['key7'][0][1]['key7_1_2_1'], test_obj.key7[0][1].key7_1_2_1)
        self.assertEqual(test_dict['key7'][1][0]['key7_2_1_1'], test_obj.key7[1][0].key7_2_1_1)
        self.assertEqual(test_dict['key8']['key8_1'][0], test_obj.key8.key8_1[0])
        self.assertEqual(test_dict['key8']['key8_1'][1], test_obj.key8.key8_1[1])
