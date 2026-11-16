"""Educational semi-honest Ristretto255 OPRF PSI using system libsodium.
Not a reviewed PSI implementation or suitable for deployment.
"""
import ctypes, ctypes.util, hashlib, secrets, re, time

libpath=ctypes.util.find_library('sodium')
if not libpath: raise RuntimeError('libsodium required: sudo apt-get install libsodium23')
S=ctypes.CDLL(libpath)
S.sodium_init.restype=ctypes.c_int
assert S.sodium_init()>=0
U=ctypes.c_ubyte
A32=U*32; A64=U*64
for name,argc in [('crypto_core_ristretto255_from_hash',2),('crypto_core_ristretto255_scalar_reduce',2),('crypto_core_ristretto255_scalar_invert',2),('crypto_scalarmult_ristretto255',3),('crypto_scalarmult_ristretto255_base',2)]:
 f=getattr(S,name);f.argtypes=[ctypes.c_void_p]*argc;f.restype=ctypes.c_int

def op(name,*vals,outlen=32):
 out=(U*outlen)(); args=[out]+[(U*len(v)).from_buffer_copy(v) for v in vals]
 rc=getattr(S,name)(*args)
 if rc!=0:raise ValueError(f'{name} rejected input')
 return bytes(out)

def scalar():
 while True:
  s=op('crypto_core_ristretto255_scalar_reduce',secrets.token_bytes(64))
  if any(s):return s

def group(x):return op('crypto_core_ristretto255_from_hash',hashlib.sha512(b'CYB599-SOC-PSI-v1/group'+x).digest())
def mul(k,p):return op('crypto_scalarmult_ristretto255',k,p)
def token(p,n):return hashlib.sha256(b'CYB599-SOC-PSI-v1/token'+p).digest()[:n]
def validate(items):
 out=set()
 for x in items:
  if not isinstance(x,str) or re.fullmatch('[0-9a-fA-F]{64}',x) is None:raise ValueError('expected 64-character SHA-256 hex digest')
  out.add(bytes.fromhex(x))
 return sorted(out)

def private_intersection(soc,provider,token_bytes=32):
 if token_bytes not in (16,32):raise ValueError('token_bytes must be 16 or 32')
 X=validate(soc);Y=validate(provider); k=scalar(); t0=time.perf_counter()
 blinded=[];inverses=[]
 for x in X:
  r=scalar();blinded.append(mul(r,group(x)));inverses.append(op('crypto_core_ristretto255_scalar_invert',r))
 evaluated=[mul(k,b) for b in blinded]
 provider_tokens=[token(mul(k,group(y)),token_bytes) for y in Y]
 # Shuffle provider messages so their order is not meaningful.
 secrets.SystemRandom().shuffle(provider_tokens)
 known=set(provider_tokens)
 matches=[x.hex() for x,e,inv in zip(X,evaluated,inverses) if token(mul(inv,e),token_bytes) in known]
 elapsed=time.perf_counter()-t0
 return matches,{'seconds':elapsed,'soc_to_provider_bytes':32*len(X),'provider_to_soc_bytes':32*len(X)+token_bytes*len(Y),'blinded_element_bytes':32,'evaluated_element_bytes':32,'token_bytes':token_bytes,'proof_bytes':0,'soc_count':len(X),'provider_count':len(Y)}

def baseline(soc,provider):return sorted(set(x.lower() for x in soc)&set(y.lower() for y in provider))
