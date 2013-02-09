class NullYesNo(object):
    def ask(self, question):
        print "Asking question %s" % question
        return True

class ProxyYesNo(object):

    def __init__(self, proxy):
        self.real = None

    def ask(question):
        return self.real.ask(question)

yesno = ProxyYesNo(NullYesNo())