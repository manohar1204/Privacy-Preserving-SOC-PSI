import hashlib,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from psi import private_intersection,baseline
H=lambda s:hashlib.sha256(s.encode()).hexdigest()
class TestPSI(unittest.TestCase):
 def test_partial(self):
  x=[H('a'),H('b'),H('c')];y=[H('b'),H('d')]
  for tb in (16,32):self.assertEqual(private_intersection(x,y,tb)[0],baseline(x,y))
 def test_none(self):self.assertEqual(private_intersection([H('a')],[H('b')])[0],[])
 def test_full(self):
  x=[H('a'),H('b')];self.assertEqual(private_intersection(x,x)[0],baseline(x,x))
 def test_duplicates_case(self):
  x=[H('a'),H('a').upper()];self.assertEqual(private_intersection(x,x)[0],[H('a')])
 def test_malformed(self):
  with self.assertRaises(ValueError):private_intersection(['abc'],[])
 def test_empty(self):self.assertEqual(private_intersection([],[])[0],[])
 def test_randomized(self):
  x=[H(str(i)) for i in range(25)];y=[H(str(i)) for i in range(10,35)]
  for _ in range(3):self.assertEqual(private_intersection(x,y)[0],baseline(x,y))
if __name__=='__main__':unittest.main()
