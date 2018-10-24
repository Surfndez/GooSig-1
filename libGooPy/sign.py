#!/usr/bin/python
#
# (C) 2018 Riad S. Wahby <rsw@cs.stanford.edu>

import sys

import libGooPy.group_ops as lgops
from libGooPy.consts import Grsa2048
from libGooPy.defs import Defs
import libGooPy.primes as lprimes
import libGooPy.prng as lprng
import libGooPy.util as lutil

# python 2/3 hack
if sys.version_info[0] == 2:
    range = xrange      # pylint: disable=redefined-builtin,undefined-variable

class GooSigSigner(object):
    def __init__(self, p, q, gops=None):
        self.p = p
        self.q = q
        self.n = self.p * self.q

        # encryption and decryption with Signer's key
        self.lam = (p - 1) * (q - 1) // lutil.gcd(p - 1, q - 1)
        for e in lprimes.primes_skip(1):
            if e > 1000:
                raise RuntimeError("cannot find suitable secret key")
            d = lutil.invert_modp(e, self.lam)
            if d is not None:
                self.e = e
                self.d = d
                break
        assert (self.d * self.e) % self.lam == 1

        if gops is None:
            modbits = lutil.clog2(p) + lutil.clog2(q)
            gops = lgops.RSAGroupOps(Grsa2048, modbits)
        self.gops = gops

        assert lprimes.is_prime(p)
        assert lprimes.is_prime(q)

    def encrypt(self, m):
        # NOTE this is not real RSA encryption! You should use RSA-OAEP or the like.
        return pow(m, self.e, self.n)

    def decrypt(self, c):
        # NOTE this is not real RSA decryption! You should use RSA-OAEP or the like.
        return pow(c, self.d, self.n)

    def sign(self, C1, s, msg):
        # NOTE one assumes that s will have been encrypted to our public key.
        #      This function expects that s has already been decrypted.
        assert C1 == self.gops.reduce(self.gops.powgh(self.n, s)), "C1 does not appear to commit to our RSA modulus with opening s"

        ###
        ### Preliminaries: compute values P needs to run the ZKPOK
        ###
        # find t
        t = None
        for t in Defs.primes:
            w = lutil.sqrt_modn(t, self.p, self.q)
            if w is not None:
                break
        if w is None or t is None:
            RuntimeError("did not find a prime quadratic residue less than 1000 mod N!")

        a = (w**2 - t) // self.n
        assert a * self.n == w**2 - t, "w^2 - t was not divisible by N!"

        # commitment to w
        s1 = self.gops.rand_scalar()
        C2 = self.gops.reduce(self.gops.powgh(w, s1))

        # inverses of C1 and C2
        (C1Inv, C2Inv) = self.gops.inv2(C1, C2)

        ###
        ### P's first message: commit to randomness
        ###
        # P's randomness
        (r_w, r_w2, r_s1, r_a, r_an, r_s1w, r_sa) = ( self.gops.rand_scalar() for _ in range(0, 7) )

        # P's first message
        A = self.gops.reduce(self.gops.powgh(r_w, r_s1))
        B = self.gops.reduce(self.gops.mul(self.gops.pow(C2Inv, C2, r_w), self.gops.powgh(r_w2, r_s1w)))
        C = self.gops.reduce(self.gops.mul(self.gops.pow(C1Inv, C1, r_a), self.gops.powgh(r_an, r_sa)))
        D = r_w2 - r_an

        ###
        ### V's message: random challenge and random prime
        ###
        (chal, ell) = lprng.fs_chal(self.gops.desc, C1, C2, t, A, B, C, D, msg)

        ###
        ### P's second message: compute quotient message
        ###
        # compute z' = c*(w, w2, s1, a, an, s1w, sa) + (r_w, r_w2, r_s1, r_a, r_an, r_s1w, r_sa)
        z_w = chal * w + r_w
        z_w2 = chal * w * w + r_w2
        z_s1 = chal * s1 + r_s1
        z_a = chal * a + r_a
        z_an = chal * a * self.n + r_an
        z_s1w = chal * s1 * w + r_s1w
        z_sa = chal * s * a + r_sa

        # compute quotient commitments
        Aq = self.gops.reduce(self.gops.powgh(z_w // ell, z_s1 // ell))
        Bq = self.gops.reduce(self.gops.mul(self.gops.pow(C2Inv, C2, z_w // ell), self.gops.powgh(z_w2 // ell, z_s1w // ell)))
        Cq = self.gops.reduce(self.gops.mul(self.gops.pow(C1Inv, C2, z_a // ell), self.gops.powgh(z_an // ell, z_sa // ell)))
        Dq = (z_w2 - z_an) // ell

        # compute z'
        z_prime = tuple( z_foo % ell for z_foo in (z_w, z_w2, z_s1, z_a, z_an, z_s1w, z_sa) )

        ###
        ### signature: (chal, ell, Aq, Bq, Cq, Dq, z_prime)
        ###
        sigma = (chal, ell, Aq, Bq, Cq, Dq, z_prime)
        return (C2, t, sigma)

    def sign_simple(self, C1, C2, msg):
        ###
        ### Preliminaries
        ###
        # decrypt C2 to get s
        s = self.decrypt(C2)
        assert C1 == self.gops.reduce(self.gops.powgh(self.n, s)), "C1 does not appear to commit to our RSA modulus with opening s"

        ###
        ### P's first message: commit to randomness
        ###
        # P's randomness
        (r_n, r_s) = ( self.gops.rand_scalar() for _ in range(0, 2) )

        # P's first message
        A = self.gops.reduce(self.gops.powgh(r_n, r_s))

        ###
        ### V's message: random challenge and random prime
        ###
        (chal, ell) = lprng.fs_chal(self.gops.desc, C1, C2, A, msg)

        ###
        ### P's second message: compute quotient message
        ###
        # compute z' = c*(n, s) + (r_n, r_s)
        z_n = chal * self.n + r_n
        z_s = chal * s + r_s

        # compute quotient commitments
        Aq = self.gops.reduce(self.gops.powgh(z_n // ell, z_s // ell))

        # compute z'
        z_prime = tuple( z_foo % ell for z_foo in (z_n, z_s) )

        ###
        ### signature: (chal, ell, Aq, z_prime)
        ###
        return (chal, ell, Aq, z_prime)
