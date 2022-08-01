#!/usr/bin/python3

KB = 2**10
MB = 2**20
GB = 2**30
TB = 2**40

class CP(object):
    def __init__(self, sidecars=0, requests=0):
        self.services = []
        self.sidecars = sidecars
        self.requests = requests
        self.estimate()
    def append(self, service):
        self.services.append(service)
    def estimate(self, hr=KB):
        if self.sidecars == 0:
            self.sidecars = sum(list(map(lambda x: x.sidecars(), self.services)))
        self.istiod=dict(vcpu=float('%02.f' % (0.001 * len(self.services))), 
                         memory=float('%0.2f' % ((805306 * self.sidecars) / hr) ))
        self.envoy=dict(vcpu=float('%0.2f' % (0.00035 * self.requests)), 
                        memory=float('%0.2f' % ((41943 * self.requests) / hr)) )
        self.telemetry=dict(vcpu=float('%0.2f' % (0.0006 * self.requests)))
        self._services=dict(vcpu=float('%0.2f' % sum(list(map(lambda x: x.vcpu, self.services)))),
                            memory=float('%0.2f' % (sum(list(map(lambda x: x.memory, self.services)) * len(self.services)) /hr )),
                            request_vcpu=float('%0.2f' % sum(list(map(lambda x: x.rcpu, self.services)))),
                            request_memory=float('%0.2f' % (sum(list(map(lambda x: x.rmem, self.services)) * len(self.services)) / hr )))
    def to_dict(self):
        return dict(istiod=self.istiod,
                    envoy=self.envoy,
                    telemetry=self.telemetry,
                    services=self._services)

class DP(object):
    def __init__(self, requests=0):
        self.requests = requests
        self.estimate()
    def estimate(self):
        self.vcpu = 0.0005 * (self.requests / 1000)
        self.memory = 41943040
    def to_dict(self):
        return dict(vcpu=self.vcpu, memory=self.memory)

class NS(object):
    def __init__(self, services=1):
        self.services = services
    def __len__(self):
        return len(self.services)

class Service(object):
    def __init__(self, size=1, vcpu=0, memory=0, overhead=None):
        self.pods = []
        for p in range(0, size):
            self.pods.append(Pod(vcpu,memory))
        self.estimate(overhead) 
        self.rcpu = sum(list(map(lambda x: x.vcpu, self.pods)))
        self.rmem = sum(list(map(lambda x: x.memory, self.pods)))
    def __len__(self):
        return len(self.pods)
    def sidecars(self):
        return len(self.pods) + 1
    def estimate(self, dataplane):
        self.vcpu = sum(list(map(lambda x: dataplane.vcpu + x.vcpu, self.pods)))
        self.memory = sum(list(map(lambda x: x.memory, self.pods)))
    def to_dict(self):
        return dict(vcpu=self.vcpu, memory=self.memory, request_vcpu=self.rcpu, request_memory=self.rmem)

class Pod(object):
    def __init__(self, vcpu=0, memory=0):
        self.vcpu = vcpu
        self.memory = memory

                    
