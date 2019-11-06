# built-in libraries
# ...

# external libraries
import numpy
import scipy.linalg

# internal libraries
from ouroboros import Image, Node

# exports
__all__ = ("triad",)

# constants
# ...


@Image(".att@triad",
       src=Node(evs=(), args=(),
                ins=(), reqs=("1_bar", "2_bar"),
                outs=(), pros=()),
       trg=Node(evs=(), args=(),
                ins=(), reqs=("1_bar", "2_bar"),
                outs=(), pros=()),
       rot=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=(), pros=("_mat",)))
def triad(src, trg, rot):
    """Triad method"""
    yield
    while True:
        r1_bar, r2_bar = src.reqs
        R1_bar, R2_bar = trg.reqs
        
        r3_bar = numpy.cross(r1_bar, r2_bar)
        R3_bar = numpy.cross(R1_bar, R2_bar)

        s_hat = r1_bar / scipy.linalg.norm(r1_bar)
        S_hat = R1_bar / scipy.linalg.norm(R1_bar)
        m_hat = r3_bar / scipy.linalg.norm(r3_bar)
        M_hat = R3_bar / scipy.linalg.norm(R3_bar)
        s_cross_m = numpy.cross(s_bar, m_bar)
        S_cross_M = numpy.cross(S_bar, M_bar)

        r_mat = numpy.column_stack((s_bar, m_bar, s_cross_m))
        R_mat = numpy.column_stack((S_bar, M_bar, S_cross_M))
        A_mat = numpy.dot(R_mat, numpy.transpose(r_mat))
        
        rot.pros = A_mat,
        yield (rot.outs((True,)),)
    
