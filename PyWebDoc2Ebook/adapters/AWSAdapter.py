from Abstract import Adapter

class AWSAdapter(Adapter):
    
    def regex(self):
        return r'^https://docs.aws.amazon.com/.*'
    
    def toc(self):
        pass
    
    
    
