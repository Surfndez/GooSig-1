#!/usr/bin/python
#
# (C) 2018 Riad S. Wahby <rsw@cs.stanford.edu>

import hashlib

class Defs(object):
    winsize = 6     # for RSA operations
    combsize = 16   # for RSA operations
    hashfn = hashlib.sha512
    chalbits = 128

    primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109
             ,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,229,233
             ,239,241,251,257,263,269,271,277,281,283,293,307,311,313,317,331,337,347,349,353,359,367
             ,373,379,383,389,397,401,409,419,421,431,433,439,443,449,457,461,463,467,479,487,491,499
             ,503,509,521,523,541,547,557,563,569,571,577,587,593,599,601,607,613,617,619,631,641,643
             ,647,653,659,661,673,677,683,691,701,709,719,727,733,739,743,751,757,761,769,773,787,797
             ,809,811,821,823,827,829,839,853,857,859,863,877,881,883,887,907,911,919,929,937,941,947
             ,953,967,971,977,983,991,997]


    class Grsa(object):
        # RSA 2048 challenge
        modulus = 25195908475657893494027183240048398571429282126204032027777137836043662020707595556264018525880784406918290641249515082189298559149176184502808489120072844992687392807287776735971418347270261896375014971824691165077613379859095700097330459748808428401797429100642458691817195118746121515172654632282216869987549182422433637259085141865462043576798423387184774447920739934236584823824281198163815010674810451660377306056201619676256133844143603833904414952634432190114657544454178424020924616515723350778707749817125772467962926386356373289912154831438167899885040445364023527381951378636564391212010397122822120720357
        g = 2
        h = 3