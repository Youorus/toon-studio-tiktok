import unittest

from toonstudio.episode import action_track, sample_action


class ActionTrackTest(unittest.TestCase):
    def test_independent_transform_interpolates_then_holds(self):
        track = action_track([
            {'t': 0, 'dx': 120},
            {'t': 1, 'dx': 0, 'angle': 8, 'courbe': 'lineaire'},
            {'t': 2, 'angle': 0, 'courbe': 'maintien'},
        ], 'plan/acteur')
        self.assertEqual(sample_action(track, 0.5), {
            'dx': 60, 'dy': 0, 'angle': 4, 'echelle': 1,
        })
        self.assertEqual(sample_action(track, 1.9)['angle'], 8)
        self.assertEqual(sample_action(track, 2)['angle'], 0)
        self.assertEqual(sample_action(track, 3)['dx'], 0)

    def test_omitted_fields_carry_forward(self):
        track = action_track([
            {'t': 0.5, 'dy': 30, 'echelle': 0.8},
            {'t': 1, 'dy': 0},
        ], 'plan/acteur')
        self.assertEqual(sample_action(track, 0)['echelle'], 1)
        self.assertAlmostEqual(sample_action(track, 1)['echelle'], 0.8)
        self.assertEqual(sample_action(track, 1)['dy'], 0)

    def test_rejects_bad_inputs(self):
        for keys in (
            [{'t': -1}],
            [{'t': 0}, {'t': 0}],
            [{'t': 0, 'echelle': 0}],
            [{'t': 0, 'angle': float('inf')}],
            [{'t': 0, 'courbe': 'inconnue'}],
        ):
            with self.subTest(keys=keys), self.assertRaisesRegex(ValueError, 'plan/acteur'):
                action_track(keys, 'plan/acteur')


if __name__ == '__main__':
    unittest.main()
