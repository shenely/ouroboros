#built-in libraries
import unittest

#external libraries
import numpy.testing

#internal libraries
import ouroboros.ext.unikep as libunikep

#constants
MINUTE = 60.0#seconds

class TestUnikep(unittest.TestCase):\

    def test_unikep(self):
        """Taken from Example 3.7 in

        Curtis, Howard D. (2005). Orbital Mechanics for Engineering
            Students. Burlington, MA: Elsevier Ltd.
        """
        mu = 398600.0
        r0_bar = numpy.array([7000.0, -12124.0, 0.0])
        v0_bar = numpy.array([2.6679, 4.6210, 0.0])
        t = 60 * MINUTE

        libunikep.setmu(mu)
        (r_bar, v_bar) = libunikep.unikep(r0_bar, v0_bar, t)
        
        (numpy.testing.assert_allclose
         (r_bar, numpy.array([-3296.8, 7413.9, 0.0]), rtol=1e-3))
        (numpy.testing.assert_allclose
         (v_bar, numpy.array([-8.2977, -0.96309, 0.0]), rtol=1e-3))

if __name__ == '__main__':
    unittest.main()
