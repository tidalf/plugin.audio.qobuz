from .base import BaseBootstrap

class ShellBootstrap(BaseBootstrap):
    '''Set some boot properties
    and route query based on parameters
    '''

    def __init__(self, application):
        super(ShellBootstrap, self).__init__(application)

    def init_app(self):
        '''General bootstrap'''
        super(ShellBootstrap, self).init_app()
        self.bootstrap_registry()
        self.bootstrap_sys_args()