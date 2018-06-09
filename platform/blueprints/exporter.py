from troposphere import Export, Sub, Output


class Exporter(object):
    def __init__(self):
        pass

    def create_exports(self):
        t = self.template
        variables = self.get_variables()
        for k, v in variables['exports'].iteritems():
            v = v.replace('$\{', '${')
            t.add_output(Output(k, Value=Sub(v), Export=Export(k)))
