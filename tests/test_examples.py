"""Numerical contracts and scientific counterexamples for the teaching models."""
import contextlib, io, json, runpy, unittest
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
LESSONS=json.loads((ROOT/'src/course.json').read_text())['lessons']
def run(index, replacements=()):
    code=(ROOT/'python'/LESSONS[index]['code']).read_text()
    for old,new in replacements:
        assert old in code
        code=code.replace(old,new)
    ns={}
    with contextlib.redirect_stdout(io.StringIO()):exec(compile(code,LESSONS[index]['code'],'exec'),ns)
    plt.close('all')
    return ns
class Examples(unittest.TestCase):
    def test_route_and_execution(self):
        self.assertEqual(len(LESSONS),18)
        self.assertEqual(len(set(l['slug'] for l in LESSONS)),18)
        for i,l in enumerate(LESSONS):
            with self.subTest(lesson=l['slug']):
                self.assertEqual(l['module'],i//3)
                self.assertEqual(len(l['options']),3)
                self.assertIn(l['correct'],range(3))
                self.assertTrue(l['kind'] and l['limit'] and l['change'] and l['feedback'])
                run(i)
    def test_counterfactual_and_confounded_contrast(self):
        self.assertAlmostEqual(run(0)['ate'],3)
        result=run(1)
        self.assertEqual(result['naive'],15)
        np.testing.assert_array_equal(result['y1'],result['y0'])
        changed=run(1,[('np.array([0, 0, 0, 1, 0, 1, 1, 1])','np.array([0, 1, 0, 1, 0, 1, 0, 1])')])
        self.assertEqual(changed['naive'],0)
    def test_collider_and_mediator(self):
        self.assertAlmostEqual(run(4)['selected_correlation'],-.5)
        result=run(5)
        self.assertEqual(result['total'],11)
        self.assertEqual(result['controlled_direct'],3)
    def test_standardisation_and_weights(self):
        self.assertAlmostEqual(run(6)['ate'],3.6)
        self.assertAlmostEqual(run(7)['ipw'],5)
        self.assertAlmostEqual(run(7,[('treatment_effect = 5','treatment_effect = -3')])['ipw'],-3)
        self.assertLess(run(8)['ess'],1.2)
        self.assertAlmostEqual(run(9)['att'],8)
    def test_design_assumption_failures(self):
        self.assertEqual(run(10)['did'],4)
        self.assertEqual(run(10,[('group_specific_trend = 0','group_specific_trend = 3')])['did'],7)
        self.assertAlmostEqual(run(12)['wald'],6)
        self.assertAlmostEqual(run(12,[('direct_invitation_effect = 0','direct_invitation_effect = 1')])['wald'],9)
    def test_uncertainty_does_not_cover_confounding(self):
        result=run(13)
        self.assertGreater(np.quantile(result['boot'],.025),10)
        self.assertLess(np.ptp(np.quantile(result['boot'],[.025,.975])),3)
    def test_selection_transport_and_capstone(self):
        result=run(15)
        self.assertEqual(result['full_effect'],5)
        self.assertEqual(result['complete_case'],15)
        result=run(16)
        self.assertAlmostEqual(result['destination_mix']@result['group_effects'],3.2)
        result=run(17)
        self.assertEqual(result['raw'],23)
        self.assertEqual(result['adjusted'],5)
if __name__=='__main__':unittest.main()
