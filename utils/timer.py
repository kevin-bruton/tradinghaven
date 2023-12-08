from threading import Timer  
 
def set_timeout(fn, secs, *args, **kwargs): 
  t = Timer(float(secs), fn, args=args, kwargs=kwargs) 
  t.start() 
  return t 